import os
import random
from flask import Flask, jsonify
from dotenv import load_dotenv
from embit.descriptor import Descriptor

load_dotenv()

app = Flask(__name__)

DESCRIPTOR = os.getenv("DESCRIPTOR")
if not DESCRIPTOR:
    raise ValueError("DESCRIPTOR not found in environment variables")

# Parse descriptor once at startup
DESC = Descriptor.from_string(DESCRIPTOR)

# Derive addresses from index 0 to this max (exclusive)
MAX_INDEX = 10


def derive_address(index: int) -> str:
    """Derive a Bitcoin address from the descriptor at the given index."""
    # branch_index=0 for external/receive chain (BIP389 multipath)
    derived = DESC.derive(index, branch_index=0)
    return derived.address()


@app.route("/address", methods=["GET"])
def get_address():
    """Return a random Bitcoin address derived from the descriptor."""
    index = random.randint(0, MAX_INDEX - 1)
    address = derive_address(index)
    return jsonify({"address": address, "index": index})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
