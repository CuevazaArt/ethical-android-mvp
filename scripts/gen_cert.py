"""
scripts/gen_cert.py — Genera certificado TLS auto-firmado para LAN HTTPS.

Uso:
    python scripts/gen_cert.py [--ip 192.168.1.65]

Genera:
    certs/server.key  — clave RSA-2048 privada
    certs/server.crt  — certificado X.509 con SAN (requerido por Chrome/Android)

Idempotente: si el cert existe y es válido por >7 días, no regenera.
Requiere: cryptography (ya en el entorno).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import ipaddress
import sys
from pathlib import Path

CERTS_DIR = Path(__file__).parent.parent / "certs"
KEY_FILE = CERTS_DIR / "server.key"
CERT_FILE = CERTS_DIR / "server.crt"
VALIDITY_DAYS = 365
MIN_REMAINING_DAYS = 7


def _load_existing_cert():
    """Return existing cert if valid for MIN_REMAINING_DAYS, else None."""
    if not CERT_FILE.exists() or not KEY_FILE.exists():
        return None
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        cert = x509.load_pem_x509_certificate(CERT_FILE.read_bytes())
        now = datetime.datetime.now(datetime.timezone.utc)
        remaining = (cert.not_valid_after_utc - now).days
        if remaining >= MIN_REMAINING_DAYS:
            return cert, remaining
    except Exception:
        pass
    return None


def _fingerprint(cert_bytes: bytes) -> str:
    digest = hashlib.sha256(cert_bytes).hexdigest().upper()
    return ":".join(digest[i:i+2] for i in range(0, len(digest), 2))


def generate_cert(ip: str) -> None:
    """Generate self-signed cert with SAN for the given LAN IP."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    # Key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Subject
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, ip),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ethos Kernel"),
    ])

    # SAN: IP + localhost + 127.0.0.1
    san_entries = [
        x509.IPAddress(ipaddress.IPv4Address(ip)),
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ]

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=VALIDITY_DAYS))
        .add_extension(
            x509.SubjectAlternativeName(san_entries),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    CERTS_DIR.mkdir(exist_ok=True)

    KEY_FILE.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    CERT_FILE.write_bytes(cert_pem)

    expires = cert.not_valid_after_utc.strftime("%Y-%m-%d")
    fp = _fingerprint(cert.public_bytes(serialization.Encoding.DER))
    print(f"✅ Cert generado: {CERT_FILE}")
    print(f"   SHA256 : {fp}")
    print(f"   Válido hasta: {expires}")
    print(f"   SAN   : IP:{ip}, DNS:localhost, IP:127.0.0.1")


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera cert TLS auto-firmado para LAN.")
    parser.add_argument("--ip", default="192.168.1.65", help="IP LAN del servidor (default: 192.168.1.65)")
    parser.add_argument("--force", action="store_true", help="Regenerar aunque el cert sea válido")
    args = parser.parse_args()

    if not args.force:
        existing = _load_existing_cert()
        if existing:
            cert, remaining = existing
            expires = cert.not_valid_after_utc.strftime("%Y-%m-%d")
            fp = _fingerprint(cert.public_bytes(__import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding.DER))
            print(f"✅ Cert existente válido ({remaining} días restantes, expira {expires})")
            print(f"   SHA256: {fp}")
            print("   Usa --force para regenerar.")
            return

    generate_cert(args.ip)
    print()
    print("▶ Arrancar servidor HTTPS:")
    print(f"  uvicorn src.server.app:app --host 0.0.0.0 --port 8443 --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt")
    print()
    print(f"▶ Acceder desde móvil:")
    print(f"  https://{args.ip}:8443/nomad")
    print()
    print("▶ Aceptar el cert en Android: abre la URL → 'Avanzado' → 'Continuar' (o instala el .crt en Ajustes → Seguridad → Instalar certificado)")


if __name__ == "__main__":
    main()
