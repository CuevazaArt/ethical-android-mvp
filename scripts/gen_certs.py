import os
import socket
import trustme
from pathlib import Path

def main():
    hostname = socket.gethostname()
    lan_ip = socket.gethostbyname(hostname)
    print(f"Generating certificates for: localhost, 127.0.0.1, {lan_ip}")

    ca = trustme.CA()
    server_cert = ca.issue_cert("localhost", "127.0.0.1", lan_ip)

    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)

    server_cert.private_key_pem.write_to_path(certs_dir / "server.key")
    server_cert.cert_chain_pems[0].write_to_path(certs_dir / "server.pem")
    
    ca.cert_pem.write_to_path(certs_dir / "ca.pem")

    print(f"Certificates generated in {certs_dir.absolute()}")
    print("For mobile browsers to accept it without warnings, you can install ca.pem as a trusted CA.")

if __name__ == "__main__":
    main()
