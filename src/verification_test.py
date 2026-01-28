#!/usr/bin/env python3
"""
ERLA + ShubiCore Verification Test

Tests that the model reaches the same conclusions as the original
Windsurf analysis sessions.

Author: Hana Omori
Date: January 27, 2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erla import create_erla_system

# Verification test cases - queries and expected key conclusions
VERIFICATION_TESTS = [
    {
        "name": "LuLu Firewall Alert Investigation",
        "query": "I got a LuLu firewall alert. A process is trying to make an outbound connection. How do I investigate?",
        "expected_keywords": ["codesign", "lsof", "ps aux", "investigation", "phase"],
        "expected_conclusion": "Should provide multi-phase investigation workflow",
    },
    {
        "name": "C2 Beacon Detection",
        "query": "I see outbound connections to the same IP every 60 seconds exactly. The traffic is HTTPS to port 443. Is this C2?",
        "expected_keywords": ["beacon", "C2", "interval", "suspicious", "75%"],
        "expected_conclusion": "Should identify as potential C2 with ~75% confidence",
    },
    {
        "name": "Ruby DNS Connection (Benign)",
        "query": "LuLu blocked ruby trying to connect to an IPv6 address on port 53. The binary is /System/Library/Frameworks/Ruby.framework/Versions/2.6/usr/bin/ruby. I wasn't running any Ruby code. Should I be worried?",
        "expected_keywords": ["benign", "LOW", "safe", "block", "Xcode", "gem"],
        "expected_conclusion": "Should classify as LOW severity, benign activity",
    },
    {
        "name": "SQL Injection Attack",
        "query": "My WAF logged these requests: GET /search?q=1' OR '1'='1, GET /login?user=admin'--, GET /api/users?id=1 UNION SELECT * FROM passwords. What am I dealing with?",
        "expected_keywords": ["SQL injection", "CRITICAL", "attack", "block", "parameterized"],
        "expected_conclusion": "Should identify as CRITICAL SQL injection attack",
    },
    {
        "name": "Mobile APT Multi-Vector Attack",
        "query": "I'm seeing multiple TLS failures across my mobile apps, suspicious WiFi networks appearing, and UDP traffic spikes. What's happening?",
        "expected_keywords": ["APT", "CRITICAL", "MITM", "rogue", "WiFi", "vector"],
        "expected_conclusion": "Should identify as multi-vector APT attack",
    },
]


def run_verification(use_mock=True):
    """Run verification tests."""
    
    print("=" * 70)
    print("🧪 ERLA + ShubiCore Verification Test")
    print("=" * 70)
    print()
    print(f"Mode: {'MOCK (fast)' if use_mock else 'REAL MODEL (slow)'}")
    print(f"Tests: {len(VERIFICATION_TESTS)}")
    print()
    
    # Create system
    system = create_erla_system()
    
    results = []
    
    for i, test in enumerate(VERIFICATION_TESTS, 1):
        print(f"{'='*70}")
        print(f"TEST {i}/{len(VERIFICATION_TESTS)}: {test['name']}")
        print(f"{'='*70}")
        print()
        print(f"📝 Query: {test['query'][:80]}...")
        print()
        
        # Process through ERLA
        result = system.process_task({"query": test["query"]})
        response = result.get("response", "")
        path = result.get("path", "unknown")
        
        print(f"📍 Path: {path.upper()}")
        print(f"💬 Response:\n{response[:500]}...")
        print()
        
        # Check for expected keywords
        response_lower = response.lower()
        found_keywords = []
        missing_keywords = []
        
        for keyword in test["expected_keywords"]:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        keyword_score = len(found_keywords) / len(test["expected_keywords"]) * 100
        
        print(f"🎯 Expected Conclusion: {test['expected_conclusion']}")
        print(f"✅ Found keywords ({len(found_keywords)}/{len(test['expected_keywords'])}): {', '.join(found_keywords) or 'None'}")
        if missing_keywords:
            print(f"❌ Missing keywords: {', '.join(missing_keywords)}")
        print(f"📊 Keyword Match: {keyword_score:.0f}%")
        print()
        
        results.append({
            "name": test["name"],
            "score": keyword_score,
            "found": found_keywords,
            "missing": missing_keywords,
            "path": path,
        })
    
    # Summary
    print("=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    
    total_score = sum(r["score"] for r in results) / len(results)
    
    for r in results:
        status = "✅" if r["score"] >= 50 else "⚠️" if r["score"] >= 25 else "❌"
        print(f"{status} {r['name']}: {r['score']:.0f}% match ({r['path']})")
    
    print()
    print(f"{'='*70}")
    print(f"OVERALL SCORE: {total_score:.0f}%")
    print(f"{'='*70}")
    
    if total_score >= 70:
        print("✅ Model is reaching similar conclusions to original analysis!")
    elif total_score >= 40:
        print("⚠️ Model partially matches - may need more training data")
    else:
        print("❌ Model not matching - check training or use real model")
    
    # Show ERLA stats
    print()
    print("📈 ERLA Statistics:")
    stats = system.get_stats()
    print(f"   Fast path hits: {stats['fast_path_hits']} ({stats['fast_path_rate']})")
    print(f"   Knowledge learned: {stats['knowledge_index_size']} patterns")
    
    return total_score


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Use real model instead of mock")
    args = parser.parse_args()
    
    run_verification(use_mock=not args.real)
