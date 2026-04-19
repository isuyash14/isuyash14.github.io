import re

html_top = """    <div class="section-header">
      <div>
        <div class="eyebrow">/ DEEP DIVE</div>
        <div class="section-title">THEORY QUESTIONS</div>
      </div>
      <div class="section-count">10 CORE CONCEPTS</div>
    </div>

    <!-- THEORY ACCORDION -->
    <div class="questions-accordion">"""

theory_qs = [
    {
        "meta": "SYS DESIGN ★★★★★ · ANTHROPIC",
        "title": "ML INFRA, LLM PIPELINES, DATA DRIFT",
        "prompt": '"Design a data pipeline to ingest 10TB of training data daily for an LLM..."',
        "hint": "",
        "companies": "",
        "bullets": [
            "Data Lake Storage: Land raw JSON/text data in S3/GCS using an object storage tier optimized for high throughput.",
            "Compute Engine: Use Apache Spark or Ray clusters to process and tokenize the 10TB of text in parallel.",
            "Quality Filters: Implement deduplication via MinHash, PII scrubbing, and heuristic quality filtering at the partition level.",
            "Orchestration: Schedule the DAG daily using Apache Airflow, triggering streaming/batch ingest jobs."
        ]
    },
    {
        "meta": "CODING ★★★★★ · OPENAI",
        "title": "RELIABILITY, IDEMPOTENCY, HEAPS/GRAPHS",
        "prompt": '"Design a system that can re-run ML training pipelines idempotently after a crash."',
        "hint": "",
        "companies": "",
        "bullets": [
            "State Management: Persist pipeline state and checkpoints externally to an object store (S3) at the end of each epoch.",
            "Idempotent Writes: Ensure all intermediate writing tasks use atomic commits (e.g., uploading to a temporary directory and renaming).",
            "Deterministic Data Loading: Seed random number generators and use consistent hash-based partitioning across nodes.",
            "Orchestrator Tracking: Use a metadata store like MLflow to track run lineage and resume exactly from the last successful checkpoint."
        ]
    },
    {
        "meta": "RELIABILITY ★★★★★ · STRIPE",
        "title": "CDC, CONSISTENCY, DIST. ALGO",
        "prompt": '"Idempotency is the #1 keyword. Know exactly-once processing for ledgers."',
        "hint": "",
        "companies": "",
        "bullets": [
            "Unique Constraints: Use unique idempotency keys in the database schema (e.g., transaction_id + event_type).",
            "Append-Only Logs: Implement an Event Sourcing pattern where updates are appended to an immutable ledger (Kafka).",
            "Transaction Boundaries: Wrap consumer updates in atomic DB transactions. If an event is re-delivered, the constraint prevents duplicates.",
            "Two-Phase Commits: Use exactly-once semantics in streaming frameworks like Flink to coordinate offsets and sinks."
        ]
    },
    {
        "meta": "SQL ★★★★★ · AIRBNB",
        "title": "WINDOW FX, EXPERIMENTATION, METRICS",
        "prompt": '"Most SQL-heavy DE interview. Know LAG/LEAD and percentile functions."',
        "hint": "",
        "companies": "",
        "bullets": [
            "Window Functions: Extensively use LAG/LEAD for finding consecutive days, gaps, and islands in user session data.",
            "Percentiles: Use PERCENTILE_CONT or APPROX_PERCENTILE within window frames to calculate median response times.",
            "Self-Joins: Optimize overlapping time conditions using range-based joins if window functions cannot express the bounding logic.",
            "Execution Plans: Understand how window functions trigger sorts in the query planner, and optimize via appropriate clustered indexes."
        ]
    },
    {
        "meta": "Data Pipelines · Senior",
        "title": "Design a Real-Time Feature Store",
        "prompt": "Design a system that serves ML features in real-time (< 10ms latency) for a model serving 100k RPS. Also supports batch feature backfilling.",
        "hint": "Use Redis/DynamoDB for latency, and Kafka for streaming ingestion.",
        "companies": "Anthropic, OpenAI, Databricks",
        "bullets": [
            "Streaming Ingestion: Kafka topics ingest live streaming event data. Apache Flink consumes these topics to compute real-time feature aggregations (e.g., rolling 5-minute sums).",
            "Online Serving Layer: Flink sinks write directly to an extremely low-latency Key-Value store (Redis/DynamoDB). This tier handles the live 100k RPS queries guaranteeing <10ms P99 retrieval.",
            "Offline Storage Layer: A Data Lakehouse (S3 + Iceberg) persists the complete historical timeline. Spark handles batch pipelines to calculate heavy offline features.",
            "State Synchronization: During backfills, batch jobs push to offline storage but also bootstrap the online KV store via bulk load APIs, without blocking real-time updates."
        ]
    },
    {
        "meta": "Streaming · Senior",
        "title": "Design a Real-Time Fraud Detection Pipeline",
        "prompt": "Design a streaming data pipeline to detect fraudulent transactions in real-time (< 1 second) at Stripe's scale (millions of transactions/day).",
        "hint": "Push events to Kafka, process with Flink, and query rules against a fast KV store.",
        "companies": "Stripe, Coinbase, Robinhood",
        "bullets": [
            "Event Ingestion: Route raw transaction payloads into Kafka partitions keyed by user_id for ordered processing.",
            "Stream Processing: Flink consumes events, querying rapid rule sets and historical aggregations (e.g. transactions per hour).",
            "State Backend: Use RocksDB within Flink to hold enormous user time-window states locally without network roundtrips.",
            "Low Latency Lookups: Query external ML features simultaneously from Redis if additional pre-computed risk embeddings are needed."
        ]
    },
    {
        "meta": "Data Lakehouse · Staff",
        "title": "Design a Petabyte-Scale Analytics Platform",
        "prompt": "You are asked to build a new analytics platform for a company with 500TB of data today, growing to 10PB. Design the storage, compute, and query layer.",
        "hint": "Use decoupled storage (S3/Iceberg) and compute (Trino/Spark).",
        "companies": "Databricks, Snowflake, Airbnb",
        "bullets": [
            "Storage Layer: Centralize structured and semi-structured payloads in AWS S3 or GCS using Parquet format.",
            "Table Format: Adopt Apache Iceberg or Delta Lake to afford ACID transactions, schema evolution, and time-travel querying.",
            "Compute Separation: Provision separate compute clusters (Spark for ETL heavy lifting, Trino/Presto for ad-hoc BI queries).",
            "Partitioning Strategy: Partition data temporally (by date/hour) to heavily prune files during reporting scans."
        ]
    },
    {
        "meta": "Data Quality · Mid",
        "title": "Design a Data Observability System",
        "prompt": "Design a system that automatically detects data quality issues (missing data, schema drift, outliers) across 500 production pipelines and alerts owners.",
        "hint": "Implement statistical checks and Great Expectations validations triggered via Airflow operators.",
        "companies": "Palantir, Confluent, Cloudflare",
        "bullets": [
            "Metadata Extraction: Use sensors (e.g., Monte Carlo) connected to warehouse logs to extract automated table metrics.",
            "Statistical Profiling: Run statistical models over standard deviations of row counts to detect volume anomalies.",
            "Schema Drift: Capture table schemas dynamically and alert on dropped columns or type changes via Slack/PagerDuty hooks.",
            "Circuit Breakers: Integrate Great Expectations checks inside the Airflow DAG to halt downstream processing upon failure."
        ]
    },
    {
        "meta": "Streaming · Senior",
        "title": "Design a CDC (Change Data Capture) Pipeline",
        "prompt": "Design a system to replicate changes from a PostgreSQL OLTP database (1M writes/day) to a data warehouse in near-real-time (<5 min lag), handling schema evolution gracefully.",
        "hint": "Debezium connector on Postgres WAL writing to Kafka, then sink down to Snowflake.",
        "companies": "Stripe, Airbnb, Confluent",
        "bullets": [
            "Log Mining: Use Debezium to hook into Postgres Logical Replication (WAL) to extract row-level changes with minimal OLTP overhead.",
            "Message Bus: Debezium streams CDC payloads (Insert, Update, Delete) into Kafka topics mapped per table.",
            "Schema Evolution: Use Confluent Schema Registry to enforce Avro schemas and map changes safely downstream.",
            "Sinking: A Kafka Connect Snowflake sink consumes the CDC feed and merges it into target tables via micro-batches."
        ]
    },
    {
        "meta": "Cost Optimization · Staff",
        "title": "Reduce Cloud Data Warehouse Costs by 60%",
        "prompt": "Your Snowflake bill is $2M/month and growing. Walk through your investigation and optimization approach.",
        "hint": "Analyze query history for un-clustered scans, check auto-suspend timing, right-size warehouses, and flag non-incremental dbt materializations.",
        "companies": "Snowflake, Airbnb, DoorDash",
        "bullets": [
             "Account Usage: Query the SNOWFLAKE.ACCOUNT_USAGE schema to identify the most expensive warehouses and longest-running queries.",
             "Auto-Suspend Tuning: Reduce the auto-suspend threshold on warehouses to 60 seconds to cut down idle credit drain.",
             "Materialization Efficiency: Convert full-refresh dbt models into incremental models where historical data is immutable.",
             "Clustering: Implement a cluster key on heavily scanned massive tables to enhance partition pruning and reduce micro-partition scans."
        ]
    }
]

