#!/usr/bin/env python3
# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Nomad Engine Orchestrator — Sync for llama.cpp, GGUF Models & Sherpa-ONNX

import json
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

# --- LLAMA.CPP CONFIGURATION ---
LLAMA_CPP_ZIP = "https://github.com/ggerganov/llama.cpp/archive/refs/heads/master.zip"
ENGINE_DEST = Path("src/clients/nomad_android/app/src/main/cpp/llama_cpp")

# Model Zoo: Classified by hardware requirements (RAM)
MODEL_ZOO = {
    "POCKET": {  # For 4GB RAM devices
        "name": "llama-3.2-1b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "min_ram_gb": 4,
    },
    "NOMAD": {  # For 8GB RAM devices
        "name": "llama-3.2-3b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "min_ram_gb": 8,
    },
    "CENTINELA": {  # For 12GB+ RAM / High-end devices
        "name": "mistral-7b-v0.3-q4_k_m.gguf",
        "url": "https://huggingface.co/MaziyarPanahi/Mistral-7B-v0.3-GGUF/resolve/main/Mistral-7B-v0.3.Q4_K_M.gguf",
        "min_ram_gb": 12,
    },
}

# --- SHERPA-ONNX CONFIGURATION ---
# Official pre-built Android package from k2-fsa/sherpa-onnx GitHub Releases.
# Format: tar.bz2 containing per-ABI .so files + Java .jar
# Pinned for reproducibility — update intentionally via --update-sherpa flag.
SHERPA_ONNX_VERSION = "1.13.0"
SHERPA_ANDROID_URL = (
    f"https://github.com/k2-fsa/sherpa-onnx/releases/download/"
    f"v{SHERPA_ONNX_VERSION}/sherpa-onnx-v{SHERPA_ONNX_VERSION}-android.tar.bz2"
)
# Gradle picks up .so files from jniLibs/ automatically by ABI dir
SHERPA_JNILIBS_DEST = Path("src/clients/nomad_android/app/src/main/jniLibs")
# .jar goes to libs/ and is included in the classpath
SHERPA_LIBS_DEST = Path("src/clients/nomad_android/app/libs")

# Keyword Spotting model: Zipformer bilingual (en+zh), ~3.3M params, ~26MB
# Custom keyword "ethos" injected at runtime via inline keyword definition.
# Source: https://k2-fsa.github.io/sherpa/onnx/kws/pretrained_models.html
SHERPA_KWS_MODEL_URL = (
    "https://github.com/k2-fsa/sherpa-onnx/releases/download/"
    "kws-models/sherpa-onnx-kws-zipformer-wenetspeech-3.3M-2024-01-01.tar.bz2"
)
SHERPA_KWS_MODEL_DEST = Path(
    "src/clients/nomad_android/app/src/main/assets/kws_model"
)

DEFAULT_TIER = "POCKET"
# ---------------------


def log(msg: str, symbol: str = "i") -> None:
    try:
        print(f"{symbol} {msg}")
    except UnicodeEncodeError:
        print(f"[{symbol}] {msg}".encode("ascii", "ignore").decode("ascii"))


def download_file(url: str, dest: Path, skip_if_exists: bool = False) -> None:
    dest = Path(dest)
    if skip_if_exists and dest.exists():
        log(f"Skipping download (already present): {dest.name}", "-")
        return
    log(f"Downloading {url} ...", ">>")
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, dest)
        log(f"Download complete: {dest}", "OK")
    except Exception as e:
        log(f"Download failed: {e}", "ERR")
        sys.exit(1)


def sync_llama_cpp() -> None:
    log("Synchronizing llama.cpp engine sources...", "==>")
    tmp_zip = Path("tmp_llama.zip")
    tmp_dir = Path("tmp_llama_extracted")

    download_file(LLAMA_CPP_ZIP, tmp_zip)

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

    log(f"Extracting to {tmp_dir}...", ">>")
    with zipfile.ZipFile(tmp_zip, "r") as z:
        z.extractall(tmp_dir)

    extracted_root = next(tmp_dir.iterdir())

    if ENGINE_DEST.exists():
        log(f"Cleaning existing engine at {ENGINE_DEST}...", "~~")
        shutil.rmtree(ENGINE_DEST)

    ENGINE_DEST.mkdir(parents=True, exist_ok=True)
    log(f"Moving sources to {ENGINE_DEST}...", ">>")
    for item in extracted_root.iterdir():
        dest_item = ENGINE_DEST / item.name
        if item.is_dir():
            shutil.copytree(item, dest_item)
        else:
            shutil.copy2(item, dest_item)

    tmp_zip.unlink()
    shutil.rmtree(tmp_dir)
    log("Engine sync successful.", "OK")


