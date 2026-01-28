#!/usr/bin/env python3
"""
ERLA Chat - Interactive security assistant

Uses the ERLA architecture with fast path for instant responses
on similar queries.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erla import create_erla_system

def main():
    print("=" * 60)
    print("🛡️  ERLA Security Chat")
    print("=" * 60)
    print()
    print("Commands:")
    print("  'stats' - Show system statistics")
    print("  'quit'  - Exit")
    print()
    print("Ask security questions and watch the system learn!")
    print("-" * 60)
    
    system = create_erla_system()
    
    while True:
        try:
            query = input("\n🔍 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break
        
        if not query:
            continue
        
        if query.lower() == "quit":
            break
        
        if query.lower() == "stats":
            stats = system.get_stats()
            print("\n📊 System Statistics:")
            print(f"   Total queries: {stats['total_queries']}")
            print(f"   Fast path hits: {stats['fast_path_hits']} ({stats['fast_path_rate']})")
            print(f"   Knowledge learned: {stats['knowledge_index_size']} patterns")
            print(f"   Version: {stats['version']}")
            continue
        
        # Process query through ERLA
        result = system.process_task({"query": query})
        
        path = result['path']
        response = result.get('response', 'No response')
        
        if path == "fast":
            conf = result.get('confidence', 0)
            print(f"\n⚡ [FAST PATH - {conf:.0%} match]")
        else:
            print(f"\n🧠 [SLOW PATH - learning...]")
        
        print(f"\n🤖 ShubiCore: {response}")
    
    # Final stats
    print("\n" + "=" * 60)
    print("📊 Session Summary")
    print("=" * 60)
    stats = system.get_stats()
    print(f"   Queries processed: {stats['total_queries']}")
    print(f"   Fast path rate: {stats['fast_path_rate']}")
    print(f"   Patterns learned: {stats['knowledge_index_size']}")
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
