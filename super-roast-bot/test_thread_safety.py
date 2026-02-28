"""
Thread-Safety Test Suite for RoastBot RAG Module
Tests concurrent access to FAISS index and embedding model
"""

import sys
import os

import concurrent.futures
import threading
import time
from rag import retrieve_context

def test_concurrent_retrieval():
    """Test that concurrent queries don't interfere with each other."""
    print("\n[TEST 1] Concurrent Retrieval Test")
    print("=" * 60)
    
    queries = [
        "Python programming",
        "JavaScript errors", 
        "Rust memory safety",
        "Go concurrency",
        "Java garbage collection"
    ]
    
    results = {}
    errors = []
    
    def retrieve_and_store(query):
        try:
            thread_id = threading.current_thread().ident
            result = retrieve_context(query, top_k=2)
            results[thread_id] = (query, result)
            print(f"[OK] Thread {thread_id}: Retrieved context for '{query}'")
            return result
        except Exception as e:
            errors.append((query, str(e)))
            print(f"[ERROR] Thread {thread_id}: Error for '{query}': {e}")
            return None
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(retrieve_and_store, q) for q in queries]
        concurrent.futures.wait(futures)
    
    elapsed = time.time() - start_time
    
    print(f"\n[RESULTS]")
    print(f"   - Queries executed: {len(queries)}")
    print(f"   - Successful: {len(results)}")
    print(f"   - Errors: {len(errors)}")
    print(f"   - Time elapsed: {elapsed:.2f}s")
    
    if errors:
        print(f"\n[FAILED]: {len(errors)} errors occurred")
        for query, error in errors:
            print(f"   - {query}: {error}")
        return False
    
    if len(results) == len(queries):
        print(f"\n[PASSED]: All {len(queries)} concurrent queries succeeded")
        return True
    else:
        print(f"\n[FAILED]: Expected {len(queries)} results, got {len(results)}")
        return False


def test_rapid_sequential_access():
    """Test rapid sequential access from multiple threads."""
    print("\n[TEST 2] Rapid Sequential Access Test")
    print("=" * 60)
    
    num_iterations = 20
    queries = ["coding", "debugging", "testing", "deployment"]
    errors = []
    
    def rapid_queries(thread_num):
        try:
            for i in range(num_iterations):
                query = queries[i % len(queries)]
                result = retrieve_context(query, top_k=1)
                if not result or len(result) == 0:
                    errors.append(f"Thread {thread_num}, iteration {i}: Empty result")
            print(f"[OK] Thread {thread_num}: Completed {num_iterations} queries")
        except Exception as e:
            errors.append(f"Thread {thread_num}: {str(e)}")
            print(f"[ERROR] Thread {thread_num}: Error - {e}")
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(rapid_queries, i) for i in range(3)]
        concurrent.futures.wait(futures)
    
    elapsed = time.time() - start_time
    total_queries = num_iterations * 3
    
    print(f"\n[RESULTS]")
    print(f"   - Total queries: {total_queries}")
    print(f"   - Errors: {len(errors)}")
    print(f"   - Time elapsed: {elapsed:.2f}s")
    print(f"   - Throughput: {total_queries/elapsed:.1f} queries/sec")
    
    if errors:
        print(f"\n[FAILED]: {len(errors)} errors occurred")
        for error in errors[:5]:
            print(f"   - {error}")
        return False
    else:
        print(f"\n[PASSED]: All {total_queries} rapid queries succeeded")
        return True


def test_thread_safety_stress():
    """Stress test with many concurrent threads."""
    print("\n[TEST 3] Thread Safety Stress Test")
    print("=" * 60)
    
    num_threads = 10
    queries_per_thread = 5
    query_templates = [
        "Python", "JavaScript", "Rust", "Go", "Java",
        "C++", "Ruby", "Swift", "Kotlin", "TypeScript"
    ]
    
    success_count = [0]
    error_count = [0]
    lock = threading.Lock()
    
    def stress_worker(worker_id):
        try:
            for i in range(queries_per_thread):
                query = query_templates[worker_id % len(query_templates)]
                result = retrieve_context(query, top_k=1)
                
                with lock:
                    if result and len(result) > 0:
                        success_count[0] += 1
                    else:
                        error_count[0] += 1
                        
        except Exception as e:
            with lock:
                error_count[0] += 1
            print(f"[ERROR] Worker {worker_id}: {e}")
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(stress_worker, i) for i in range(num_threads)]
        concurrent.futures.wait(futures)
    
    elapsed = time.time() - start_time
    total_queries = num_threads * queries_per_thread
    
    print(f"\n[RESULTS]")
    print(f"   - Threads: {num_threads}")
    print(f"   - Total queries: {total_queries}")
    print(f"   - Successful: {success_count[0]}")
    print(f"   - Errors: {error_count[0]}")
    print(f"   - Time elapsed: {elapsed:.2f}s")
    print(f"   - Throughput: {total_queries/elapsed:.1f} queries/sec")
    
    if error_count[0] == 0 and success_count[0] == total_queries:
        print(f"\n[PASSED]: All {total_queries} queries succeeded under stress")
        return True
    else:
        print(f"\n[FAILED]: {error_count[0]} errors out of {total_queries} queries")
        return False


def run_all_tests():
    """Run all thread-safety tests."""
    print("\n" + "=" * 60)
    print("ROASTBOT RAG THREAD-SAFETY TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_concurrent_retrieval,
        test_rapid_sequential_access,
        test_thread_safety_stress,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[CRASHED] Test crashed: {e}")
            results.append(False)
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - Test {i}: {test.__name__}")
    
    print(f"\n{'='*60}")
    print(f"Final Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("*** ALL TESTS PASSED - Thread safety verified! ***")
        print("=" * 60)
        return True
    else:
        print(f"WARNING: {total - passed} test(s) failed")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
