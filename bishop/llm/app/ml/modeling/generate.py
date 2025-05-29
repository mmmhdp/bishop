import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from pathlib import Path

class TextGenerator:
    def __init__(self, model_dir: str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = GPT2LMHeadModel.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_length: int = 100,
        do_sample: bool = True,
        num_beams: int = 2,
        temperature: float = 1.5,
        top_p: float = 0.9
    ) -> str:
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids=input_ids,
                do_sample=do_sample,
                num_beams=num_beams,
                temperature=temperature,
                top_p=top_p,
                max_length=max_length,
                pad_token_id=self.tokenizer.pad_token_id
            )

        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

