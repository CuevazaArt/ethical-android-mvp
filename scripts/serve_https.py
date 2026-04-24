import socket
import sys
import uvicorn
from pathlib import Path

def main():
    certs_dir = Path("certs")
    cert_file = certs_dir / "server.pem"
    key_file = certs_dir / "server.key"

    if not cert_file.exists() or not key_file.exists():
        print("Error: Certificates not found. Please run 'python scripts/gen_certs.py' first.")
        sys.exit(1)

    hostname = socket.gethostname()
    lan_ip = socket.gethostbyname(hostname)
    
    print("="*60)
    print(f"Ethos HTTPS en: https://{lan_ip}:8443")
    print("="*60)
    print("Note: If you get a certificate warning on mobile, tap 'Advanced' -> 'Proceed'.")
    print("If you cannot connect from mobile, ensure your Windows Firewall allows TCP port 8443.")
    print("="*60)

    uvicorn.run(
        "src.server.app:app",
        host="0.0.0.0",
        port=8443,
        ssl_certfile=str(cert_file),
        ssl_keyfile=str(key_file)
    )

if __name__ == "__main__":
    main()
