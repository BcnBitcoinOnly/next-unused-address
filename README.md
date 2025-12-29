# Bitcoin Address API

Tiny HTTP API that serves random Bitcoin addresses derived from a descriptor.

Supports single-sig, multisig, and BIP389 multipath descriptors.

## Setup

1. Sync dependencies:
   ```bash
   uv sync
   ```

2. Create `.env` file with your descriptor and optional mempool URL:
   ```bash
   echo 'DESCRIPTOR=wpkh(xpub.../0/*)' > .env
   echo 'MEMPOOL_URL=https://mempool.space' >> .env  # optional, this is the default
   ```

3. Run the server:
   ```bash
   make serve
   ```

## Descriptor Examples

Single-sig P2WPKH:
```
wpkh(xpub.../0/*)
```

Multisig 2-of-3:
```
wsh(sortedmulti(2,xpub1/0/*,xpub2/0/*,xpub3/0/*))
```

BIP389 multipath (receive + change):
```
wpkh(xpub.../<0;1>/*)
```

## Usage

```bash
curl http://localhost:8080/address
```

Response:
```json
{
  "address": "bc1q...",
  "index": 4
}
```

Returns the first unused address (zero balance) by scanning from index 0 until an empty address is found.
