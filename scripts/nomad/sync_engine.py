#!/usr/bin/env python3
# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Nomad Engine Orchestrator — Robust Sync for llama.cpp & GGUF Models

import os
import sys
import json
import urllib.request
import zipfile
import shutil
import subprocess
from pathlib import Path

# --- CONFIGURATION ---
LLAMA_CPP_ZIP = "https://github.com/ggerganov/llama.cpp/archive/refs/heads/master.zip"
ENGINE_DEST = Path("src/clients/nomad_android/app/src/main/cpp/llama_cpp")

# Model Zoo: Classified by hardware requirements (RAM)
MODEL_ZOO = {
    "POCKET": { # For 4GB RAM devices
        "name": "llama-3.2-1b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "min_ram_gb": 4
    },
    "NOMAD": { # For 8GB RAM devices
        "name": "llama-3.2-3b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "min_ram_gb": 8
    },
    "CENTINELA": { # For 12GB+ RAM / High-end devices
        "name": "mistral-7b-v0.3-q4_k_m.gguf",
        "url": "https://huggingface.co/MaziyarPanahi/Mistral-7B-v0.3-GGUF/resolve/main/Mistral-7B-v0.3.Q4_K_M.gguf",
        "min_ram_gb": 12
    }
}

DEFAULT_TIER = "POCKET"
# ---------------------

def log(msg, symbol="ℹ️"):
    print(f"{symbol} {msg}")

def download_file(url, dest):
    log(f"Downloading {url} to {dest}...", "📥")
    try:
        urllib.request.urlretrieve(url, dest)
        log(f"Download complete: {dest}", "✅")
    except Exception as e:
        log(f"Download failed: {e}", "❌")
        sys.exit(1)

def sync_llama_cpp():
    log("Synchronizing llama.cpp engine sources...", "⚙️")
    
    tmp_zip = Path("tmp_llama.zip")
    tmp_dir = Path("tmp_llama_extracted")

    # 1. Download
    download_file(LLAMA_CPP_ZIP, tmp_zip)

    # 2. Extract
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    
    log(f"Extracting to {tmp_dir}...", "📦")
    with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)

    # 3. Locate the real source folder (usually llama.cpp-master)
    extracted_root = next(tmp_dir.iterdir())
    
    # 4. Atomic Replace
    if ENGINE_DEST.exists():
        log(f"Cleaning existing engine at {ENGINE_DEST}...", "🧹")
        shutil.rmtree(ENGINE_DEST)
    
    ENGINE_DEST.mkdir(parents=True, exist_ok=True)
    
    # We only need the core files for the Android build to keep it lean
    # but for robustness, we'll copy the whole thing for now to avoid missing headers
    log(f"Moving sources to {ENGINE_DEST}...", "🚚")
    for item in extracted_root.iterdir():
        dest_item = ENGINE_DEST / item.name
        if item.is_dir():
            shutil.copytree(item, dest_item)
        else:
            shutil.copy2(item, dest_item)

    # 5. Cleanup
    tmp_zip.unlink()
    shutil.rmtree(tmp_dir)
    log("Engine sync successful.", "✅")

def update_cmake():
    log("Updating CMakeLists.txt to include real llama.cpp sources...", "📝")
    cmake_path = Path("src/clients/nomad_android/app/src/main/cpp/CMakeLists.txt")
    
    # Standard mobile-friendly CMake template for llama.cpp integration
    # Note: Real implementation would ideally use the llama.cpp provided CMake or a custom wrapper
    cmake_content = """cmake_minimum_required(VERSION 3.22.1)
project("nomad_llama")

set(CMAKE_CXX_STANDARD 17)
set(LLAMA_DIR ${CMAKE_CURRENT_SOURCE_DIR}/llama_cpp)

# Minimal sources for inference
add_library(nomad_llama SHARED
        llama-jni.cpp
        ${LLAMA_DIR}/ggml.c
        ${LLAMA_DIR}/ggml-alloc.c
        ${LLAMA_DIR}/ggml-backend.c
        ${LLAMA_DIR}/ggml-quants.c
        ${LLAMA_DIR}/llama.cpp
)

target_include_directories(nomad_llama PRIVATE ${LLAMA_DIR})

find_library(log-lib log)
target_link_libraries(nomad_llama ${log-lib})
"""
    cmake_path.write_text(cmake_content)
    log("CMakeLists.txt updated.", "✅")

def sync_model(tier=None):
    tier = tier or DEFAULT_TIER
    if tier not in MODEL_ZOO:
        log(f"Unknown tier '{tier}'. Available: {list(MODEL_ZOO.keys())}", "❌")
        sys.exit(1)

    model = MODEL_ZOO[tier]
    log(f"Preparing model reference for tier '{tier}': {model['name']}", "🤖")
    log(f"  URL: {model['url']}", "ℹ️")
    log(f"  Min RAM: {model['min_ram_gb']}GB", "ℹ️")

if __name__ == "__main__":
    log("NOMAD ENGINE SYNC STARTING", "🚀")

    # Parse tier from CLI: --tier POCKET|NOMAD|CENTINELA
    tier = DEFAULT_TIER
    if "--tier" in sys.argv:
        idx = sys.argv.index("--tier")
        if idx + 1 < len(sys.argv):
            tier = sys.argv[idx + 1].upper()

    # Option to skip engine sync if only model needs update
    if "--only-model" not in sys.argv:
        sync_llama_cpp()
        update_cmake()

    sync_model(tier)

    log("NOMAD ENGINE SYNC COMPLETE", "🏁")

