import os
import random
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv
from embit.descriptor import Descriptor

load_dotenv()

app = Flask(__name__)

DESCRIPTOR = os.getenv("DESCRIPTOR")
if not DESCRIPTOR:
    raise ValueError("DESCRIPTOR not found in environment variables")

MEMPOOL_URL = os.getenv("MEMPOOL_URL", "https://mempool.space")

# Parse descriptor once at startup
DESC = Descriptor.from_string(DESCRIPTOR)

# Derive addresses from index 0 to this max (exclusive)
MAX_INDEX = 10


def derive_address(index: int) -> str:
    """Derive a Bitcoin address from the descriptor at the given index."""
    # branch_index=0 for external/receive chain (BIP389 multipath)
    derived = DESC.derive(index, branch_index=0)
    return derived.address()


def get_balance(address: str) -> int:
    """Get the balance of an address in satoshis from mempool.space."""
    url = f"{MEMPOOL_URL}/api/address/{address}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    # Balance = funded - spent (both confirmed and mempool)
    chain = data.get("chain_stats", {})
    mempool = data.get("mempool_stats", {})
    
    funded = chain.get("funded_txo_sum", 0) + mempool.get("funded_txo_sum", 0)
    spent = chain.get("spent_txo_sum", 0) + mempool.get("spent_txo_sum", 0)
    
    return funded - spent


@app.route("/address", methods=["GET"])
def get_address():
    """Return a random Bitcoin address derived from the descriptor."""
    index = random.randint(0, MAX_INDEX - 1)
    address = derive_address(index)
    balance = get_balance(address)
    return jsonify({"address": address, "index": index, "balance_sats": balance})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
