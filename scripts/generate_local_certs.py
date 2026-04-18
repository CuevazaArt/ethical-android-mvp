#!/usr/bin/env python3
"""
Local SSL Certificate Generator for Phase 10 Nomad PWA.
Requires OpenSSL installed on the system (native on Linux/Mac, or git-bash on Windows).

If you prefer python-native:
1. pip install cryptography
2. Update this script to use python's cryptography module.

For simple deployment, this script just wraps an OpenSSL command.
"""

import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_log = logging.getLogger("SSL-Generator")

def generate_dev_certs(out_dir: str = ".certs"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    key_path = os.path.join(out_dir, "nomad-dev-key.pem")
    cert_path = os.path.join(out_dir, "nomad-dev-cert.pem")

    if os.path.exists(key_path) and os.path.exists(cert_path):
        _log.info("Certs already exist in %s", out_dir)
        return

    _log.info("Generating Self-Signed SSL Certificates using OpenSSL...")
    
    # Standard OpenSSL command for 365-day cert
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", key_path,
        "-out", cert_path,
        "-sha256", "-days", "365",
        "-nodes",
        "-subj", "/CN=EthosNomadDev/O=EthosKernel/C=US"
    ]

    try:
        subprocess.run(cmd, check=True)
        _log.info("Successfully generated dev certificates:")
        _log.info("  Key:  %s", key_path)
        _log.info("  Cert: %s", cert_path)
        _log.info("To run the uvicorn server with HTTPS, use:")
        _log.info(f"  uvicorn src.chat_server:app --host 0.0.0.0 --port 8443 --ssl-keyfile {key_path} --ssl-certfile {cert_path}")
    except FileNotFoundError:
        _log.critical("OpenSSL not found. Please ensure OpenSSL is installed on your OS and added to PATH.")
        _log.info("Alternatively, run local forwarding: ssh -R 80:localhost:8000 serveo.net")
    except subprocess.CalledProcessError as e:
        _log.error("Failed to generate certificates: %s", e)

if __name__ == "__main__":
    generate_dev_certs()
