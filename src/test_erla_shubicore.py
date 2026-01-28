"""
Test ERLA with ShubiCore adapter - automated test script.

This demonstrates the full ERLA + ShubiCore integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erla import create_erla_system

print("=" * 60)
print("🛡️  ERLA + ShubiCore Test")
print("=" * 60)
print()

# Create system with mock backend (fast) for demo
# In production, use ShubiCoreLLMBackend with real adapter
system = create_erla_system()

# Simulate a security analyst's workflow
test_scenarios = [
    # First time seeing these - will go SLOW path
    {"query": "LuLu firewall blocked ruby process connecting to 185.234.x.x on port 443", "desc": "Firewall alert"},
    {"query": "Detected C2 beacon pattern with 60-second intervals to unknown IP", "desc": "C2 detection"},
    {"query": "Suspicious DNS queries from chrome process to unusual domains", "desc": "DNS anomaly"},
    
    # Similar queries - should hit FAST path
    {"query": "LuLu blocked python process making outbound connection", "desc": "Similar firewall alert"},
    {"query": "Seeing beaconing behavior every minute from unknown process", "desc": "Similar C2 pattern"},
    
    # Novel query - will go SLOW
    {"query": "Memory dump detected possible credential harvesting", "desc": "New pattern"},
    
    # Similar to novel - should hit FAST
    {"query": "Credential dumping activity detected in memory", "desc": "Similar credential alert"},
]

print("📋 Processing security scenarios...\n")

for i, scenario in enumerate(test_scenarios, 1):
    print(f"--- Scenario {i}: {scenario['desc']} ---")
    print(f"Query: {scenario['query'][:60]}...")
    
    result = system.process_task({"query": scenario["query"]})
    
    path = result['path'].upper()
    if path == "FAST":
        print(f"⚡ PATH: {path} (confidence: {result.get('confidence', 0):.2f})")
        print(f"   Pattern matched: {result.get('pattern', 'N/A')[:50]}...")
    else:
        print(f"🐢 PATH: {path}")
        print(f"   Learnings extracted: {result.get('learnings_extracted', 0)}")
    
    print(f"   Response: {result.get('response', 'N/A')[:80]}...")
    print()

# Final statistics
print("=" * 60)
print("📊 Session Statistics")
print("=" * 60)
stats = system.get_stats()
for key, value in stats.items():
    print(f"   {key}: {value}")

print()
print("=" * 60)
print("🎯 Key Metrics")
print("=" * 60)
print(f"   Total queries: {stats['total_queries']}")
print(f"   Fast path hits: {stats['fast_path_hits']} ({stats['fast_path_rate']})")
print(f"   Knowledge learned: {stats['knowledge_index_size']} patterns")
print()

if stats['fast_path_hits'] > 0:
    print("✅ SUCCESS: ERLA fast path is working!")
    print("   Similar queries are being served instantly from learned knowledge.")
else:
    print("⚠️  No fast path hits - may need to adjust similarity threshold")

print()
print("=" * 60)
print("🔮 What This Means")
print("=" * 60)
print("""
In production with the real ShubiCore adapter:

1. SLOW PATH (~2-5 seconds):
   - Full LLM inference with your trained LoRA adapter
   - Deep security analysis using your methodology
   - Extracts learnings for future use

2. FAST PATH (~10 milliseconds):
   - Instant response from knowledge index
   - No LLM inference needed
   - Gets faster as system learns more

3. RECURSIVE IMPROVEMENT:
   - Every slow path query adds to knowledge
   - System automatically gets smarter
   - No manual retraining needed
""")
