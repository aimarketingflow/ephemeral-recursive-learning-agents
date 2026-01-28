#!/usr/bin/env python3
"""
MLX Model Downloader with Resume Support

Downloads MLX-compatible models from HuggingFace with:
- Progress tracking
- Resume capability (picks up where it left off)
- Status checkpoints

Author: Hana Omori
Date: January 27, 2026
"""

import os
import json
import time
import hashlib
from pathlib import Path
from huggingface_hub import hf_hub_download, snapshot_download, HfApi
from huggingface_hub.utils import HfHubHTTPError

# Configuration
MODELS_DIR = Path.home() / ".cache" / "erla_models"
STATUS_FILE = MODELS_DIR / "download_status.json"

# Recommended models for 8GB RAM M1
RECOMMENDED_MODELS = {
    "tiny": "mlx-community/Qwen1.5-0.5B-Chat-4bit",      # ~300MB, very fast
    "small": "mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit",  # ~600MB, good balance
    "medium": "mlx-community/Mistral-7B-Instruct-v0.2-4bit",  # ~4GB, best quality
}


def load_status():
    """Load download status from checkpoint file."""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"downloads": {}, "completed": []}


def save_status(status):
    """Save download status to checkpoint file."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def get_model_files(model_name: str):
    """Get list of files in a model repo."""
    api = HfApi()
    try:
        files = api.list_repo_files(model_name)
        return [f for f in files if not f.startswith(".")]
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def download_model_with_resume(model_name: str, force: bool = False):
    """
    Download an MLX model with resume support.
    
    Args:
        model_name: HuggingFace model name (e.g., "mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit")
        force: Force re-download even if completed
    """
    status = load_status()
    
    # Check if already completed
    if model_name in status["completed"] and not force:
        print(f"✅ Model already downloaded: {model_name}")
        local_path = MODELS_DIR / model_name.replace("/", "_")
        print(f"   Location: {local_path}")
        return str(local_path)
    
    print(f"📥 Downloading: {model_name}")
    print(f"   Destination: {MODELS_DIR}")
    print()
    
    # Get file list
    files = get_model_files(model_name)
    if not files:
        print("❌ Could not get file list")
        return None
    
    print(f"   Files to download: {len(files)}")
    
    # Initialize status for this model
    if model_name not in status["downloads"]:
        status["downloads"][model_name] = {
            "files": {f: {"status": "pending", "size": 0} for f in files},
            "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_status(status)
    
    model_status = status["downloads"][model_name]
    local_dir = MODELS_DIR / model_name.replace("/", "_")
    local_dir.mkdir(parents=True, exist_ok=True)
    
    # Download each file
    completed = 0
    failed = 0
    
    for filename in files:
        file_status = model_status["files"].get(filename, {"status": "pending"})
        
        if file_status["status"] == "completed":
            completed += 1
            continue
        
        print(f"   [{completed + failed + 1}/{len(files)}] {filename}...", end=" ", flush=True)
        
        try:
            # Download with resume support (huggingface_hub handles this)
            local_path = hf_hub_download(
                repo_id=model_name,
                filename=filename,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                resume_download=True,
            )
            
            # Mark as completed
            model_status["files"][filename] = {
                "status": "completed",
                "size": os.path.getsize(local_path),
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            save_status(status)
            
            size_mb = os.path.getsize(local_path) / 1024 / 1024
            print(f"✅ ({size_mb:.1f} MB)")
            completed += 1
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Download paused. Run again to resume.")
            save_status(status)
            return None
            
        except Exception as e:
            print(f"❌ Error: {e}")
            model_status["files"][filename] = {
                "status": "failed",
                "error": str(e),
            }
            save_status(status)
            failed += 1
    
    # Check if all completed
    if failed == 0:
        status["completed"].append(model_name)
        model_status["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_status(status)
        
        print()
        print(f"✅ Download complete: {model_name}")
        print(f"   Location: {local_dir}")
        return str(local_dir)
    else:
        print()
        print(f"⚠️  {failed} files failed. Run again to retry.")
        return None


def show_status():
    """Show current download status."""
    status = load_status()
    
    print("=" * 60)
    print("📊 Download Status")
    print("=" * 60)
    
    if not status["downloads"]:
        print("   No downloads in progress")
        return
    
    for model_name, model_status in status["downloads"].items():
        files = model_status["files"]
        completed = sum(1 for f in files.values() if f["status"] == "completed")
        total = len(files)
        
        is_done = model_name in status["completed"]
        status_icon = "✅" if is_done else "⏳"
        
        print(f"\n{status_icon} {model_name}")
        print(f"   Progress: {completed}/{total} files")
        
        if not is_done:
            pending = [f for f, s in files.items() if s["status"] == "pending"]
            if pending:
                print(f"   Pending: {pending[0]}...")


def clear_status(model_name: str = None):
    """Clear download status (for re-download)."""
    status = load_status()
    
    if model_name:
        if model_name in status["downloads"]:
            del status["downloads"][model_name]
        if model_name in status["completed"]:
            status["completed"].remove(model_name)
        print(f"🗑️  Cleared status for: {model_name}")
    else:
        status = {"downloads": {}, "completed": []}
        print("🗑️  Cleared all download status")
    
    save_status(status)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download MLX models with resume support")
    parser.add_argument("--model", "-m", help="Model to download (or 'tiny', 'small', 'medium')")
    parser.add_argument("--status", "-s", action="store_true", help="Show download status")
    parser.add_argument("--clear", "-c", action="store_true", help="Clear download status")
    parser.add_argument("--list", "-l", action="store_true", help="List recommended models")
    args = parser.parse_args()
    
    if args.list:
        print("Recommended MLX models for 8GB RAM:")
        print()
        for key, name in RECOMMENDED_MODELS.items():
            print(f"  {key:8} → {name}")
        print()
        print("Usage: python download_mlx_model.py --model tiny")
        
    elif args.status:
        show_status()
        
    elif args.clear:
        clear_status(args.model)
        
    elif args.model:
        # Resolve shorthand names
        model_name = RECOMMENDED_MODELS.get(args.model, args.model)
        download_model_with_resume(model_name)
        
    else:
        print("ERLA MLX Model Downloader")
        print()
        print("Usage:")
        print("  python download_mlx_model.py --model tiny    # Download tiny model (~300MB)")
        print("  python download_mlx_model.py --model small   # Download small model (~600MB)")
        print("  python download_mlx_model.py --status        # Check download progress")
        print("  python download_mlx_model.py --list          # List recommended models")
        print()
        print("Downloads resume automatically if interrupted!")
