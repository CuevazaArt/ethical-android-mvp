import os
from datetime import datetime, timedelta
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_local_certs():
    """
    Generates self-signed certificates using pure Python (cryptography lib).
    Required for Nomad Vessel to access camera/mic over LAN.
    """
    cert_dir = Path(".certs")
    cert_dir.mkdir(exist_ok=True)
    
    key_file = cert_dir / "key.pem"
    cert_file = cert_dir / "cert.pem"
    
    print(f"[*] Generating local certificates in {cert_dir} using 'cryptography' library...")
    
    # 1. Generate Private Key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Generate Certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Nomadic"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Ethos"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Antigravity Fleet"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        # Valid for 1 year
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
    ).sign(key, hashes.SHA256())

    # 3. Write to files
    with open(key_file, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("[+] Certificates generated successfully!")
    print(f"    Key:  {key_file}")
    print(f"    Cert: {cert_file}")

if __name__ == "__main__":
    generate_local_certs()
