#!/usr/bin/env python3
"""
Quick verification with real ShubiCore adapter.
Tests just ONE query to verify the model works.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Path to ShubiCore adapter
ADAPTER_PATH = "/Users/akidob0t/Documents/OfflineLogAnalyzerAI/shubicore/training/shubicore-tinyllama-lora"

def test_real_model():
    print("=" * 60)
    print("🧪 Quick ShubiCore Verification")
    print("=" * 60)
    print()
    print(f"Adapter: {ADAPTER_PATH}")
    print()
    
    # Load model
    print("📥 Loading model (this takes ~1 min)...")
    start = time.time()
    
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
    base_model = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype=torch.float32,
    )
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()
    
    load_time = time.time() - start
    print(f"✅ Model loaded in {load_time:.1f}s")
    print()
    
    # Test query - C2 beacon (should get good response)
    query = "I see outbound connections to the same IP every 60 seconds exactly. The traffic is HTTPS to port 443. Is this C2?"
    
    print(f"📝 Query: {query}")
    print()
    print("⏳ Generating response (this takes ~2-3 min on CPU)...")
    
    # Generate - use the same format as training data
    start = time.time()
    
    system_prompt = "You are ShubiCore, a cybersecurity incident investigation assistant. You help security analysts investigate threats, analyze IOCs, interpret logs, and respond to incidents. Be precise, actionable, and cite evidence."
    
    input_text = f"System: {system_prompt}\n\nUser: {query}\n\nAssistant:"
    inputs = tokenizer(input_text, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Assistant:" in response:
        response = response.split("Assistant:")[-1].strip()
    
    gen_time = time.time() - start
    
    print(f"✅ Generated in {gen_time:.1f}s")
    print()
    print("=" * 60)
    print("💬 ShubiCore Response:")
    print("=" * 60)
    print(response)
    print()
    
    # Check for expected keywords
    expected = ["beacon", "C2", "interval", "connection"]
    found = [k for k in expected if k.lower() in response.lower()]
    
    print("=" * 60)
    print(f"🎯 Keyword Check: {len(found)}/{len(expected)} found")
    print(f"   Found: {', '.join(found) if found else 'None'}")
    print("=" * 60)
    
    if len(found) >= 2:
        print("✅ Model appears to be working correctly!")
    else:
        print("⚠️ Model may need more training or different prompt format")


if __name__ == "__main__":
    test_real_model()
