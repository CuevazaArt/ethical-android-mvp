import os
import subprocess
from pathlib import Path

def generate_local_certs():
    """
    Generates self-signed certificates for local HTTPS communication.
    Required for Nomad Vessel to access camera/mic over LAN.
    """
    cert_dir = Path(".certs")
    cert_dir.mkdir(exist_ok=True)
    
    key_file = cert_dir / "key.pem"
    cert_file = cert_dir / "cert.pem"
    
    print(f"[*] Generating local certificates in {cert_dir}...")
    
    # Check if openssl is available
    try:
        subprocess.run(["openssl", "version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] Error: OpenSSL not found. Please install OpenSSL or Git for Windows (which includes it).")
        return

    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", str(key_file),
        "-out", str(cert_file), "-days", "365", "-nodes",
        "-subj", "/CN=localhost"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("[+] Certificates generated successfully!")
        print(f"    Key:  {key_file}")
        print(f"    Cert: {cert_file}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error generating certificates: {e}")

if __name__ == "__main__":
    generate_local_certs()