coding_qs = [
    {
        "meta": "Arrays · Medium",
        "title": "Sliding Window — Max Sum Subarray of Size K",
        "prompt": "Given an array of integers and a number k, find the maximum sum of a subarray of size k.",
        "hint": "Use a sliding window: add the next element, subtract the last element, track the max.",
        "companies": "Google, Stripe, OpenAI",
        "bullets": [
             "Initialization: Compute the sum of the first k elements and store it as the initial maximum window sum.",
             "Sliding Mechanism: For element i from k to the end of the array, add the new element and subtract the element at i-k.",
             "Tracking: Compare the newly computed window sum against the global maximum and update if larger.",
             "Time Complexity: This approach evaluates in strict O(n) time and O(1) space, as it passes through the array exactly once."
        ]
    },
    {
        "meta": "Hash Maps · Medium",
        "title": "Two Sum / Group Anagrams",
        "prompt": "Given a list of strings, group all anagrams together.",
        "hint": "Sort each string as a key in a hashmap — anagrams will share the same sorted key.",
        "companies": "Airbnb, Databricks",
        "bullets": [
             "Key Generation: For each string, sort its characters alphabetically to generate a standard signature (e.g., eat -> aet).",
             "Dictionary Mapping: Use a Hash Map where the sorted signature is the key, and the value is a list of the original strings.",
             "Alternative Keying: To avoid the O(K log K) string sort, create a 26-element character frequency array and cast it to a tuple as the dict key.",
             "Time Complexity: Sorting takes O(N * K log K). The character array approach drops this to O(N * K)."
        ]
    },
    {
        "meta": "Graphs · Hard",
        "title": "Task Scheduler / Topological Sort",
        "prompt": "Given a list of tasks and their prerequisites, find a valid execution order (or detect a cycle).",
        "hint": "Use Kahn's algorithm (BFS-based topological sort). Track in-degrees.",
        "companies": "Anthropic, Palantir, Stripe",
        "bullets": [
             "Graph Construction: Build an adjacency list to represent prerequisites as directed edges, and an array to track in-degrees for each node.",
             "Queue Initialization: Identify all nodes (tasks) with an in-degree of 0 (no prerequisites) and push them onto a queue.",
             "BFS Traversal: Pop a node, append to the sorted list, and decrement the in-degree of its neighbors. If a neighbor reaches 0, enqueue it.",
             "Cycle Detection: If the processed node count equals the total tasks, return the order. Otherwise, a cycle exists (return empty or error)."
        ]
    },
    {
        "meta": "Recursion / DP · Easy",
        "title": "Fibonacci with Memoization",
        "prompt": "Implement Fibonacci using recursion, then optimize with memoization, then with DP.",
        "hint": "Cache results in a dict (top-down). Then build bottom-up to eliminate the call stack.",
        "companies": "Meta, Amazon",
        "bullets": [
             "Naive Recursion: Base case if n <= 1 return n. Else return fib(n-1) + fib(n-2). Pathological O(2^n) time.",
             "Top-Down Memoization: Pass a dictionary/array into the recursion. Store computed results. Drops time to O(N) by preventing duplicate sub-trees.",
             "Bottom-Up DP: Use a loop from 2 to N, maintaining an array of solutions. Time is O(N), Space is O(N).",
             "Constant Space DP: Realize we only need the last two variables. Track a and b. Swap them. Drops Space to strict O(1)."
        ]
    },
    {
        "meta": "Heaps · Hard",
        "title": "Top K Frequent Elements",
        "prompt": "Given an array, return the k most frequent elements.",
        "hint": "Use a min-heap of size k. Or bucket sort by frequency for O(n) solution.",
        "companies": "Databricks, Confluent, Stripe",
        "bullets": [
             "Hash Map Counting: First pass, iterate through the array compiling a frequency map of value -> count. O(N).",
             "Min-Heap Approach: Push keys into a priority queue/min-heap based on frequency. Maintain size K. Total time O(N log K).",
             "Bucket Sort Optimization: Create an array of lists buckets where the index is the frequency. Time drops to strict O(N).",
             "Extraction: Iterate the buckets backwards (from max possible frequency N down to 1), appending items until K is reached."
        ]
    }
]

