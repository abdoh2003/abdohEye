import psutil
import time
import json
from hashlib import sha256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from pathlib import Path
import os

class AbdohEyeMonitor:
    def __init__(self, interval=5, log_dir="logs"):
        self.interval = interval
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.last_hash = None
        
        # Initialize cryptographic keys
        self._init_crypto()

    def _init_crypto(self):
        key_path = self.log_dir / "keys"
        key_path.mkdir(exist_ok=True)
        
        priv_key_file = key_path / "private_key.pem"
        pub_key_file = key_path / "public_key.pem"

        if not priv_key_file.exists():
            from cryptography.hazmat.primitives.asymmetric import rsa
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            with open(priv_key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            public_key = private_key.public_key()
            with open(pub_key_file, "wb") as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))

    def get_system_metrics(self):
        """Collect system metrics"""
        return {
            "timestamp": time.time(),
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": psutil.net_io_counters()._asdict(),
            "processes": len(psutil.pids())
        }

    def create_log_entry(self, data):
        """Create tamper-evident log entry"""
        entry = {
            "data": data,
            "previous_hash": self.last_hash,
        }
        
        # Create hash chain
        entry_str = json.dumps(entry, sort_keys=True).encode()
        current_hash = sha256(entry_str).hexdigest()
        entry["current_hash"] = current_hash
        
        # Digital signature
        with open(self.log_dir / "keys" / "private_key.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
        
        signature = private_key.sign(
            json.dumps(entry).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        entry["signature"] = signature.hex()
        self.last_hash = current_hash
        return entry

    def log_metrics(self):
        """Save metrics to encrypted log"""
        log_file = self.log_dir / f"abdohEye_log_{int(time.time())}.json"
        
        metrics = self.get_system_metrics()
        entry = self.create_log_entry(metrics)
        
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def start_monitoring(self):
        """Start continuous monitoring"""
        try:
            while True:
                self.log_metrics()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

def main():
    monitor = AbdohEyeMonitor()
    print("Starting abdohEye system monitor...")
    monitor.start_monitoring()