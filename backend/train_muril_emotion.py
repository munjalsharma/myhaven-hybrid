# -*- coding: utf-8 -*-
"""
PyTorch MuRIL-BERT Fine-Tuning Pipeline for High-Precision Multilingual Emotion Classification.
Fine-tunes the classification head + top MuRIL transformer layer on English, Hindi, and Hinglish.
Saves fine-tuned weights directly to backend/muril_emotion_model.pth.
"""

import json
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, BertConfig, BertModel
from mindmate_integration import MuRILEmotionClassifier, EMOTION_LABELS, MURIL_BASE

class MultilingualEmotionDataset(Dataset):
    def __init__(self, data_path, tokenizer, max_len=96):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item["text"]
        labels = torch.tensor(item["labels"], dtype=torch.float32)
        
        inputs = self.tokenizer(
            text,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": inputs["input_ids"].squeeze(0),
            "attention_mask": inputs["attention_mask"].squeeze(0),
            "labels": labels
        }


def train_model(epochs=3, batch_size=32, lr_head=1e-3, lr_backbone=1e-5):
    print("=" * 65)
    print("STARTING MURIL-BERT MULTILINGUAL FINE-TUNING")
    print("=" * 65)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device selected for training: {device}")
    
    dataset_path = os.path.join(os.path.dirname(__file__), "multilingual_emotion_dataset.json")
    model_save_path = os.path.join(os.path.dirname(__file__), "muril_emotion_model.pth")
    
    # Fast local snapshot loading for Windows
    snapshot_path = os.path.expanduser(r"~/.cache/huggingface/hub/models--google--muril-base-cased/snapshots/afd9f36c7923d54e97903922ff1b260d091d202f")
    if os.path.exists(snapshot_path):
        print(f"[Train] Using cached MuRIL from: {snapshot_path}")
        tokenizer = AutoTokenizer.from_pretrained(snapshot_path)
        cfg = BertConfig.from_pretrained(snapshot_path)
    else:
        tokenizer = AutoTokenizer.from_pretrained(MURIL_BASE)
        cfg = BertConfig.from_pretrained(MURIL_BASE)
        
    dataset = MultilingualEmotionDataset(dataset_path, tokenizer, max_len=96)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    
    base_muril = BertModel(cfg)
    model = MuRILEmotionClassifier(muril_model=base_muril).to(device)
    
    # Load existing trained weights for transfer learning
    if os.path.exists(model_save_path):
        try:
            ckpt = torch.load(model_save_path, map_location=device)
            state = ckpt.get("model_state_dict", ckpt) if isinstance(ckpt, dict) else ckpt
            model.load_state_dict(state, strict=False)
            print("[Train] Loaded existing weights for fine-tuning initialization.")
        except Exception as e:
            print(f"[Train] Notice initializing fresh weights: {e}")
            
    # Freeze lower layers (embeddings + first 10 transformer layers)
    for p in model.muril.embeddings.parameters():
        p.requires_grad = False
    for i in range(10):
        for p in model.muril.encoder.layer[i].parameters():
            p.requires_grad = False
            
    # Unfreeze top layers (layer 10 & 11) for subtle cross-lingual attention fine-tuning
    for i in [10, 11]:
        for p in model.muril.encoder.layer[i].parameters():
            p.requires_grad = True
            
    # Ensure classification head is fully trainable
    for p in model.classifier.parameters():
        p.requires_grad = True
        
    backbone_params = [p for p in model.muril.parameters() if p.requires_grad]
    head_params = [p for p in model.classifier.parameters() if p.requires_grad]
    
    optimizer = torch.optim.AdamW([
        {"params": backbone_params, "lr": lr_backbone, "weight_decay": 0.01},
        {"params": head_params, "lr": lr_head, "weight_decay": 0.01}
    ])
    criterion = nn.BCEWithLogitsLoss()
    
    print(f"[Train] Training on {len(dataset)} samples across {epochs} epochs...")
    model.train()
    
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        step = 0
        for batch in dataloader:
            step += 1
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            optimizer.zero_grad()
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            if step % 35 == 0:
                print(f"  Epoch [{epoch}/{epochs}] Batch [{step}/{len(dataloader)}] - Batch Loss: {loss.item():.4f}")
            
        avg_loss = total_loss / len(dataloader)
        print(f"==> Epoch [{epoch}/{epochs}] Finished - Average Loss: {avg_loss:.4f}\n")
        
    # Save fine-tuned checkpoint
    torch.save({
        "model_state_dict": model.state_dict(),
        "epoch": epochs,
        "labels": EMOTION_LABELS
    }, model_save_path)
    
    print("=" * 65)
    print("SUCCESS: FINE-TUNING COMPLETE!")
    print(f"📁 Updated weights saved to: {model_save_path}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    train_model(epochs=3, batch_size=32)
