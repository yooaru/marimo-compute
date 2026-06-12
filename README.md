# marimo-compute

ML compute worker notebooks for [molab](https://molab.marimo.io/notebooks).

## Notebooks

| Notebook | Description |
|----------|-------------|
| `compute_worker.py` | Distributed compute worker with auto-restart |

## Quick Start

1. Go to https://molab.marimo.io/notebooks
2. Click "New notebook" → "From GitHub"
3. Paste: `https://github.com/yooaru/marimo-compute/blob/main/compute_worker.py`

Or open directly:
[![Open in molab](https://molab.marimo.io/github/yooaru/marimo-compute/blob/main/compute_worker.py)](https://molab.marimo.io/github/yooaru/marimo-compute/blob/main/compute_worker.py)

## GPU

Attach NVIDIA RTX Pro 6000 Blackwell (96GB VRAM) via notebook specs button.

## Config

Edit the configuration cell in the notebook:
- `RELAY_HOST` / `RELAY_PORT` — relay server
- `WALLET` — your wallet address
- `WORKER_NAME` — node identifier
