"""
Demo: ERLA Fast Path vs Slow Path

Shows how the system gets faster as it learns.
"""

from erla import create_erla_system

print("=" * 60)
print("🛡️  ERLA: Fast Path Demo")
print("=" * 60)
print()

system = create_erla_system()

# Round 1: All queries go through SLOW path (no prior knowledge)
print("📍 ROUND 1: First time seeing these patterns")
print("-" * 60)

queries_round1 = [
    {"query": "LuLu firewall blocked unknown process connecting to external IP"},
    {"query": "C2 beacon detected with 60-second interval"},
    {"query": "Suspicious ruby process making outbound connections"},
]

for task in queries_round1:
    result = system.process_task(task)
    print(f"  [{result['path'].upper()}] {task['query'][:50]}...")

print()
stats = system.get_stats()
print(f"  Knowledge index size: {stats['knowledge_index_size']}")
print(f"  Fast path rate: {stats['fast_path_rate']}")

# Round 2: Similar queries should hit FAST path
print()
print("📍 ROUND 2: Similar queries (should hit fast path)")
print("-" * 60)

queries_round2 = [
    {"query": "LuLu blocked a process trying to connect externally"},  # Similar to #1
    {"query": "Seeing C2 beaconing behavior every minute"},  # Similar to #2
    {"query": "Ruby making suspicious network calls"},  # Similar to #3
]

for task in queries_round2:
    result = system.process_task(task)
    path = result['path'].upper()
    extra = f" (conf: {result.get('confidence', 0):.2f})" if path == "FAST" else ""
    print(f"  [{path}]{extra} {task['query'][:50]}...")

print()
stats = system.get_stats()
print(f"  Knowledge index size: {stats['knowledge_index_size']}")
print(f"  Fast path rate: {stats['fast_path_rate']}")

# Round 3: Novel query goes slow, then similar goes fast
print()
print("📍 ROUND 3: Novel query, then similar")
print("-" * 60)

result1 = system.process_task({"query": "Detecting DNS tunneling exfiltration attempts"})
print(f"  [{result1['path'].upper()}] DNS tunneling query (novel)")

result2 = system.process_task({"query": "DNS exfil tunnel detected in network traffic"})
path = result2['path'].upper()
extra = f" (conf: {result2.get('confidence', 0):.2f})" if path == "FAST" else ""
print(f"  [{path}]{extra} Similar DNS query")

# Final stats
print()
print("=" * 60)
print("📊 Final Statistics")
print("=" * 60)
stats = system.get_stats()
for key, value in stats.items():
    print(f"   {key}: {value}")

print()
print("✅ Demo complete!")
print()
print("KEY INSIGHT: System learns from slow path queries and")
print("             serves similar queries via fast path (~100x faster)")
