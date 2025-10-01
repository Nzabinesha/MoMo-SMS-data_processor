#!/usr/bin/env python3
"""
dsa/parse_xml.py
Parse examples/modified_sms_v2.xml -> data/processed/transactions.json
"""

import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# Paths (adjust if needed)
INPUT_XML = Path("/examples/modified_sms_v2.xml")
OUT_JSON = Path("data/processed/transactions.json")

# Regexes tuned for your SMS patterns
AMOUNT_RE = re.compile(r'(\d{1,3}(?:[,\s]\d{3})*|\d+)\s*RWF', re.IGNORECASE)
TXID_RE = re.compile(r'(?:TxId:|Financial Transaction Id:)\s*([0-9A-Za-z\-]+)', re.IGNORECASE)
FEE_RE = re.compile(r'Fee\s*was[: ]*\s*([0-9,]+)\s*RWF', re.IGNORECASE)
BALANCE_RE = re.compile(r'(?:new balance[:\s]*|NEW BALANCE\s*[:]*\s*)([0-9,]+)\s*RWF', re.IGNORECASE)
RECEIVED_RE = re.compile(r'You have received\s+([0-9,]+)\s*RWF\s+from\s+([A-Za-z .\-]+)\s*\(?([+\d\*]{6,})?\)?', re.IGNORECASE)
PAYMENT_RE = re.compile(r'TxId:\s*([0-9A-Za-z\-]+).*payment of\s+([0-9,]+)\s*RWF\s+to\s+([A-Za-z .\-0-9]+)', re.IGNORECASE)
TRANSFER_RE = re.compile(r'(?:(?:transferred to|to)\s+)([A-Za-z .\-]+)\s*\(?([+\d\*]{6,})\)?', re.IGNORECASE)
DATE_ATTR_RE = re.compile(r'^\d+$')  # numeric epoch in ms

def parse_sms_element(elem):
    attrs = elem.attrib.copy()
    body = attrs.get("body", "") or ""
    readable_date = attrs.get("readable_date") or None
    epoch_ms = attrs.get("date")  # sometimes present as milliseconds

    # timestamp: prefer epoch_ms -> ISO, else readable_date
    timestamp = None
    if epoch_ms and DATE_ATTR_RE.match(epoch_ms):
        try:
            ts = int(epoch_ms) / 1000.0
            timestamp = datetime.utcfromtimestamp(ts).isoformat() + "Z"
        except Exception:
            timestamp = readable_date
    else:
        timestamp = readable_date

    tx = {
        "internal_id": None,            # set later
        "transaction_id": None,         # external id if any (TxId or Financial Transaction Id)
        "transaction_type": None,       # receive/payment/deposit/transfer/other
        "amount": None,
        "fee": None,
        "balance": None,
        "sender": None,                 # {"name":..., "phone":...} if found
        "receiver": None,               # {"name":..., "phone":...} if found
        "timestamp": timestamp,
        "raw": body,
        "xml_attrs": attrs
    }

    # txid
    m = TXID_RE.search(body)
    if m:
        tx["transaction_id"] = m.group(1).strip()

    # amount (first RWF amount in message likely the transaction amount)
    m = AMOUNT_RE.search(body)
    if m:
        amt = m.group(1).replace(",", "").replace(" ", "")
        try:
            tx["amount"] = int(amt)
        except:
            try:
                tx["amount"] = int(float(amt))
            except:
                tx["amount"] = None

    # fee
    m = FEE_RE.search(body)
    if m:
        try:
            tx["fee"] = int(m.group(1).replace(",", ""))
        except:
            tx["fee"] = None

    # balance
    m = BALANCE_RE.search(body)
    if m:
        try:
            tx["balance"] = int(m.group(1).replace(",", ""))
        except:
            tx["balance"] = None

    # received pattern (You have received X RWF from NAME (phone))
    m = RECEIVED_RE.search(body)
    if m:
        tx["transaction_type"] = "receive"
        try:
            tx["amount"] = int(m.group(1).replace(",", ""))
        except:
            pass
        name = m.group(2).strip()
        phone = m.group(3)
        tx["sender"] = {"name": name, "phone": phone} if name or phone else None
        # receiver is the account owner (not present in body) -> leave None

    # payment pattern (TxId: ... Your payment of X RWF to NAME ...)
    m = PAYMENT_RE.search(body)
    if m:
        tx["transaction_type"] = "payment"
        if not tx["transaction_id"]:
            tx["transaction_id"] = m.group(1).strip()
        try:
            tx["amount"] = int(m.group(2).replace(",", ""))
        except:
            pass
        receiver_name = m.group(3).strip()
        tx["receiver"] = {"name": receiver_name}

    # transfer pattern (transferred to NAME (phone) from <something>)
    m = TRANSFER_RE.search(body)
    if m:
        # avoid overwriting receiver if payment already set
        if not tx["receiver"]:
            tx["receiver"] = {"name": m.group(1).strip(), "phone": m.group(2)}
        if not tx["transaction_type"]:
            tx["transaction_type"] = "transfer"

    # deposit (bank deposit)
    if "bank deposit" in body.lower() or "bank deposit of" in body.lower():
        tx["transaction_type"] = "deposit"
        # amount may already be set by AMOUNT_RE

    # fallback: set type to 'other' if none matched
    if not tx["transaction_type"]:
        low = body.lower()
        if "transferred" in low:
            tx["transaction_type"] = "transfer"
        elif "deposit" in low:
            tx["transaction_type"] = "deposit"
        elif "payment" in low:
            tx["transaction_type"] = "payment"
        elif "received" in low:
            tx["transaction_type"] = "receive"
        else:
            tx["transaction_type"] = "other"

    return tx

def parse_file(input_path=INPUT_XML):
    if not input_path.exists():
        raise FileNotFoundError(f"{input_path} not found")
    tree = ET.parse(str(input_path))
    root = tree.getroot()
    sms_elems = root.findall(".//sms")
    parsed = []
    for elem in sms_elems:
        parsed.append(parse_sms_element(elem))
    # assign internal ids
    for idx, rec in enumerate(parsed, start=1):
        rec["internal_id"] = idx
        if not rec.get("transaction_id"):
            rec["transaction_id"] = f"local-{idx}"
    return parsed

def save_json(data, out_path=OUT_JSON):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(data)} transactions to {out_path}")

def main():
    parsed = parse_file()
    save_json(parsed)

if __name__ == "__main__":
    main()

