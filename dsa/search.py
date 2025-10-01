import time
from parse_xml import parse_file  
# ---------- Linear Search ----------
def linear_search(transactions, transaction_id):
    for tx in transactions:
        if tx["id"] == transaction_id:
            return tx
    return None

# ---------- Dictionary Lookup ----------
def build_transaction_dict(transactions):
    return {tx["id"]: tx for tx in transactions}

def dict_lookup(transaction_dict, transaction_id):
    return transaction_dict.get(transaction_id, None)

# ---------- Comparison Runner ----------
if __name__ == "__main__":
    # Load transactions from the XML file
    transactions = parse_transactions("modified_sms_v2.xml")

    # Make sure we have at least 20 transactions
    print(f"Loaded {len(transactions)} transactions")

    # Pick a transaction ID to search for (you can change this)
    search_id = "20"

    # Linear Search
    start = time.time()
    result1 = linear_search(transactions, search_id)
    end = time.time()
    print("\n--- Linear Search ---")
    print("Result:", result1)
    print("Time Taken:", end - start, "seconds")

    # Dictionary Lookup
    transaction_dict = build_transaction_dict(transactions)
    start = time.time()
    result2 = dict_lookup(transaction_dict, search_id)
    end = time.time()
    print("\n--- Dictionary Lookup ---")
    print("Result:", result2)
    print("Time Taken:", end - start, "seconds")

    # Reflection
    print("\n✅ Dictionary lookup is faster because it uses hash tables (O(1)) vs linear scan (O(n))")
