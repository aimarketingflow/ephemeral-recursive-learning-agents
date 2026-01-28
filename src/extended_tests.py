#!/usr/bin/env python3
"""
ERLA Extended Test Suite - Large Scale Testing

Runs 500+ queries to generate robust statistical data for publication.

Author: Hana Omori
Date: January 27, 2026
"""

import sys
import os
import time
import json
import random
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erla import create_erla_system

# Output directory
RESULTS_DIR = Path(__file__).parent.parent / "test_results" / "extended"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Query templates (security domain)
TEMPLATES = [
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
    "Suspicious cron job added by {process}",
    "Unauthorized SSH key added to {user} account",
    "Binary {process} has modified system files",
    "Network scan detected from {ip} targeting port {port}",
    "Privilege escalation attempt detected from {process}",
]

PROCESSES = ["ruby", "python", "node", "chrome", "firefox", "curl", "wget", "nc", "bash", "perl", "java"]
IPS = ["192.168.1.50", "10.0.0.100", "172.16.0.1", "8.8.8.8", "1.1.1.1", "203.0.113.50", "198.51.100.25"]
PORTS = ["443", "80", "8080", "22", "53", "4444", "3389", "445", "139"]
DOMAINS = ["suspicious.com", "malware.net", "c2server.io", "legit.com", "update.microsoft.com", "cdn.example.org"]
PAYLOADS = ["1' OR '1'='1", "admin'--", "UNION SELECT", "<script>alert(1)</script>", "'; DROP TABLE users;--"]
INTERVALS = ["30", "60", "120", "300", "600"]
COMPONENTS = ["AppleMobileDispH13G", "IOKit", "kernel_task", "WindowServer", "mds_stores"]
MALWARE_TYPES = ["credential harvesting", "keylogger", "ransomware", "rootkit", "backdoor", "cryptominer"]
USERS = ["root", "admin", "www-data", "nobody", "daemon"]


def generate_query(template_idx=None):
    """Generate a query from templates."""
    if template_idx is None:
        template_idx = random.randint(0, len(TEMPLATES) - 1)
    
    template = TEMPLATES[template_idx % len(TEMPLATES)]
    
    query = template.format(
        process=random.choice(PROCESSES),
        ip=random.choice(IPS),
        port=random.choice(PORTS),
        domain=random.choice(DOMAINS),
        payload=random.choice(PAYLOADS),
        interval=random.choice(INTERVALS),
        component=random.choice(COMPONENTS),
        malware_type=random.choice(MALWARE_TYPES),
        user=random.choice(USERS),
    )
    
    return query, template_idx


