# Next unused address

Tiny HTTP API that serves the first unused Bitcoin address derived from a descriptor.

Supports single-sig, multisig, and BIP389 multipath descriptors.

## Setup

1. Sync dependencies:
   ```bash
   uv sync
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

   - `DESCRIPTOR` (required): Bitcoin output descriptor
   - `MEMPOOL_URL` (required): Mempool instance URL
   - `BIND_ADDRESS` (optional, default `127.0.0.1`): Interface to bind (`0.0.0.0` for external access)
   - `LISTENING_PORT` (optional, default `8080`): Port to listen on

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

Returns the first unused address (plain text):

```
bc1q...
```

Scans from index 0 until finding an address with no transaction history.

## Warming up

The app keeps track of the highest unused index in memory. This is lost everytime you shutdown and restart. 

On boot, the runtime will start iterating through addresses until it finds the first unused one. On a wallet with many used addresses, this might take a while.

## Privacy and security

- The mempool server you query learns which addresses belong to your wallet. Use your own instance if this matters.
- Anyone with access to the `/address` endpoint can enumerate your addresses by calling it repeatedly. Keep `BIND_ADDRESS` as `127.0.0.1` and only allow trusted local apps to reach it.
- Your xpub/descriptor lets anyone derive all your addresses and view balances. Keep `.env` secure.

## Why this

We wanted to have a simple solution to serve addresses for donation purposes in the [Barcelona Bitcoin Only meetup homepage](https://bitcoinbarcelona.xyz), and didn't feel like deploying a full BTCPayserver instance just for this was sensible. We currently use this app to dynamically write the address into the homepage when someone requests it.
