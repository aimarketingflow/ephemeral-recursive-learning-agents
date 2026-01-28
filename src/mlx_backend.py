"""
MLX Backend for ERLA - Optimized for Apple Silicon

MLX is Apple's machine learning framework optimized for M1/M2/M3 chips.
It provides 5-10x faster inference compared to PyTorch on Apple Silicon.

Author: Hana Omori
Date: January 27, 2026
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erla import LLMBackend, BaseLayer


class MLXBackend(LLMBackend):
    """
    LLM backend using MLX for fast Apple Silicon inference.
    
    Requires: pip install mlx mlx-lm
    """
    
    def __init__(self, model_path: str = "/Users/akidob0t/.cache/erla_models/qwen-0.5b-4bit"):
        """
        Initialize MLX backend.
        
        Args:
            model_name: HuggingFace model name (must be MLX-compatible)
                       Use 4-bit quantized models for best speed on 8GB RAM
        """
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._loaded = False
    
    def _load_model(self):
        """Lazy load the model."""
        if self._loaded:
            return
        
        print(f"📥 Loading MLX model: {self.model_path}")
        
        from mlx_lm import load
        
        self.model, self.tokenizer = load(self.model_path)
        
        self._loaded = True
        print("✅ MLX model loaded!")
    
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate text using MLX (fast on Apple Silicon)."""
        self._load_model()
        
        from mlx_lm import generate
        
        start_time = time.time()
        
        # Format as chat
        messages = [{"role": "user", "content": prompt}]
        formatted = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        # Generate
        response = generate(
            self.model,
            self.tokenizer,
            prompt=formatted,
            max_tokens=max_tokens,
            verbose=False,
        )
        
        elapsed = time.time() - start_time
        print(f"   ⚡ MLX generated in {elapsed:.2f}s")
        
        return response


def create_mlx_erla(model_path: str = "/Users/akidob0t/.cache/erla_models/qwen-0.5b-4bit") -> BaseLayer:
    """Create an ERLA system with MLX backend for fast Apple Silicon inference."""
    backend = MLXBackend(model_path)
    return BaseLayer(backend)


if __name__ == "__main__":
    print("=" * 60)
    print("🍎 MLX Backend Speed Test")
    print("=" * 60)
    print()
    
    # Create system with MLX backend
    system = create_mlx_erla()
    
    # Test queries
    test_queries = [
        "How should I investigate a LuLu firewall alert for an unknown process?",
        "What are signs of C2 beacon activity?",
        "Similar firewall alert for blocked process",  # Should hit fast path after learning
    ]
    
    print("Running speed test...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"--- Query {i} ---")
        print(f"Q: {query[:50]}...")
        
        start = time.time()
        result = system.process_task({"query": query})
        total = time.time() - start
        
        path = result['path'].upper()
        print(f"Path: {path}")
        print(f"Total time: {total:.2f}s")
        print(f"Response: {result.get('response', '')[:100]}...")
        print()
    
    # Stats
    print("=" * 60)
    print("📊 Statistics")
    print("=" * 60)
    stats = system.get_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")