def run_extended_fast_path_test(num_queries=500):
    """
    Extended Fast Path Efficiency Test
    
    Runs 500 queries and tracks hit rate at fine-grained intervals.
    """
    print("=" * 70)
    print(f"EXTENDED FAST PATH TEST ({num_queries} queries)")
    print("=" * 70)
    print()
    
    system = create_erla_system()
    
    results = {
        "test": "extended_fast_path",
        "timestamp": datetime.now().isoformat(),
        "num_queries": num_queries,
        "data_points": [],  # Every 10 queries
        "per_query": [],    # Every query (for detailed analysis)
    }
    
    fast_hits = 0
    
    for i in range(1, num_queries + 1):
        # Mix of similar and novel queries
        if i > 20 and random.random() < 0.7:
            # 70% chance to reuse a template we've seen
            template_idx = random.randint(0, min(i-1, len(TEMPLATES)-1))
        else:
            template_idx = None
        
        query, tidx = generate_query(template_idx)
        
        start = time.time()
        result = system.process_task({"query": query})
        elapsed = (time.time() - start) * 1000
        
        if result["path"] == "fast":
            fast_hits += 1
        
        # Record every query
        results["per_query"].append({
            "idx": i,
            "path": result["path"],
            "time_ms": round(elapsed, 3),
            "template": tidx,
        })
        
        # Record data point every 10 queries
        if i % 10 == 0:
            hit_rate = fast_hits / i * 100
            results["data_points"].append({
                "query_count": i,
                "fast_hits": fast_hits,
                "hit_rate": round(hit_rate, 2),
                "knowledge_size": system.knowledge.size(),
            })
            
            if i % 50 == 0:
                print(f"  Query {i}: Hit rate = {hit_rate:.1f}%, Knowledge = {system.knowledge.size()}")
    
    # Final stats
    final_stats = system.get_stats()
    results["final"] = {
        "total_queries": num_queries,
        "fast_hits": fast_hits,
        "hit_rate": round(fast_hits / num_queries * 100, 2),
        "knowledge_size": final_stats["knowledge_index_size"],
    }
    
    print()
    print(f"✅ Final: {results['final']['hit_rate']}% hit rate, {results['final']['knowledge_size']} patterns")
    
    # Save
    with open(RESULTS_DIR / "extended_fast_path.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def run_extended_response_time_test(num_queries=200):
    """
    Extended Response Time Test
    
    Collects detailed timing data for fast vs slow path.
    """
    print()
    print("=" * 70)
    print(f"EXTENDED RESPONSE TIME TEST ({num_queries} queries)")
    print("=" * 70)
    print()
    
    system = create_erla_system()
    
    results = {
        "test": "extended_response_time",
        "timestamp": datetime.now().isoformat(),
        "fast_path_times": [],
        "slow_path_times": [],
    }
    
    for i in range(1, num_queries + 1):
        if i > 20 and random.random() < 0.6:
            template_idx = random.randint(0, min(i-1, len(TEMPLATES)-1))
        else:
            template_idx = None
        
        query, _ = generate_query(template_idx)
        
        start = time.time()
        result = system.process_task({"query": query})
        elapsed = (time.time() - start) * 1000
        
        if result["path"] == "fast":
            results["fast_path_times"].append(round(elapsed, 3))
        else:
            results["slow_path_times"].append(round(elapsed, 3))
        
        if i % 50 == 0:
            print(f"  Query {i}: Fast={len(results['fast_path_times'])}, Slow={len(results['slow_path_times'])}")
    
    # Calculate statistics
    def calc_stats(times):
        if not times:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0}
        sorted_times = sorted(times)
        return {
            "count": len(times),
            "avg": round(sum(times) / len(times), 3),
            "min": round(min(times), 3),
            "max": round(max(times), 3),
            "p50": round(sorted_times[len(sorted_times) // 2], 3),
            "p95": round(sorted_times[int(len(sorted_times) * 0.95)], 3),
        }
    
    results["fast_path_stats"] = calc_stats(results["fast_path_times"])
    results["slow_path_stats"] = calc_stats(results["slow_path_times"])
    
    if results["fast_path_stats"]["avg"] > 0:
        results["speedup"] = round(results["slow_path_stats"]["avg"] / results["fast_path_stats"]["avg"], 2)
    else:
        results["speedup"] = 0
    
    print()
    print(f"✅ Fast path: avg={results['fast_path_stats']['avg']}ms, p95={results['fast_path_stats']['p95']}ms")
    print(f"   Slow path: avg={results['slow_path_stats']['avg']}ms, p95={results['slow_path_stats']['p95']}ms")
    print(f"   Speedup: {results['speedup']}x")
    
    # Save
    with open(RESULTS_DIR / "extended_response_time.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def run_extended_scalability_test(max_agents=50):
    """
    Extended Scalability Test
    
    Tests memory efficiency with more agent counts.
    """
    print()
    print("=" * 70)
    print(f"EXTENDED SCALABILITY TEST (up to {max_agents} agents)")
    print("=" * 70)
    print()
    
    import tracemalloc
    
    results = {
        "test": "extended_scalability",
        "timestamp": datetime.now().isoformat(),
        "measurements": [],
    }
    
    agent_counts = [1, 5, 10, 20, 30, 40, 50]
    agent_counts = [n for n in agent_counts if n <= max_agents]
    
    for n in agent_counts:
        tracemalloc.start()
        
        systems = [create_erla_system() for _ in range(n)]
        
        for sys in systems:
            query, _ = generate_query()
            sys.process_task({"query": query})
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        mem_per_agent = peak / n / 1024
        
        results["measurements"].append({
            "agents": n,
            "total_kb": round(peak / 1024, 2),
            "per_agent_kb": round(mem_per_agent, 2),
        })
        
        print(f"  {n} agents: {peak/1024:.1f} KB total, {mem_per_agent:.1f} KB/agent")
        
        del systems
    
    # Calculate efficiency
    if len(results["measurements"]) >= 2:
        first = results["measurements"][0]
        last = results["measurements"][-1]
        results["efficiency_ratio"] = round(last["per_agent_kb"] / first["per_agent_kb"], 3)
    
    print()
    print(f"✅ Memory efficiency: {results.get('efficiency_ratio', 0)}x (lower is better)")
    
    # Save
    with open(RESULTS_DIR / "extended_scalability.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def run_multiple_trials(num_trials=3, queries_per_trial=200):
    """
    Run multiple trials for statistical significance.
    """
    print()
    print("=" * 70)
    print(f"MULTIPLE TRIALS ({num_trials} trials x {queries_per_trial} queries)")
    print("=" * 70)
    print()
    
    results = {
        "test": "multiple_trials",
        "timestamp": datetime.now().isoformat(),
        "num_trials": num_trials,
        "queries_per_trial": queries_per_trial,
        "trials": [],
    }
    
    for trial in range(1, num_trials + 1):
        print(f"  Trial {trial}/{num_trials}...")
        
        system = create_erla_system()
        fast_hits = 0
        
        for i in range(queries_per_trial):
            if i > 20 and random.random() < 0.7:
                template_idx = random.randint(0, min(i, len(TEMPLATES)-1))
            else:
                template_idx = None
            
            query, _ = generate_query(template_idx)
            result = system.process_task({"query": query})
            
            if result["path"] == "fast":
                fast_hits += 1
        
        hit_rate = fast_hits / queries_per_trial * 100
        results["trials"].append({
            "trial": trial,
            "fast_hits": fast_hits,
            "hit_rate": round(hit_rate, 2),
            "knowledge_size": system.knowledge.size(),
        })
        
        print(f"    Hit rate: {hit_rate:.1f}%")
    
    # Calculate mean and std
    hit_rates = [t["hit_rate"] for t in results["trials"]]
    mean_rate = sum(hit_rates) / len(hit_rates)
    variance = sum((r - mean_rate) ** 2 for r in hit_rates) / len(hit_rates)
    std_rate = variance ** 0.5
    
    results["summary"] = {
        "mean_hit_rate": round(mean_rate, 2),
        "std_hit_rate": round(std_rate, 2),
        "min_hit_rate": round(min(hit_rates), 2),
        "max_hit_rate": round(max(hit_rates), 2),
    }
    
    print()
    print(f"✅ Mean hit rate: {mean_rate:.1f}% ± {std_rate:.1f}%")
    
    # Save
    with open(RESULTS_DIR / "multiple_trials.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


def run_all_extended_tests():
    """Run all extended tests."""
    print("=" * 70)
    print("🧪 ERLA EXTENDED TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    all_results = {}
    
    # Run tests
    all_results["fast_path"] = run_extended_fast_path_test(num_queries=500)
    all_results["response_time"] = run_extended_response_time_test(num_queries=200)
    all_results["scalability"] = run_extended_scalability_test(max_agents=50)
    all_results["trials"] = run_multiple_trials(num_trials=5, queries_per_trial=200)
    
    # Summary
    print()
    print("=" * 70)
    print("📊 EXTENDED TEST SUMMARY")
    print("=" * 70)
    print()
    print(f"1. Fast Path: {all_results['fast_path']['final']['hit_rate']}% hit rate (500 queries)")
    print(f"2. Response Time: {all_results['response_time']['speedup']}x speedup")
    print(f"3. Scalability: {all_results['scalability'].get('efficiency_ratio', 0)}x memory efficiency")
    print(f"4. Trials: {all_results['trials']['summary']['mean_hit_rate']}% ± {all_results['trials']['summary']['std_hit_rate']}%")
    print()
    print(f"📁 Results saved to: {RESULTS_DIR}")
    print()
    print("=" * 70)
    print("✅ ALL EXTENDED TESTS COMPLETE")
    print("=" * 70)
    
    return all_results


if __name__ == "__main__":
    run_all_extended_tests()
