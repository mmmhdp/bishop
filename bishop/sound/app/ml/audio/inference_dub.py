from app.common.logging_service import logger
from app.broker.producer_service import send_update_message_state
from app.broker.Producer import KafkaMessageProducer
from app.common.config import settings

# import os
import time
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch
# import soundfile as sf
# from xcodec2.modeling_xcodec2 import XCodec2Model

producer = KafkaMessageProducer(
    bootstrap_servers=settings.KAFKA_BROKER_URL,
)


def process_inference_task(task_data):
    input_text = task_data["text"]
    msg_id = task_data["message_id"]
    dub_url = "app/sample.wav"

    logger.info(f"Processing sound inference task with task_data: {task_data}")

    send_update_message_state(
        producer=producer,
        message_id=msg_id,
        generated_text=input_text,
        dub_url=dub_url,
    )

    logger.info(f"Dub URL: {dub_url}")
    logger.info(f"Generated text: {input_text}")

    # Uncomment the following lines to run the inference pipeline

    # 1) Load tokenizer & model
    # checkpoint = "Malecc/Borscht-llasa-1b-tts"
    # checkpoint = "HKUSTAudio/Llasa-1B-Multilingual"

    # logger.info(f"\n[1] Loading tokenizer & model from {checkpoint}")
    # tokenizer = AutoTokenizer.from_pretrained(
    #    checkpoint, local_files_only=False)

    # tokenizer_path = 'HKUSTAudio/Llasa-1B-Multilingual'

    # model = AutoModelForCausalLM.from_pretrained(
    #    tokenizer_path, local_files_only=False)
    # model.eval().to("cuda")
    # logger.info(f"    • Tokenizer vocab size: {len(tokenizer)}")
    # logger.info(f"    • pad_token_id: {tokenizer.pad_token_id}")
    # logger.info(f"    • Model class: {model.__class__.__name__}")

    # 2) Load XCodec2 decoder
    # xcodec2_name = "HKUSTAudio/xcodec2"
    # logger.info(f"\n[2] Loading XCodec2 decoder from {xcodec2_name}")
    # codec = XCodec2Model.from_pretrained(xcodec2_name, local_files_only=False)
    # codec.eval().to("cuda")
    # logger.info(f"    • XCodec2 class: {codec.__class__.__name__}")

    # 3) Prepare input text
    # input_text = "Маленькая страна Россия"
    # input_text = 'Auch das unter Schirmherrschaft der Vereinten Nationen ausgehandelte Klimaschutzabkommen von Pariswollen die USA verlassen.'
    # input_text = '言いなりにならなきゃいけないほど後ろめたい事をしたわけでしょ。'

    # logger.info(f"\n[3] Input text: {input_text!r}")
    # formatted = f"<|TEXT_UNDERSTANDING_START|>{
    #    input_text}<|TEXT_UNDERSTANDING_END|>"
    # chat = [
    #    {"role": "user",    "content": "Convert the text to speech:" + formatted},
    #    {"role": "assistant", "content": "<|SPEECH_GENERATION_START|>"}
    # ]
    # logger.info(f"    • Chat template: {chat}")

    # 4) Tokenize
    # t0 = time.time()
    # input_ids = tokenizer.apply_chat_template(
    #    chat,
    #    tokenize=True,
    #    return_tensors="pt",
    #    continue_final_message=True
    # ).to("cuda")
    # t1 = time.time()
    # logger.info(f"\n[4] Tokenized input in {t1-t0:.3f}s")
    # logger.info(f"    • input_ids shape: {tuple(input_ids.shape)}")

    # 5) Build attention mask & get end token
    # pad_id = tokenizer.pad_token_id
    # attention_mask = (input_ids != pad_id).long()
    # logger.info(
    #    f"\n[5] Attention mask built (non-pad tokens: {int(attention_mask.sum())})")
    # speech_end_id = tokenizer.convert_tokens_to_ids(
    #    "<|SPEECH_GENERATION_END|>")
    # logger.info(f"    • SPEECH_GENERATION_END token id: {speech_end_id}")

    # 6) Generate speech tokens
    # gen_kwargs = {
    #    "max_length": 2048,
    #    "eos_token_id": speech_end_id,
    #    "do_sample": True,
    #    "top_p": 1.0,
    #    "temperature": 0.8,
    #    "pad_token_id": pad_id,
    #    "attention_mask": attention_mask,
    # }
    # logger.info(f"\n[6] Running model.generate with args: {gen_kwargs}")
    # t0 = time.time()
    # outputs = model.generate(input_ids, **gen_kwargs)
    # t1 = time.time()
    # logger.info(f"    • Generation time: {t1-t0:.3f}s")
    # logger.info(f"    • Output shape: {tuple(outputs.shape)}")

    # 7) Extract speech token ids
    # gen_ids = outputs[0][input_ids.shape[1]: -1]
    # logger.info(f"\n[7] Extracted {gen_ids.shape[0]} generated token IDs")
    # tok_strs = tokenizer.batch_decode(gen_ids, skip_special_tokens=True)
    # logger.info(f"    • Sample decoded tokens: {tok_strs[:5]}")

    # 8) Convert to integer codes
    # speech_ids = []
    # for tok in tok_strs:
    #    if tok.startswith("<|s_") and tok.endswith("|>"):
    #        speech_ids.append(int(tok[4:-2]))
    #    else:
    #        logger.info(f"    ⚠️ unexpected token: {tok}")
    # logger.info(f"    • Converted to {len(speech_ids)
    #                                  } integer codes (sample: {speech_ids[:5]})")

    # speech_tensor = torch.tensor(speech_ids).cuda().unsqueeze(0).unsqueeze(0)
    # logger.info(f"    • Speech tensor shape for decode: {
    #    tuple(speech_tensor.shape)}")

    # 9) Decode to waveform
    # t0 = time.time()
    # wav_tensor = codec.decode_code(speech_tensor)
    # t1 = time.time()
    # logger.info(f"\n[9] Decoded waveform in {t1-t0:.3f}s")
    # logger.info(f"    • Waveform tensor shape: {
    #    tuple(wav_tensor.shape)}, dtype: {wav_tensor.dtype}")

    # 10) Write to WAV
    # wav_path = "gen.wav"
    # sf.write(wav_path, wav_tensor[0, 0, :].cpu().numpy(), 16000)
    # size_mb = os.path.getsize(wav_path) / 1e6
    # logger.info(f"\n[10] Wrote output WAV '{wav_path}' ({size_mb:.2f} MB)")
