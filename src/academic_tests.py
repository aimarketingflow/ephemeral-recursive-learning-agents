#!/usr/bin/env python3
"""
ERLA Academic Test Suite

Rigorous tests to validate the ERLA architecture claims for publication.

Author: Hana Omori
Date: January 27, 2026
"""

import sys
import os
import time
import json
import random
import tracemalloc
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erla import create_erla_system, KnowledgeIndex, Learning

# Test output directory
RESULTS_DIR = Path(__file__).parent.parent / "test_results"
RESULTS_DIR.mkdir(exist_ok=True)

# Sample queries for testing (security domain)
BASE_QUERIES = [
    "LuLu firewall blocked {process} trying to connect to {ip}",
    "Seeing {interval} second interval connections to {ip} on port {port}",
    "WAF logged SQL injection attempt: {payload}",
    "Suspicious DNS queries from {process} to {domain}",
    "TLS certificate error when connecting to {domain}",
    "Process {process} spawned unexpected child process",
    "Unusual outbound traffic volume from {process}",
    "Failed authentication attempts from {ip}",
    "Kernel panic with {component} in backtrace",
    "Memory dump shows potential {malware_type} indicators",
]

PROCESSES = ["ruby", "python", "node", "chrome", "firefox", "curl", "wget", "nc"]
IPS = ["192.168.1.50", "10.0.0.100", "172.16.0.1", "8.8.8.8", "1.1.1.1"]
PORTS = ["443", "80", "8080", "22", "53", "4444"]
DOMAINS = ["suspicious.com", "malware.net", "c2server.io", "legit.com"]
PAYLOADS = ["1' OR '1'='1", "admin'--", "UNION SELECT", "<script>alert(1)</script>"]
INTERVALS = ["30", "60", "120", "300"]
COMPONENTS = ["AppleMobileDispH13G", "IOKit", "kernel_task", "WindowServer"]
MALWARE_TYPES = ["credential harvesting", "keylogger", "ransomware", "rootkit"]


def generate_query(template_idx=None, variation=0):
    """Generate a query from templates with variations."""
    if template_idx is None:
        template_idx = random.randint(0, len(BASE_QUERIES) - 1)
    
    template = BASE_QUERIES[template_idx]
    
    # Fill in placeholders
    query = template.format(
        process=random.choice(PROCESSES),
        ip=random.choice(IPS),
        port=random.choice(PORTS),
        domain=random.choice(DOMAINS),
        payload=random.choice(PAYLOADS),
        interval=random.choice(INTERVALS),
        component=random.choice(COMPONENTS),
        malware_type=random.choice(MALWARE_TYPES),
    )
    
    return query, template_idx


