import re

with open("intel.html", "r") as f:
    text = f.read()

# Change font to Open Sans
text = text.replace("font-family: 'Google Sans', sans-serif;", "font-family: 'Open Sans', sans-serif;")

# We need to find all <div class="q-answer"> blocks that DO NOT already have a <details> inside them.
# A regex to match <div class="q-answer">...</div>
# We can use a simpler approach: replace each specific known prompt with its prompt + the appended details block.

answers_map = {
    '"Design a data pipeline to ingest 10TB of training data daily for an LLM..."': [
        "Data Lake Storage: Land raw JSON/text data in S3/GCS using an object storage tier optimized for high throughput.",
        "Compute Engine: Use Apache Spark or Ray clusters to process and tokenize the 10TB of text in parallel.",
        "Quality Filters: Implement deduplication via MinHash, PII scrubbing, and heuristic quality filtering at the partition level.",
        "Orchestration: Schedule the DAG daily using Apache Airflow, triggering streaming/batch ingest jobs."
    ],
    '"Design a system that can re-run ML training pipelines idempotently after a crash."': [
        "State Management: Persist pipeline state and checkpoints externally to an object store (S3) at the end of each epoch.",
        "Idempotent Writes: Ensure all intermediate writing tasks use atomic commits (e.g., uploading to a temporary directory and renaming).",
        "Deterministic Data Loading: Seed random number generators and use consistent hash-based partitioning across nodes.",
        "Orchestrator Tracking: Use a metadata store like MLflow to track run lineage and resume exactly from the last successful checkpoint."
    ],
    '"Idempotency is the #1 keyword. Know exactly-once processing for ledgers."': [
        "Unique Constraints: Use unique idempotency keys in the database schema (e.g., transaction_id + event_type).",
        "Append-Only Logs: Implement an Event Sourcing pattern where updates are appended to an immutable ledger (Kafka).",
        "Transaction Boundaries: Wrap consumer updates in atomic DB transactions. If an event is re-delivered, the constraint prevents duplicates.",
        "Two-Phase Commits: Use exactly-once semantics in streaming frameworks like Flink to coordinate offsets and sinks."
    ],
    '"Most SQL-heavy DE interview. Know LAG/LEAD and percentile functions."': [
        "Window Functions: Extensively use LAG/LEAD for finding consecutive days, gaps, and islands in user session data.",
        "Percentiles: Use PERCENTILE_CONT or APPROX_PERCENTILE within window frames to calculate median response times.",
        "Self-Joins: Optimize overlapping time conditions using range-based joins if window functions cannot express the bounding logic.",
        "Execution Plans: Understand how window functions trigger sorts in the query planner, and optimize via appropriate clustered indexes."
    ],
    'Design a streaming data pipeline to detect fraudulent transactions in real-time (< 1 second)': [
        "Event Ingestion: Route raw transaction payloads into Kafka partitions keyed by user_id for ordered processing.",
        "Stream Processing: Flink consumes events, querying rapid rule sets and historical aggregations (e.g. transactions per hour).",
        "State Backend: Use RocksDB within Flink to hold enormous user time-window states locally without network roundtrips.",
        "Low Latency Lookups: Query external ML features simultaneously from Redis if additional pre-computed risk embeddings are needed."
    ],
    'You are asked to build a new analytics platform for a company with 500TB of data today, growing to 10PB': [
        "Storage Layer: Centralize structured and semi-structured payloads in AWS S3 or GCS using Parquet format.",
        "Table Format: Adopt Apache Iceberg or Delta Lake to afford ACID transactions, schema evolution, and time-travel querying.",
        "Compute Separation: Provision separate compute clusters (Spark for ETL heavy lifting, Trino/Presto for ad-hoc BI queries).",
        "Partitioning Strategy: Partition data temporally (by date/hour) to heavily prune files during reporting scans."
    ],
    'Design a system that automatically detects data quality issues': [
        "Metadata Extraction: Use sensors (e.g., Monte Carlo) connected to warehouse logs to extract automated table metrics.",
        "Statistical Profiling: Run statistical models over standard deviations of row counts to detect volume anomalies.",
        "Schema Drift: Capture table schemas dynamically and alert on dropped columns or type changes via Slack/PagerDuty hooks.",
        "Circuit Breakers: Integrate Great Expectations checks inside the Airflow DAG to halt downstream processing upon failure."
    ],
    'Design a system to replicate changes from a PostgreSQL OLTP database': [
        "Log Mining: Use Debezium to hook into Postgres Logical Replication (WAL) to extract row-level changes with minimal OLTP overhead.",
        "Message Bus: Debezium streams CDC payloads (Insert, Update, Delete) into Kafka topics mapped per table.",
        "Schema Evolution: Use Confluent Schema Registry to enforce Avro schemas and map changes safely downstream.",
        "Sinking: A Kafka Connect Snowflake sink consumes the CDC feed and merges it into target tables via micro-batches."
    ],
    'Your Snowflake bill is $2M/month and growing. Walk through your investigation': [
        "Account Usage: Query the `SNOWFLAKE.ACCOUNT_USAGE` schema to identify the most expensive warehouses and longest-running queries.",
        "Auto-Suspend Tuning: Reduce the auto-suspend threshold on warehouses to 60 seconds to cut down idle credit drain.",
        "Materialization Efficiency: Convert full-refresh dbt models into incremental models where historical data is immutable.",
        "Clustering: Implement a cluster key on heavily scanned massive tables to enhance partition pruning and reduce micro-partition scans."
    ],
    'Explain the difference between narrow and wide transformations in Spark.': [
        "Narrow Transformations: Operations like map(), filter(), and union() where each child partition depends on one parent partition.",
        "Wide Transformations: Operations like groupByKey(), join(), and distinct() which require data from multiple parent partitions.",
        "Shuffle Cost: Wide transformations trigger a shuffle, moving data across network executors, which is the most expensive operation in Spark.",
        "Optimization: Reduce wide transformations where possible (e.g., using reduceByKey over groupByKey) to minimize memory spills."
    ],
    'A Spark job processing 1TB of data takes 3 hours but should run in 20 minutes.': [
        "Data Skew: Look at the Spark UI Stage page for tasks taking disproportionately long compared to the median. Mitigate by salting keys.",
        "Spill to Disk: Check for massive Memory Spill / Disk Spill metrics. Increase executor memory or repartition prior to wide transformations.",
        "Shuffle Partitions: Increase default `spark.sql.shuffle.partitions` (200) to a value closer to 2x or 3x the number of cluster cores.",
        "File Formats: Ensure inputs are heavily compressed, splittable formats (like Parquet/ORC) and employ partition pruning."
    ],
    'You have two DataFrames: one with 10TB of events, one with 500MB of user dimensions.': [
        "Broadcast Hash Join: Because the dimension table is 500MB, it can easily fit into the memory of every executor.",
        "Implementation: Use the `broadcast()` hint or adjust `spark.sql.autoBroadcastJoinThreshold` to force a broadcast.",
        "Performance: This eliminates the need for a massive network shuffle of the 10TB table, functioning as a localized map-side join.",
        "Fallback: If data grows beyond memory limits, the system falls back to SortMergeJoin, requiring expensive shuffles."
    ],
    'Your Spark executors are throwing OutOfMemoryError during a groupBy + aggregation': [
        "Memory Tuning: Check if the OOM is occurring during execution (shuffle) or storage (caching). Increase `spark.executor.memory`.",
        "Overhead: If it is a container-kill, increase `spark.executor.memoryOverhead` to allocate more off-heap memory.",
        "Algorithm Swap: Do not use `groupByKey()` which buffers all values in memory. Use `reduceByKey()` to aggregate map-side first.",
        "Repartitioning: If partitions are too large, insert a `.repartition()` to break data into smaller, manageable chunks for each thread."
    ],
    'Given an array of integers and a number k, find the maximum sum of a subarray of size k.': [
        "Initialization: Compute the sum of the first `k` elements and store it as the initial maximum window sum.",
        "Sliding Mechanism: For element `i` from `k` to the end of the array, add the new element and subtract the element at `i-k`.",
        "Tracking: Compare the newly computed window sum against the global maximum and update if larger.",
        "Time Complexity: This approach evaluates in strict O(n) time and O(1) space, as it passes through the array exactly once."
    ],
    'Given a list of strings, group all anagrams together.': [
        "Key Generation: For each string, sort its characters alphabetically to generate a standard signature (e.g., 'eat' -> 'aet').",
        "Dictionary Mapping: Use a Hash Map where the sorted signature is the key, and the value is a list of the original strings.",
        "Alternative Keying: To avoid the O(K log K) string sort, create a 26-element character frequency array and cast it to a tuple as the dict key.",
        "Time Complexity: Sorting takes O(N * K log K). The character array approach drops this to O(N * K)."
    ],
    'Given a list of tasks and their prerequisites, find a valid execution order': [
        "Graph Construction: Build an adjacency list to represent prerequisites as directed edges, and an array to track in-degrees for each node.",
        "Queue Initialization: Identify all nodes (tasks) with an in-degree of 0 (no prerequisites) and push them onto a queue.",
        "BFS Traversal: Pop a node, append to the sorted list, and decrement the in-degree of its neighbors. If a neighbor reaches 0, enqueue it.",
        "Cycle Detection: If the processed node count equals the total tasks, return the order. Otherwise, a cycle exists (return empty or error)."
    ],
    'Implement Fibonacci using recursion, then optimize with memoization, then with DP.': [
        "Naive Recursion: Base case `if n <= 1 return n`. Else `return fib(n-1) + fib(n-2)`. Pathological O(2^n) time.",
        "Top-Down Memoization: Pass a dictionary/array into the recursion. Store computed results. Drops time to O(N) by preventing duplicate sub-trees.",
        "Bottom-Up DP: Use a loop from 2 to N, maintaining an array of solutions. Time is O(N), Space is O(N).",
        "Constant Space DP: Realize we only need the last two variables. Track `a` and `b`. Swap them. Drops Space to strict O(1)."
    ],
    'Given an array, return the k most frequent elements.': [
        "Hash Map Counting: First pass, iterate through the array compiling a frequency map of value -> count. O(N).",
        "Min-Heap Approach: Push keys into a priority queue/min-heap based on frequency. Maintain size K. Total time O(N log K).",
        "Bucket Sort Optimization: Create an array of lists `buckets` where the index is the frequency. Time drops to strict O(N).",
        "Extraction: Iterate the buckets backwards (from max possible frequency N down to 1), appending items until K is reached."
    ]
}

