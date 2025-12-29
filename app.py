import os
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv
from embit.descriptor import Descriptor

load_dotenv()

app = Flask(__name__)

DESCRIPTOR = os.getenv("DESCRIPTOR")
if not DESCRIPTOR:
    raise ValueError("DESCRIPTOR not found in environment variables")
MEMPOOL_URL = os.getenv("MEMPOOL_URL")
if not MEMPOOL_URL:
    raise ValueError("MEMPOOL_URL not found in environment variables")

DESC = Descriptor.from_string(DESCRIPTOR)
used_indices: set[int] = set()


def derive_address(index: int) -> str:
    """Derive a Bitcoin address from the descriptor at the given index."""
    RECEIVE_BRANCH_INDEX = 0
    derived = DESC.derive(index, branch_index=RECEIVE_BRANCH_INDEX)
    return derived.address()


def has_tx_history(address: str) -> bool:
    """Check if an address has any transaction history."""
    url = f"{MEMPOOL_URL}/api/address/{address}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    chain = data.get("chain_stats", {})
    mempool = data.get("mempool_stats", {})
    
    tx_count = chain.get("tx_count", 0) + mempool.get("tx_count", 0)
    return tx_count > 0


def find_unused_address() -> tuple[str, int]:
    """Find the first address with no transaction history."""
    index = 0
    while True:
        already_seen = index in used_indices
        if already_seen:
            index += 1
            continue
        
        address = derive_address(index)
        if not has_tx_history(address):
            return address, index
        
        # Cache this index as used
        used_indices.add(index)
        index += 1


@app.route("/address", methods=["GET"])
def get_address():
    """Return the first address that has never received any sats."""
    address, index = find_unused_address()
    return jsonify({"address": address, "index": index})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
