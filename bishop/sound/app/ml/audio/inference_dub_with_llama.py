import os
import time
import io
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import soundfile as sf
from xcodec2.modeling_xcodec2 import XCodec2Model

from app.common.db import minio_client
from app.common.logging_service import logger
from app.broker.producer_service import send_update_message_state
from app.broker.Producer import KafkaMessageProducer
from app.common.config import settings

producer = KafkaMessageProducer(
    bootstrap_servers=settings.KAFKA_BROKER_URL,
)


def save_dub_to_s3(dub_url, gen_wav):
    buffer = io.BytesIO()
    sf.write(buffer, gen_wav[0, 0, :].cpu().numpy(), 16000, format='WAV')
    buffer.seek(0)  # Reset buffer position to the beginning

    minio_client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=dub_url,
        data=buffer,
        length=buffer.getbuffer().nbytes,
        content_type='audio/wav'
    )
    return dub_url


def process_inference_task(task_data):
    input_text = task_data["text"]
    msg_id = task_data["message_id"]
    dub_url = task_data["storage_url"]

    logger.info(f"Processing sound inference task with task_data: {task_data}")

    llasa_1b = 'HKUSTAudio/Llasa-1B'

    tokenizer = AutoTokenizer.from_pretrained(llasa_1b)
    model = AutoModelForCausalLM.from_pretrained(llasa_1b)
    model.eval()
    model.to('cuda')

    model_path = "HKUSTAudio/xcodec2"

    Codec_model = XCodec2Model.from_pretrained(model_path)
    Codec_model.eval().cuda()

    def ids_to_speech_tokens(speech_ids):

        speech_tokens_str = []
        for speech_id in speech_ids:
            speech_tokens_str.append(f"<|s_{speech_id}|>")
        return speech_tokens_str

    def extract_speech_ids(speech_tokens_str):

        speech_ids = []
        for token_str in speech_tokens_str:
            if token_str.startswith('<|s_') and token_str.endswith('|>'):
                num_str = token_str[4:-2]

                num = int(num_str)
                speech_ids.append(num)
            else:
                print(f"Unexpected token: {token_str}")
        return speech_ids

    # TTS start!
    with torch.no_grad():

        formatted_text = f"<|TEXT_UNDERSTANDING_START|>{
            input_text}<|TEXT_UNDERSTANDING_END|>"

        # Tokenize the text
        chat = [
            {"role": "user", "content": "Convert the text to speech:" + formatted_text},
            {"role": "assistant", "content": "<|SPEECH_GENERATION_START|>"}
        ]

        input_ids = tokenizer.apply_chat_template(
            chat,
            tokenize=True,
            return_tensors='pt',
            continue_final_message=True
        )
        input_ids = input_ids.to('cuda')
        speech_end_id = tokenizer.convert_tokens_to_ids(
            '<|SPEECH_GENERATION_END|>')

        # Generate the speech autoregressively
        outputs = model.generate(
            input_ids,
            max_length=2048,  # We trained our model with a max length of 2048
            eos_token_id=speech_end_id,
            do_sample=True,
            top_p=1,  # Adjusts the diversity of generated content
            temperature=0.8,  # Controls randomness in output
        )
        # Extract the speech tokens
        generated_ids = outputs[0][input_ids.shape[1]:-1]

        speech_tokens = tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True)

        # Convert  token <|s_23456|> to int 23456
        speech_tokens = extract_speech_ids(speech_tokens)

        speech_tokens = torch.tensor(
            speech_tokens).cuda().unsqueeze(0).unsqueeze(0)

        # Decode the speech tokens to speech waveform
        gen_wav = Codec_model.decode_code(speech_tokens)

    save_dub_to_s3(dub_url, gen_wav)
    send_update_message_state(
        producer=producer,
        message_id=msg_id,
        generated_text=input_text,
        dub_url=dub_url,
    )

    logger.info(f"Dub URL: {dub_url}")
    logger.info(f"Generated text: {input_text}")