def update_cmake() -> None:
    log("Updating CMakeLists.txt to include real llama.cpp sources...", ">>")
    cmake_path = Path("src/clients/nomad_android/app/src/main/cpp/CMakeLists.txt")
    cmake_content = """\
cmake_minimum_required(VERSION 3.22.1)
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
    log("CMakeLists.txt updated.", "OK")


def sync_sherpa_onnx() -> None:
    """Download official Sherpa-ONNX Android package and KWS model."""
    log(f"Synchronizing Sherpa-ONNX v{SHERPA_ONNX_VERSION} (Wake Word Engine)...", "==>")

    # 1. Download android tarball (per-ABI .so + .jar)
    android_archive = Path("tmp_sherpa_android.tar.bz2")
    download_file(SHERPA_ANDROID_URL, android_archive, skip_if_exists=False)

    # 2. Extract and place into expected Gradle dirs
    log("Extracting Sherpa-ONNX Android package...", ">>")
    tmp_sherpa = Path("tmp_sherpa_extracted")
    if tmp_sherpa.exists():
        shutil.rmtree(tmp_sherpa)
    try:
        with tarfile.open(android_archive, "r:bz2") as tar:
            tar.extractall(tmp_sherpa)
    except Exception as e:
        log(f"Sherpa extraction failed: {e}", "ERR")
        sys.exit(1)
    finally:
        if android_archive.exists():
            android_archive.unlink()

    # Locate extracted root (first child dir)
    sherpa_root = next(tmp_sherpa.iterdir())

    # Place .jar into app/libs/
    SHERPA_LIBS_DEST.mkdir(parents=True, exist_ok=True)
    for jar in sherpa_root.rglob("*.jar"):
        shutil.copy2(jar, SHERPA_LIBS_DEST / jar.name)
        log(f"JAR: {jar.name} -> {SHERPA_LIBS_DEST}", "OK")

    # Place per-ABI .so into jniLibs/
    SHERPA_JNILIBS_DEST.mkdir(parents=True, exist_ok=True)
    for abi in ["arm64-v8a", "armeabi-v7a", "x86_64", "x86"]:
        src_abi = sherpa_root / abi
        if src_abi.exists():
            dest_abi = SHERPA_JNILIBS_DEST / abi
            if dest_abi.exists():
                shutil.rmtree(dest_abi)
            shutil.copytree(src_abi, dest_abi)
            log(f"Native libs: {abi}/ -> {SHERPA_JNILIBS_DEST}", "OK")

    shutil.rmtree(tmp_sherpa)
    log("Sherpa-ONNX Android native libs ready.", "OK")

    # 2b. Download the API JAR (compile-time stubs for Kotlin/Java)
    api_jar_url = (
        f"https://github.com/k2-fsa/sherpa-onnx/releases/download/"
        f"v{SHERPA_ONNX_VERSION}/sherpa-onnx-v{SHERPA_ONNX_VERSION}.jar"
    )
    api_jar_dest = SHERPA_LIBS_DEST / f"sherpa-onnx-v{SHERPA_ONNX_VERSION}.jar"
    download_file(api_jar_url, api_jar_dest, skip_if_exists=True)
    log(f"API JAR ready: {api_jar_dest.name}", "OK")

    # 3. Download KWS model
    model_archive = Path("tmp_kws_model.tar.bz2")
    download_file(SHERPA_KWS_MODEL_URL, model_archive, skip_if_exists=False)

    if SHERPA_KWS_MODEL_DEST.exists():
        shutil.rmtree(SHERPA_KWS_MODEL_DEST)
    SHERPA_KWS_MODEL_DEST.mkdir(parents=True, exist_ok=True)
    log("Extracting KWS model...", ">>")
    try:
        with tarfile.open(model_archive, "r:bz2") as tar:
            tar.extractall(SHERPA_KWS_MODEL_DEST)
        log(f"KWS model ready: {SHERPA_KWS_MODEL_DEST}", "OK")
    except Exception as e:
        log(f"Model extraction failed: {e}", "ERR")
        log("Continuing — native libs ready; add model manually if needed.", "!")
    finally:
        if model_archive.exists():
            model_archive.unlink()

    # 4. Write runtime discovery metadata
    metadata = {
        "version": SHERPA_ONNX_VERSION,
        "type": "keyword_spotting",
        "keywords": ["ethos", "etos", "ethos nomad"],
        "model_dir": "kws_model",
        "note": "Zipformer wenetspeech 3.3M — smallest bilingual model available",
    }
    meta_path = Path("src/clients/nomad_android/app/src/main/assets/sherpa_config.json")
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(metadata, indent=2))
    log(f"Runtime config: {meta_path}", "OK")


def sync_model(tier: str | None = None) -> None:
    tier = tier or DEFAULT_TIER
    if tier not in MODEL_ZOO:
        log(f"Unknown tier '{tier}'. Available: {list(MODEL_ZOO.keys())}", "ERR")
        sys.exit(1)
    model = MODEL_ZOO[tier]
    log(f"Model reference for tier '{tier}': {model['name']}", ">>")
    log(f"  URL: {model['url']}", "i")
    log(f"  Min RAM: {model['min_ram_gb']}GB", "i")


if __name__ == "__main__":
    log("NOMAD ENGINE SYNC STARTING", "===")

    tier = DEFAULT_TIER
    if "--tier" in sys.argv:
        idx = sys.argv.index("--tier")
        if idx + 1 < len(sys.argv):
            tier = sys.argv[idx + 1].upper()

    only_model = "--only-model" in sys.argv
    only_sherpa = "--only-sherpa" in sys.argv
    skip_llama = "--skip-llama" in sys.argv

    if only_sherpa:
        sync_sherpa_onnx()
    elif only_model:
        sync_model(tier)
    else:
        if not skip_llama:
            sync_llama_cpp()
            update_cmake()
        sync_sherpa_onnx()
        sync_model(tier)

    log("NOMAD ENGINE SYNC COMPLETE", "===")