def build_q(q):
    html = f"""      <details class="q-detail">
        <summary class="q-summary">
          <div class="q-meta">{q['meta']}</div>
          <div class="q-title">{q['title']}</div>
        </summary>
        <div class="q-answer">
          <p><strong>Prompt:</strong> {q['prompt']}</p>"""
          
    if q.get('hint'):
        html += f"""\n          <p><strong>Hint:</strong> {q['hint']}</p>"""
    if q.get('companies'):
        html += f"""\n          <p class="q-companies"><strong>Tagged at:</strong> {q['companies']}</p>"""
        
    html += f"""
          <details style="margin-top: 1.5rem; background: rgba(0,0,0,0.2); border: 1px solid var(--border); padding: 1rem; border-left: 2px solid var(--amber);">
            <summary style="font-family: 'Open Sans', sans-serif; font-size: 0.95rem; font-weight: normal; color: var(--amber); cursor: pointer; outline: none; list-style: none; display: flex; align-items: center; gap: 0.5rem;">
              ▶ Show expert answer
            </summary>
            <div style="margin-top: 1rem;">
              <ul style="padding-left: 1.25rem; margin-bottom: 0;">\n"""
              
    for b in q['bullets']:
        html += f"""                <li style="margin-bottom: .75rem;">{b}</li>\n"""
        
    html += """              </ul>
            </div>
          </details>
        </div>
      </details>\n"""
    return html

