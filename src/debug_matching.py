"""Debug the knowledge index matching."""

from erla import create_erla_system

system = create_erla_system()

# Add one query
result = system.process_task({"query": "LuLu firewall blocked unknown process"})
print(f"Processed: {result['path']}")

# Check what's in the knowledge index
print("\nKnowledge Index Contents:")
for i, entry in enumerate(system.knowledge.entries):
    print(f"  {i}: {entry['text']}")
    print(f"     Vector keys: {list(entry['vector'].keys())[:10]}...")

# Test similarity
query = "LuLu blocked a process"
print(f"\nTest query: {query}")
match = system.knowledge.find_similar(query, threshold=0.0)
if match:
    print(f"  Best match confidence: {match['confidence']:.3f}")
    print(f"  Pattern: {match['learning'].pattern}")
else:
    print("  No match found")
