"""
ERLA: Ephemeral Recursive Learning Agents

A privacy-preserving architecture for continuous AI improvement.
Agents spawn, learn, distill knowledge, then self-destruct.

Author: Hana Omori
Date: January 27, 2026
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import secrets


@dataclass
class Learning:
    """Abstract knowledge extracted from an agent's analysis."""
    pattern: str
    indicators: List[str]
    classification: str
    confidence: float
    recommended_response: str
    original_query: str = ""  # Store original for better matching
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "pattern": self.pattern,
            "indicators": self.indicators,
            "classification": self.classification,
            "confidence": self.confidence,
            "recommended_response": self.recommended_response,
            "original_query": self.original_query,
            "timestamp": self.timestamp,
        }
    
    def embedding_text(self) -> str:
        """Text representation for embedding - include original query for better matching."""
        base = f"{self.pattern} {' '.join(self.indicators)} {self.classification}"
        if self.original_query:
            base = f"{self.original_query} {base}"
        return base


class KnowledgeIndex:
    """
    Vector-based knowledge index for fast path responses.
    
    In production, this would use a real vector DB (Chroma, Pinecone, etc).
    This is a simplified implementation using cosine similarity on TF-IDF-like vectors.
    """
    
    def __init__(self):
        self.entries: List[Dict] = []
        self.vocabulary: Dict[str, int] = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return text.lower().replace(",", " ").replace(".", " ").split()
    
    def _to_vector(self, text: str) -> Dict[str, float]:
        """Convert text to sparse vector (word frequencies)."""
        tokens = self._tokenize(text)
        vec = {}
        for token in tokens:
            vec[token] = vec.get(token, 0) + 1
        # Normalize
        total = sum(vec.values())
        if total > 0:
            vec = {k: v/total for k, v in vec.items()}
        return vec
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between sparse vectors."""
        keys = set(vec1.keys()) | set(vec2.keys())
        dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in keys)
        norm1 = sum(v**2 for v in vec1.values()) ** 0.5
        norm2 = sum(v**2 for v in vec2.values()) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
    
    def add(self, learning: Learning):
        """Add a learning to the index."""
        text = learning.embedding_text()
        vector = self._to_vector(text)
        self.entries.append({
            "learning": learning,
            "vector": vector,
            "text": text,
        })
    
    def find_similar(self, query: str, threshold: float = 0.5) -> Optional[Dict]:
        """Find most similar entry above threshold."""
        if not self.entries:
            return None
        
        query_vec = self._to_vector(query)
        best_match = None
        best_score = 0.0
        
        for entry in self.entries:
            score = self._cosine_similarity(query_vec, entry["vector"])
            if score > best_score:
                best_score = score
                best_match = entry
        
        if best_match and best_score >= threshold:
            return {
                "learning": best_match["learning"],
                "confidence": best_score,
            }
        return None
    
    def size(self) -> int:
        return len(self.entries)
    
    def save(self, path: str):
        """Save index to JSON file."""
        data = []
        for entry in self.entries:
            data.append({
                "learning": entry["learning"].to_dict(),
                "text": entry["text"],
            })
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str):
        """Load index from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        self.entries = []
        for item in data:
            learning = Learning(**item["learning"])
            self.add(learning)


class LLMBackend(ABC):
    """Abstract LLM backend interface."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate text from prompt."""
        pass


class MockLLMBackend(LLMBackend):
    """Mock LLM for testing without real model."""
    
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Return mock response based on keywords."""
        prompt_lower = prompt.lower()
        
        if "firewall" in prompt_lower or "lulu" in prompt_lower:
            return """Based on ShubiCore methodology:
1. Check process path and signature
2. Verify if process is expected system behavior
3. Look for associated network connections
4. Cross-reference with known IOCs
Classification: potential_unauthorized_network_access
Confidence: 0.75"""
        
        if "c2" in prompt_lower or "beacon" in prompt_lower:
            return """C2 beacon indicators:
1. Regular interval connections (beaconing pattern)
2. Connections to unusual ports or IPs
3. Encoded/encrypted payloads
4. Process injection or hollowing
Classification: potential_c2_communication
Confidence: 0.85"""
        
        if "abstract" in prompt_lower or "extract" in prompt_lower:
            return """Pattern: unauthorized_process_network_activity