html_mid = """    </div>

    <a href="#" style="display:block; margin-top:1rem; font-family:'IBM Plex Mono'; font-size:.65rem; color:var(--blue-lt); text-decoration:none; text-align:right; letter-spacing:.05em;">SEE MORE THEORY CONCEPTS →</a>

    <div class="section-header" style="margin-top: 3rem;">
      <div>
        <div class="eyebrow">/ DAILY DRILLS</div>
        <div class="section-title">DAILY INTERVIEW QUESTIONS</div>
      </div>
      <div class="section-count">5 ACTIVE QUESTIONS</div>
    </div>

    <!-- CODING ACCORDION -->
    <div class="questions-accordion">\n"""

html_bot = """    </div>
    
    <a href="#" style="display:block; margin-top:1rem; font-family:'IBM Plex Mono'; font-size:.65rem; color:var(--blue-lt); text-decoration:none; text-align:right; letter-spacing:.05em;">SEE ALL CODING DRILLS →</a>
"""

final = html_top + "\n"
for q in theory_qs:
    final += build_q(q)

final += html_mid
for q in coding_qs:
    final += build_q(q)

final += html_bot


with open("intel.html", "r") as f:
    text = f.read()
    
# Extract bounds 
start_idx = text.find('<div class="section-header">\n      <div>\n        <div class="eyebrow">/ DEEP DIVE</div>')
end_idx = text.find('<!-- TOPIC HEATMAP -->')

if start_idx != -1 and end_idx != -1:
    with open("intel.html", "w") as f:
        f.write(text[:start_idx] + final + "\n    " + text[end_idx:])
    print("SUCCESS")
else:
    print("FAILED TO FIND BOUNDS")
