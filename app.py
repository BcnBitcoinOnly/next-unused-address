import os
import requests
from flask import Flask
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
first_unused_index: int = 0


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


def find_unused_address(offset: int) -> tuple[int, str]:
    """Find the first address with no transaction history."""
    index = offset
    while True:
        address = derive_address(index)
        if not has_tx_history(address):
            return index, address
        index += 1


@app.route("/address", methods=["GET"])
def get_address():
    """Return the first address that has never received any sats."""
    global first_unused_index

    first_unused_index, address = find_unused_address(first_unused_index)
    return address


if __name__ == "__main__":
    bind_address = os.getenv("BIND_ADDRESS", "127.0.0.1")
    listening_port = int(os.getenv("LISTENING_PORT", "8080"))
    first_unused_index, _ = find_unused_address(0)
    app.run(host=bind_address, port=listening_port)