def test_1_fast_path_efficiency(num_queries=50):
    """
    Test 1: Fast Path Efficiency
    
    Measures how fast path hit rate improves as the system learns.
    """
    print("=" * 70)
    print("TEST 1: Fast Path Efficiency")
    print("=" * 70)
    print(f"Running {num_queries} queries, tracking hit rate over time...")
    print()
    
    system = create_erla_system()
    
    results = {
        "test": "fast_path_efficiency",
        "timestamp": datetime.now().isoformat(),
        "num_queries": num_queries,
        "checkpoints": [],
        "queries": [],
    }
    
    checkpoints = [10, 25, 50, 75, 100]
    
    for i in range(1, num_queries + 1):
        # Generate query - mix of similar (same template) and novel
        if i > 10 and random.random() < 0.6:
            # 60% chance to use a template we've seen before
            template_idx = random.randint(0, min(i-1, len(BASE_QUERIES)-1) % len(BASE_QUERIES))
        else:
            template_idx = None
        
        query, tidx = generate_query(template_idx)
        
        start = time.time()
        result = system.process_task({"query": query})
        elapsed = time.time() - start
        
        results["queries"].append({
            "idx": i,
            "path": result["path"],
            "time_ms": elapsed * 1000,
            "template": tidx,
        })
        
        # Progress indicator
        if i % 10 == 0:
            stats = system.get_stats()
            hit_rate = stats["fast_path_hits"] / i * 100
            print(f"  Query {i}: Fast path rate = {hit_rate:.1f}%")
            
            if i in checkpoints:
                results["checkpoints"].append({
                    "query_count": i,
                    "fast_path_hits": stats["fast_path_hits"],
                    "hit_rate_pct": hit_rate,
                    "knowledge_size": stats["knowledge_index_size"],
                })
    
    # Final stats
    final_stats = system.get_stats()
    results["final"] = {
        "total_queries": final_stats["total_queries"],
        "fast_path_hits": final_stats["fast_path_hits"],
        "hit_rate_pct": final_stats["fast_path_hits"] / final_stats["total_queries"] * 100,
        "knowledge_size": final_stats["knowledge_index_size"],
    }
    
    print()
    print(f"✅ Final hit rate: {results['final']['hit_rate_pct']:.1f}%")
    print(f"   Knowledge patterns learned: {results['final']['knowledge_size']}")
    
    # Save results
    with open(RESULTS_DIR / "test1_fast_path_efficiency.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def test_2_response_time_comparison(num_queries=20):
    """
    Test 2: Response Time Comparison
    
    Compares fast path vs slow path latency.
    """
    print()
    print("=" * 70)
    print("TEST 2: Response Time Comparison")
    print("=" * 70)
    print(f"Running {num_queries} queries, measuring latency...")
    print()
    
    system = create_erla_system()
    
    results = {
        "test": "response_time_comparison",
        "timestamp": datetime.now().isoformat(),
        "fast_path_times_ms": [],
        "slow_path_times_ms": [],
    }
    
    # First pass - all slow path (learning)
    print("  Phase 1: Learning (slow path)...")
    for i in range(num_queries // 2):
        query, _ = generate_query(i % len(BASE_QUERIES))
        start = time.time()
        result = system.process_task({"query": query})
        elapsed = (time.time() - start) * 1000
        
        if result["path"] == "slow":
            results["slow_path_times_ms"].append(elapsed)
    
    # Second pass - should hit fast path more often
    print("  Phase 2: Retrieval (mixed path)...")
    for i in range(num_queries // 2):
        query, _ = generate_query(i % len(BASE_QUERIES))
        start = time.time()
        result = system.process_task({"query": query})
        elapsed = (time.time() - start) * 1000
        
        if result["path"] == "fast":
            results["fast_path_times_ms"].append(elapsed)
        else:
            results["slow_path_times_ms"].append(elapsed)
    
    # Calculate stats
    if results["fast_path_times_ms"]:
        results["fast_path_avg_ms"] = sum(results["fast_path_times_ms"]) / len(results["fast_path_times_ms"])
    else:
        results["fast_path_avg_ms"] = 0
    
    if results["slow_path_times_ms"]:
        results["slow_path_avg_ms"] = sum(results["slow_path_times_ms"]) / len(results["slow_path_times_ms"])
    else:
        results["slow_path_avg_ms"] = 0
    
    if results["fast_path_avg_ms"] > 0:
        results["speedup_factor"] = results["slow_path_avg_ms"] / results["fast_path_avg_ms"]
    else:
        results["speedup_factor"] = 0
    
    print()
    print(f"✅ Fast path avg: {results['fast_path_avg_ms']:.2f} ms")
    print(f"   Slow path avg: {results['slow_path_avg_ms']:.2f} ms")
    print(f"   Speedup: {results['speedup_factor']:.1f}x")
    
    # Save results
    with open(RESULTS_DIR / "test2_response_time.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def test_3_memory_usage(num_queries=50):
    """
    Test 3: Memory/Resource Usage
    
    Verifies that ephemeral agents don't leak memory.
    """
    print()
    print("=" * 70)
    print("TEST 3: Memory/Resource Usage")
    print("=" * 70)
    print(f"Running {num_queries} queries, tracking memory...")
    print()
    
    # Start memory tracking
    tracemalloc.start()
    
    system = create_erla_system()
    
    results = {
        "test": "memory_usage",
        "timestamp": datetime.now().isoformat(),
        "measurements": [],
    }
    
    # Get baseline
    baseline = tracemalloc.get_traced_memory()
    results["baseline_mb"] = baseline[0] / 1024 / 1024
    
    for i in range(1, num_queries + 1):
        query, _ = generate_query()
        system.process_task({"query": query})
        
        if i % 10 == 0:
            current, peak = tracemalloc.get_traced_memory()
            results["measurements"].append({
                "query_count": i,
                "current_mb": current / 1024 / 1024,
                "peak_mb": peak / 1024 / 1024,
            })
            print(f"  Query {i}: Current = {current/1024/1024:.2f} MB, Peak = {peak/1024/1024:.2f} MB")
    
    # Final measurement
    final_current, final_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    results["final_mb"] = final_current / 1024 / 1024
    results["peak_mb"] = final_peak / 1024 / 1024
    results["growth_mb"] = results["final_mb"] - results["baseline_mb"]
    results["growth_per_query_kb"] = (results["growth_mb"] * 1024) / num_queries
    
    print()
    print(f"✅ Baseline: {results['baseline_mb']:.2f} MB")
    print(f"   Final: {results['final_mb']:.2f} MB")
    print(f"   Peak: {results['peak_mb']:.2f} MB")
    print(f"   Growth per query: {results['growth_per_query_kb']:.2f} KB")
    
    # Save results
    with open(RESULTS_DIR / "test3_memory_usage.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def test_4_knowledge_retention():
    """
    Test 4: Knowledge Retention
    
    Verifies that knowledge persists across system restarts.
    """
    print()
    print("=" * 70)
    print("TEST 4: Knowledge Retention (Persistence)")
    print("=" * 70)
    print()
    
    results = {
        "test": "knowledge_retention",
        "timestamp": datetime.now().isoformat(),
    }
    
    # Phase 1: Create system and learn
    print("  Phase 1: Learning...")
    system1 = create_erla_system()
    
    training_queries = [
        "LuLu firewall blocked ruby connecting to 192.168.1.50",
        "C2 beacon detected with 60 second intervals",
        "SQL injection attempt in login form",
    ]
    
    for q in training_queries:
        system1.process_task({"query": q})
    
    results["learned_patterns"] = system1.knowledge.size()
    print(f"   Learned {results['learned_patterns']} patterns")
    
    # Save knowledge index
    index_path = RESULTS_DIR / "test4_knowledge_index.json"
    system1.knowledge.save(str(index_path))
    print(f"   Saved to {index_path}")
    
    # Phase 2: Create new system and load
    print("  Phase 2: Loading into new system...")
    system2 = create_erla_system()
    system2.knowledge.load(str(index_path))
    
    results["loaded_patterns"] = system2.knowledge.size()
    print(f"   Loaded {results['loaded_patterns']} patterns")
    
    # Phase 3: Test fast path works
    print("  Phase 3: Testing fast path on loaded knowledge...")
    test_queries = [
        "LuLu blocked python making outbound connection",  # Similar to #1
        "Seeing beaconing behavior every minute",  # Similar to #2
    ]
    
    fast_hits = 0
    for q in test_queries:
        result = system2.process_task({"query": q})
        if result["path"] == "fast":
            fast_hits += 1
    
    results["fast_path_hits_after_load"] = fast_hits
    results["retention_success"] = results["loaded_patterns"] == results["learned_patterns"]
    
    print()
    print(f"✅ Patterns retained: {results['loaded_patterns']}/{results['learned_patterns']}")
    print(f"   Fast path hits after reload: {fast_hits}/{len(test_queries)}")
    print(f"   Retention test: {'PASSED' if results['retention_success'] else 'FAILED'}")
    
    # Save results
    with open(RESULTS_DIR / "test4_knowledge_retention.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def test_5_privacy_verification():
    """
    Test 5: Privacy Verification
    
    Verifies that raw PII doesn't persist in knowledge index.
    """
    print()
    print("=" * 70)
    print("TEST 5: Privacy Verification (No PII Leakage)")
    print("=" * 70)
    print()
    
    results = {
        "test": "privacy_verification",
        "timestamp": datetime.now().isoformat(),
        "pii_items_tested": [],
        "pii_found_in_index": [],
    }
    
    # Test PII items
    pii_items = [
        ("email", "john.doe@secretcorp.com"),
        ("ip", "192.168.100.55"),
        ("ssn", "123-45-6789"),
        ("phone", "555-123-4567"),
        ("name", "John Doe"),
        ("domain", "internal.secretcorp.com"),
    ]
    
    system = create_erla_system()
    
    # Queries containing PII
    print("  Phase 1: Processing queries with PII...")
    queries_with_pii = [
        f"Alert: user john.doe@secretcorp.com failed login from 192.168.100.55",
        f"Suspicious connection from internal.secretcorp.com to external IP",
        f"Process accessed file containing SSN 123-45-6789",
        f"Call from 555-123-4567 triggered security alert",
    ]
    
    for q in queries_with_pii:
        system.process_task({"query": q})
    
    # Check knowledge index for raw PII
    print("  Phase 2: Scanning knowledge index for PII...")
    
    # Get all text from knowledge index
    index_text = ""
    for entry in system.knowledge.entries:
        index_text += entry["text"].lower() + " "
        index_text += str(entry["learning"].to_dict()).lower() + " "
    
    for pii_type, pii_value in pii_items:
        results["pii_items_tested"].append({"type": pii_type, "value": pii_value})
        
        if pii_value.lower() in index_text:
            results["pii_found_in_index"].append({"type": pii_type, "value": pii_value})
            print(f"   ⚠️  FOUND: {pii_type} = {pii_value}")
        else:
            print(f"   ✅ Safe: {pii_type} not in index")
    
    results["pii_leaked"] = len(results["pii_found_in_index"])
    results["privacy_test_passed"] = results["pii_leaked"] == 0
    
    print()
    print(f"✅ PII items tested: {len(pii_items)}")
    print(f"   PII leaked to index: {results['pii_leaked']}")
    print(f"   Privacy test: {'PASSED' if results['privacy_test_passed'] else 'FAILED'}")
    
    # Save results
    with open(RESULTS_DIR / "test5_privacy_verification.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def test_6_scalability_simulation(max_concurrent=10):
    """
    Test 6: Scalability Simulation
    
    Measures resource efficiency of ephemeral agents.
    Key metric: memory per concurrent agent should be constant (not growing).
    
    Note: Python's GIL limits threading throughput, but the key insight
    is that ERLA agents are stateless and can scale horizontally in
    production (serverless, Kubernetes, etc.)
    """
    print()
    print("=" * 70)
    print("TEST 6: Scalability Simulation")
    print("=" * 70)
    print(f"Measuring resource efficiency with up to {max_concurrent} simulated agents...")
    print()
    
    results = {
        "test": "scalability_simulation",
        "timestamp": datetime.now().isoformat(),
        "measurements": [],
        "note": "Python GIL limits threading; real scaling is horizontal (serverless)"
    }
    
    # Test 1: Sequential baseline
    print("  Phase 1: Sequential baseline...")
    system = create_erla_system()
    
    tracemalloc.start()
    baseline_start = time.time()
    
    for _ in range(20):
        query, _ = generate_query()
        system.process_task({"query": query})
    
    baseline_time = time.time() - baseline_start
    baseline_mem = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    
    results["baseline"] = {
        "queries": 20,
        "time_s": baseline_time,
        "qps": 20 / baseline_time,
        "memory_mb": baseline_mem / 1024 / 1024,
    }
    print(f"     20 queries: {results['baseline']['qps']:.1f} q/s, {results['baseline']['memory_mb']:.2f} MB")
    
    # Test 2: Measure memory per agent (simulate N independent agents)
    print("  Phase 2: Memory per agent test...")
    
    agent_counts = [1, 5, 10, 20]
    
    for n_agents in agent_counts:
        tracemalloc.start()
        
        # Create N independent systems (simulates N serverless instances)
        systems = [create_erla_system() for _ in range(n_agents)]
        
        # Each processes one query
        for sys in systems:
            query, _ = generate_query()
            sys.process_task({"query": query})
        
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        mem_per_agent = peak_mem / n_agents / 1024  # KB per agent
        
        results["measurements"].append({
            "agents": n_agents,
            "total_memory_mb": peak_mem / 1024 / 1024,
            "memory_per_agent_kb": mem_per_agent,
        })
        
        print(f"     {n_agents} agents: {peak_mem/1024/1024:.2f} MB total, {mem_per_agent:.1f} KB/agent")
        
        # Clean up
        del systems
    
    # Test 3: Shared knowledge index efficiency
    print("  Phase 3: Shared knowledge index efficiency...")
    
    system = create_erla_system()
    
    # Process 50 queries, measure knowledge index growth
    tracemalloc.start()
    
    for i in range(50):
        query, _ = generate_query()
        system.process_task({"query": query})
    
    final_mem = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    
    knowledge_size = system.knowledge.size()
    mem_per_pattern = (final_mem / knowledge_size / 1024) if knowledge_size > 0 else 0
    
    results["knowledge_efficiency"] = {
        "patterns_learned": knowledge_size,
        "total_memory_kb": final_mem / 1024,
        "memory_per_pattern_kb": mem_per_pattern,
    }
    
    print(f"     {knowledge_size} patterns: {mem_per_pattern:.2f} KB/pattern")
    
    # Calculate key metrics
    if len(results["measurements"]) >= 2:
        first = results["measurements"][0]
        last = results["measurements"][-1]
        
        # Memory should scale linearly (not exponentially)
        expected_linear = first["memory_per_agent_kb"] * last["agents"] / first["agents"]
        actual = last["memory_per_agent_kb"]
        
        # If actual is close to or less than expected, scaling is good
        results["memory_efficiency"] = actual / first["memory_per_agent_kb"]
        results["scales_linearly"] = results["memory_efficiency"] <= 1.5  # Allow 50% overhead
    
    print()
    print(f"✅ Memory efficiency: {results.get('memory_efficiency', 0):.2f}x (1.0 = perfect linear)")
    print(f"   Scales linearly: {'YES' if results.get('scales_linearly', False) else 'NO'}")
    print(f"   Knowledge index: {mem_per_pattern:.2f} KB/pattern")
    
    # Save results
    with open(RESULTS_DIR / "test6_scalability.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def generate_summary(all_results):
    """Generate a summary report of all tests."""
    print()
    print("=" * 70)
    print("📊 ACADEMIC TEST SUMMARY")
    print("=" * 70)
    print()
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
    }
    
    # Test 1
    if "fast_path_efficiency" in all_results:
        r = all_results["fast_path_efficiency"]
        summary["tests"]["fast_path_efficiency"] = {
            "final_hit_rate": f"{r['final']['hit_rate_pct']:.1f}%",
            "knowledge_learned": r["final"]["knowledge_size"],
        }
        print(f"1. Fast Path Efficiency: {r['final']['hit_rate_pct']:.1f}% hit rate")
    
    # Test 2
    if "response_time_comparison" in all_results:
        r = all_results["response_time_comparison"]
        summary["tests"]["response_time"] = {
            "fast_path_ms": f"{r['fast_path_avg_ms']:.2f}",
            "slow_path_ms": f"{r['slow_path_avg_ms']:.2f}",
            "speedup": f"{r['speedup_factor']:.1f}x",
        }
        print(f"2. Response Time: {r['speedup_factor']:.1f}x speedup (fast vs slow)")
    
    # Test 3
    if "memory_usage" in all_results:
        r = all_results["memory_usage"]
        summary["tests"]["memory_usage"] = {
            "growth_per_query_kb": f"{r['growth_per_query_kb']:.2f}",
            "peak_mb": f"{r['peak_mb']:.2f}",
        }
        print(f"3. Memory Usage: {r['growth_per_query_kb']:.2f} KB/query growth")
    
    # Test 4
    if "knowledge_retention" in all_results:
        r = all_results["knowledge_retention"]
        summary["tests"]["knowledge_retention"] = {
            "passed": r["retention_success"],
            "patterns_retained": f"{r['loaded_patterns']}/{r['learned_patterns']}",
        }
        print(f"4. Knowledge Retention: {'PASSED' if r['retention_success'] else 'FAILED'}")
    
    # Test 5
    if "privacy_verification" in all_results:
        r = all_results["privacy_verification"]
        summary["tests"]["privacy"] = {
            "passed": r["privacy_test_passed"],
            "pii_leaked": r["pii_leaked"],
        }
        print(f"5. Privacy Verification: {'PASSED' if r['privacy_test_passed'] else 'FAILED'}")
    
    # Test 6
    if "scalability_simulation" in all_results:
        r = all_results["scalability_simulation"]
        summary["tests"]["scalability"] = {
            "memory_efficiency": f"{r.get('memory_efficiency', 0):.2f}x",
            "scales_linearly": r.get("scales_linearly", False),
            "kb_per_pattern": f"{r.get('knowledge_efficiency', {}).get('memory_per_pattern_kb', 0):.2f}",
        }
        print(f"6. Scalability: {'PASSED' if r.get('scales_linearly', False) else 'NEEDS WORK'} (memory efficiency: {r.get('memory_efficiency', 0):.2f}x)")
    
    print()
    
    # Save summary
    with open(RESULTS_DIR / "test_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"📁 Results saved to: {RESULTS_DIR}")
    
    return summary


def run_all_tests():
    """Run all academic tests in sequence."""
    print("=" * 70)
    print("🧪 ERLA ACADEMIC TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    all_results = {}
    
    # Run tests
    all_results["fast_path_efficiency"] = test_1_fast_path_efficiency(num_queries=50)
    all_results["response_time_comparison"] = test_2_response_time_comparison(num_queries=20)
    all_results["memory_usage"] = test_3_memory_usage(num_queries=50)
    all_results["knowledge_retention"] = test_4_knowledge_retention()
    all_results["privacy_verification"] = test_5_privacy_verification()
    all_results["scalability_simulation"] = test_6_scalability_simulation(max_concurrent=10)
    
    # Generate summary
    summary = generate_summary(all_results)
    
    print()
    print("=" * 70)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 70)
    
    return all_results, summary


if __name__ == "__main__":
    run_all_tests()