new_html = []
blocks = text.split('<div class="q-answer">')

new_html.append(blocks[0])

for block in blocks[1:]:
    # Find which prompt it is to inject the right answer
    matched_prompt = None
    for prompt_key, bullets in answers_map.items():
        if prompt_key in block and "▶ SHOW EXPERT ANSWER" not in block:
            matched_prompt = prompt_key
            break
    
    if matched_prompt:
        # Build the details block
        bullets_html = ""
        for b in answers_map[matched_prompt]:
            bullets_html += f"                <li style=\"margin-bottom: .75rem;\">{b}</li>\n"
        
        details_block = f"""
          <details style="margin-top: 1.5rem; background: rgba(0,0,0,0.2); border: 1px solid var(--border); padding: 1rem; border-left: 2px solid var(--amber);">
            <summary style="font-family: 'IBM Plex Mono'; font-size: .65rem; color: var(--amber); letter-spacing: .1em; cursor: pointer; outline: none; list-style: none;">
              ▶ SHOW EXPERT ANSWER
            </summary>
            <div style="margin-top: 1rem;">
              <ul style="padding-left: 1.25rem; margin-bottom: 0;">
{bullets_html}              </ul>
            </div>
          </details>
        """
        
        # Inject details_block right before the closing </div> of <div class="q-answer">
        # Find the end of the block which is </div>
        # Actually block ends at </div>\n      </details>
        # So we can just split by "</div>\n      </details>" or rfind "</div>"
        
        # Find the first </div> that closes q-answer
        # Since <p> tags are closed inside, rfind("</div>") should work for replacing the end of the div
        end_idx = block.rfind("</div>")
        if end_idx != -1:
            modified_block = block[:end_idx] + details_block + block[end_idx:]
            new_html.append('<div class="q-answer">' + modified_block)
        else:
            new_html.append('<div class="q-answer">' + block)
            
    else:
        new_html.append('<div class="q-answer">' + block)

result = "".join(new_html)

with open("intel.html", "w") as f:
    f.write(result)

print("SUCCESSFULLY UPDATED MULTIPLE ANSWERS")
