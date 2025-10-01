!/usr/bin/env python3
"""
dsa/search.py
Compare Linear Search vs Dictionary Lookup on MoMo SMS transactions.
Uses parse_file() from parse_xml.py to load transactions.
"""

import time
import random
from parse_xml import parse_file

# ---------- Linear Search ----------
def linear_search(transactions, transaction_id):
    for tx in transactions:
        if str(tx.get("transaction_id")) == str(transaction_id):
            return tx
    return None

# ---------- Dictionary Lookup ----------

def dict_lookup(transaction_dict, transaction_id):
    return transaction_dict.get(str(transaction_id))

# ---------- Benchmark ----------
def benchmark(transactions, runs=20):
    transaction_dict = build_transaction_dict(transactions)
    ids = list(transaction_dict.keys())

    if not ids:
        print("No transactions found.")
        return

    # mix of valid and invalid IDs
    search_ids = [random.choice(ids) if random.random() < 0.8 else f"invalid-{i}" for i in range(runs)]

    # Linear Search timing
    start = time.time()
    for sid in search_ids:
        linear_search(transactions, sid)
    linear_time = time.time() - start

    # Dict Lookup timing
    start = time.time()
    for sid in search_ids:
        dict_lookup(transaction_dict, sid)
    dict_time = time.time() - start

    # Results
    print(f"\n--- Benchmark Results ({runs} lookups) ---")
    print(f"Linear Search Total Time: {linear_time:.8f} sec")
    print(f"Dictionary Lookup Total Time: {dict_time:.8f} sec")
    print(f"Average Linear Search: {linear_time/runs:.10f} sec per lookup")
    print(f"Average Dict Lookup : {dict_time/runs:.10f} sec per lookup")

    print("\nReflection:")
    print("- Linear Search: O(n), grows with dataset size.")
    print("- Dict Lookup: O(1) on average, independent of dataset size.")
    print("- Dict lookup is faster because Python dicts use hash tables.")
    print("- Alternatives: binary search on sorted data (O(log n)), B-Trees, database indexes.")

# ---------- Main ----------
if __name__ == "__main__":
    transactions = parse_file()  # loads from examples/modified_sms_v2.xml
    print(f"Loaded {len(transactions)} transactions")
    benchmark(transactions, runs=20)
