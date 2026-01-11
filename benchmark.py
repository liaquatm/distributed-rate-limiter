import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost/limited"
TOTAL_REQUESTS = 1000
CONCURRENT_USERS = 10

def fetch(url):
    start = time.time()
    try:
        resp = requests.get(url)
        # We don't care if it's 200 (Allowed) or 429 (Limited)
        # We only care how fast the system made the decision!
        resp.close()
    except Exception as e:
        print(f"Error: {e}")
        return None
    end = time.time()
    return (end - start) * 1000  # Convert to milliseconds

print(f"🚀 Starting benchmark: {TOTAL_REQUESTS} requests with {CONCURRENT_USERS} concurrent users...")

latencies = []
with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
    # Submit all tasks
    futures = [executor.submit(fetch, URL) for _ in range(TOTAL_REQUESTS)]
    
    # Gather results
    for future in futures:
        result = future.result()
        if result:
            latencies.append(result)

# Calculate Stats
avg_latency = statistics.mean(latencies)
p99_latency = statistics.quantiles(latencies, n=100)[98] # 99th percentile

print("\n--- 📊 RESULTS ---")
print(f"Total Requests: {len(latencies)}")
print(f"Average Latency: {avg_latency:.2f} ms")
print(f"99th Percentile: {p99_latency:.2f} ms")

if avg_latency < 10:
    print("\n✅ SUCCESS: Sub-10ms latency achieved!")
else:
    print("\n⚠️ WARNING: Latency is too high.")