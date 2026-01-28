"""
ERLA + ShubiCore Integration

Connects the ERLA architecture with a real LoRA-tuned model.

Author: Hana Omori
Date: January 27, 2026
"""

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erla import BaseLayer, LLMBackend, create_erla_system


class ShubiCoreLLMBackend(LLMBackend):
    """
    LLM backend using the ShubiCore LoRA adapter.
    
    Requires:
    - transformers
    - peft
    - torch
    """
    
    def __init__(self, adapter_path: str, base_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.adapter_path = adapter_path
        self.base_model_name = base_model
        self.model = None
        self.tokenizer = None
        self._loaded = False
    
    def _load_model(self):
        """Lazy load the model (expensive operation)."""
        if self._loaded:
            return
        
        print("📥 Loading ShubiCore model...")
        
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.adapter_path)
        
        # Load base model
        self.base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        
        # Load LoRA adapter
        self.model = PeftModel.from_pretrained(self.base_model, self.adapter_path)
        self.model.eval()
        
        self._loaded = True
        print("✅ ShubiCore model loaded!")
    
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate text using the ShubiCore model."""
        self._load_model()
        
        import torch
        
        # Format prompt
        input_text = f"User: {prompt}\n\nAssistant:"
        inputs = self.tokenizer(input_text, return_tensors="pt")
        
        # Move to device
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract assistant response
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()
        
        return response


def create_shubicore_erla(adapter_path: str) -> BaseLayer:
    """Create an ERLA system with ShubiCore backend."""
    backend = ShubiCoreLLMBackend(adapter_path)
    return BaseLayer(backend)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ERLA + ShubiCore Demo")
    parser.add_argument("--adapter", required=True, help="Path to ShubiCore LoRA adapter")
    parser.add_argument("--mock", action="store_true", help="Use mock LLM (faster, for testing)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🛡️  ERLA + ShubiCore Integration")
    print("=" * 60)
    print()
    
    # Create system
    if args.mock:
        print("Using MOCK LLM backend (fast mode)")
        system = create_erla_system()
    else:
        print(f"Using ShubiCore adapter: {args.adapter}")
        system = create_shubicore_erla(args.adapter)
    
    print()
    
    # Interactive mode
    print("Enter security queries (type 'quit' to exit, 'stats' for statistics)")
    print("-" * 60)
    
    while True:
        try:
            query = input("\n🔍 Query: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not query:
            continue
        
        if query.lower() == "quit":
            break
        
        if query.lower() == "stats":
            stats = system.get_stats()
            print("\n📊 System Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
            continue
        
        # Process query
        print("\n⏳ Processing...")
        result = system.process_task({"query": query})
        
        print(f"\n📍 Path: {result['path'].upper()}")
        if result['path'] == 'fast':
            print(f"🎯 Pattern: {result.get('pattern', 'N/A')}")
            print(f"📊 Confidence: {result.get('confidence', 0):.2f}")
        print(f"\n💬 Response:\n{result.get('response', 'No response')}")
    
    # Final stats
    print("\n" + "=" * 60)
    print("📊 Final Statistics")
    print("=" * 60)
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Session complete!")