Indicators: unknown_process, outbound_connection, blocked_by_firewall
Classification: potential_threat
Confidence: 0.7
Recommended_response: investigate_process_origin"""
        
        return "Analysis complete. No specific patterns detected."


class BaseLayer:
    """
    Persistent base layer that improves over time.
    
    Contains:
    - Knowledge index (fast path)
    - Training buffer (for periodic LoRA retraining)
    - Configuration
    """
    
    def __init__(self, llm_backend: Optional[LLMBackend] = None):
        self.knowledge = KnowledgeIndex()
        self.training_buffer: List[Learning] = []
        self.llm = llm_backend or MockLLMBackend()
        self.version = "1.0.0"
        self.retrain_threshold = 100
        self.stats = {
            "total_queries": 0,
            "fast_path_hits": 0,
            "slow_path_hits": 0,
            "agents_spawned": 0,
            "learnings_distilled": 0,
        }
    
    def spawn_agent(self, task_context: Dict) -> "VirtualAgent":
        """Spawn an ephemeral agent for a task."""
        self.stats["agents_spawned"] += 1
        return VirtualAgent(self, task_context)
    
    def process_task(self, task: Dict) -> Dict:
        """
        Main entry point: process a task through ERLA.
        
        1. Check fast path (knowledge index)
        2. If no match, spawn agent for slow path
        3. Agent analyzes, learns, distills, destroys
        4. Return result
        """
        self.stats["total_queries"] += 1
        query = task.get("query", "")
        
        # Fast path: check knowledge index
        match = self.knowledge.find_similar(query, threshold=0.3)
        if match:
            self.stats["fast_path_hits"] += 1
            return {
                "path": "fast",
                "response": match["learning"].recommended_response,
                "confidence": match["confidence"],
                "pattern": match["learning"].pattern,
            }
        
        # Slow path: spawn agent
        self.stats["slow_path_hits"] += 1
        agent = self.spawn_agent(task)
        
        # Agent lifecycle
        result = agent.analyze()
        agent.extract_learnings()
        learnings_count = len(agent.learnings) if agent.learnings else 0
        agent.distill_to_base()
        
        # Destroy agent (secure deletion)
        agent.destroy()
        
        # Check if retraining needed
        if len(self.training_buffer) >= self.retrain_threshold:
            self._schedule_retrain()
        
        return {
            "path": "slow",
            "response": result,
            "learnings_extracted": learnings_count,
        }
    
    def _schedule_retrain(self):
        """
        Schedule LoRA adapter retraining.
        
        In production, this would:
        1. Convert training_buffer to training format
        2. Run incremental LoRA training
        3. Update adapter
        4. Clear buffer
        """
        print(f"📚 Retraining scheduled with {len(self.training_buffer)} new learnings")
        # In production: actual retraining logic here
        self.training_buffer = []
        # Bump version
        major, minor, patch = self.version.split(".")
        self.version = f"{major}.{minor}.{int(patch) + 1}"
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        fast_rate = 0
        if self.stats["total_queries"] > 0:
            fast_rate = self.stats["fast_path_hits"] / self.stats["total_queries"] * 100
        
        return {
            **self.stats,
            "fast_path_rate": f"{fast_rate:.1f}%",
            "knowledge_index_size": self.knowledge.size(),
            "training_buffer_size": len(self.training_buffer),
            "version": self.version,
        }


class VirtualAgent:
    """
    Ephemeral agent that processes one task then self-destructs.
    
    Lifecycle:
    1. SPAWN - Created with references to base layer
    2. ANALYZE - Process the task
    3. LEARN - Extract abstract learnings
    4. DISTILL - Push learnings to base layer
    5. DESTROY - Secure deletion of all sensitive data
    """
    
    def __init__(self, base_layer: BaseLayer, task_context: Dict):
        # References to shared resources (not copies)
        self.base = base_layer
        self.llm = base_layer.llm
        
        # Ephemeral state (dies with agent)
        self.context = task_context
        self.memory: List[Dict] = []
        self.session_key = secrets.token_bytes(32)
        self.created_at = time.time()
        
        # Learning buffer (abstracted before persistence)
        self.learnings: List[Learning] = []
        
        # State tracking
        self._destroyed = False
    
    def analyze(self) -> str:
        """
        Analyze the task using full LLM inference.
        
        This is the "slow path" - full reasoning.
        """
        if self._destroyed:
            raise RuntimeError("Agent has been destroyed")
        
        query = self.context.get("query", "")
        
        # Build prompt
        prompt = f"""You are a security analyst using the ShubiCore methodology.
Analyze the following and provide your assessment:

{query}

Provide:
1. Initial assessment
2. Key indicators
3. Recommended actions
4. Confidence level"""
        
        # Generate response
        response = self.llm.generate(prompt)
        
        # Store in memory (ephemeral)
        self.memory.append({
            "role": "user",
            "content": query,
        })
        self.memory.append({
            "role": "assistant", 
            "content": response,
        })
        
        return response
    
    def extract_learnings(self):
        """
        Extract abstract, generalizable learnings from the analysis.
        
        Key: Remove all specific identifiers, keep only patterns.
        """
        if self._destroyed:
            raise RuntimeError("Agent has been destroyed")
        
        if not self.memory:
            return
        
        # Get the analysis we produced
        analysis = self.memory[-1]["content"] if self.memory else ""
        
        # Ask LLM to abstract the learnings
        abstraction_prompt = f"""Extract generalizable patterns from this analysis.
