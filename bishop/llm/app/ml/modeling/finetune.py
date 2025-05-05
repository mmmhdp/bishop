import os
import torch
from datasets import load_dataset
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)

def finetune(
    dataset_path: str,
    model_name_or_path: str = "ai-forever/rugpt3medium_based_on_gpt2",
    output_dir: str = "./finetuned_model",
    num_train_epochs: int = 10,
    per_device_train_batch_size: int = 6,
    gradient_accumulation_steps: int = 1,
    learning_rate: float = 5e-5,
    save_steps: int = 880,
    logging_steps: int = 500,
):
    os.environ["WANDB_DISABLED"] = "true"

    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = GPT2Tokenizer.from_pretrained(model_name_or_path)
    tokenizer.pad_token = tokenizer.eos_token

    model = GPT2LMHeadModel.from_pretrained(model_name_or_path).to(device)

    dataset = load_dataset("text", data_files={"train": dataset_path})
    tokenized_datasets = dataset.map(
        lambda examples: tokenizer(
            examples["text"], truncation=True, padding="max_length", max_length=512
        ),
        batched=True,
        remove_columns=["text"]
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        save_strategy="steps",
        save_steps=save_steps,
        logging_steps=logging_steps,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        data_collator=data_collator,
    )

    trainer.train()

    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
