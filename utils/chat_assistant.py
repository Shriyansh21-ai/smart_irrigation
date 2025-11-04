# Note: transformers + torch must be installed. This will download the model on first run.
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class ChatAssistant:
    def __init__(self, model_name="google/flan-t5-small", device=None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading chat model {model_name} on {self.device} (may take time)...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)

    def ask(self, prompt, max_length=64):
        toks = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        out = self.model.generate(**toks, max_new_tokens=max_length)
        return self.tokenizer.decode(out[0], skip_special_tokens=True)