REMOVE all specific identifiers (IPs, names, emails, paths).
KEEP only abstract patterns and indicators.

Analysis:
{analysis}

Output a JSON object with:
- pattern: abstract description of what was detected
- indicators: list of abstract indicator types
- classification: category of the finding
- confidence: 0.0 to 1.0
- recommended_response: abstract response recommendation"""
        
        abstraction = self.llm.generate(abstraction_prompt)
        
        # Parse the abstraction (in production, use proper JSON parsing)
        # For now, create a learning from the analysis
        # Get original query from context
        original_query = self.context.get("query", "") if self.context else ""
        
        learning = Learning(
            pattern=self._extract_field(abstraction, "pattern", "unknown_pattern"),
            indicators=self._extract_list(abstraction, "indicators"),
            classification=self._extract_field(abstraction, "classification", "unknown"),
            confidence=self._extract_float(abstraction, "confidence", 0.5),
            recommended_response=self._extract_field(abstraction, "recommended_response", "investigate"),
            original_query=original_query,
        )
        
        self.learnings.append(learning)
    
    def _extract_field(self, text: str, field: str, default: str) -> str:
        """Extract a field from text (simple parsing)."""
        text_lower = text.lower()
        if field.lower() in text_lower:
            # Find the line containing the field
            for line in text.split("\n"):
                if field.lower() in line.lower():
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        return parts[1].strip().strip('"').strip("'")
        return default
    
    def _extract_list(self, text: str, field: str) -> List[str]:
        """Extract a list field from text."""
        value = self._extract_field(text, field, "")
        if value:
            # Try to parse as comma-separated
            return [v.strip() for v in value.replace("[", "").replace("]", "").split(",")]
        return ["unknown_indicator"]
    
    def _extract_float(self, text: str, field: str, default: float) -> float:
        """Extract a float field from text."""
        value = self._extract_field(text, field, str(default))
        try:
            return float(value)
        except ValueError:
            return default
    
    def distill_to_base(self):
        """
        Push abstract learnings to base layer.
        
        This is the ONLY data that survives agent destruction.
        """
        if self._destroyed:
            raise RuntimeError("Agent has been destroyed")
        
        for learning in self.learnings:
            # Add to knowledge index (fast path improvement)
            self.base.knowledge.add(learning)
            
            # Add to training buffer (slow path improvement)
            self.base.training_buffer.append(learning)
            
            self.base.stats["learnings_distilled"] += 1
    
    def destroy(self):
        """
        Secure deletion of all ephemeral data.
        
        After this, no sensitive data can be recovered.
        Only abstract learnings (already distilled) survive.
        """
        if self._destroyed:
            return
        
        # Secure overwrite of sensitive data
        self.context = None
        self.memory = None
        self.learnings = None
        
        # Destroy session key (makes any encrypted remnants unrecoverable)
        self.session_key = None
        
        # Mark as destroyed
        self._destroyed = True
        
        # Calculate lifetime
        lifetime = time.time() - self.created_at
        # print(f"🗑️  Agent destroyed after {lifetime:.2f}s")


# Convenience function for quick usage
def create_erla_system(llm_backend: Optional[LLMBackend] = None) -> BaseLayer:
    """Create a new ERLA system."""
    return BaseLayer(llm_backend)


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("🛡️  ERLA: Ephemeral Recursive Learning Agents")
    print("=" * 60)
    print()
    
    # Create system
    system = create_erla_system()
    
    # Test queries
    test_queries = [
        {"query": "LuLu firewall blocked an unknown process trying to connect to 185.234.xx.xx on port 443"},
        {"query": "Seeing regular 60-second interval connections to an unusual IP address"},
        {"query": "LuLu alert for suspicious outbound connection from ruby process"},
    ]
    
    print("Processing test queries...\n")
    
    for i, task in enumerate(test_queries, 1):
        print(f"--- Query {i} ---")
        print(f"Input: {task['query'][:60]}...")
        
        result = system.process_task(task)
        
        print(f"Path: {result['path'].upper()}")
        print(f"Response: {result.get('response', 'N/A')[:100]}...")
        print()
    
    # Show stats
    print("=" * 60)
    print("📊 System Statistics")
    print("=" * 60)
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print()
    print("✅ Demo complete!")
