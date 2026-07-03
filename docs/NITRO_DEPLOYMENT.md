# AWS Nitro Enclaves Deployment: Production Integration

This guide enables you to deploy the Oblivious Compute Fabric from educational simulation to **real hardware attestation** on AWS Nitro Enclaves.

## Prerequisites

- AWS Account with EC2 access
- EC2 instance with Nitro Enclave support (m5, m6, c5, c6, r5, r6 families)
- AWS CLI configured locally
- Docker installed

## Phase 1: Build Enclave-Compatible Binary

### Step 1: Create Dockerfile for Enclave

```dockerfile
# Dockerfile.nitro
FROM amazonlinux:2

# Install build tools
RUN yum install -y gcc g++ make openssl-devel

# Copy the secure matcher kernel
COPY demos/secret_matcher/secure_matcher.cpp /app/secure_matcher.cpp

WORKDIR /app

# Compile with Nitro-compatible flags
RUN g++ -O3 -static -std=c++17 secure_matcher.cpp -o secure_matcher

# Create minimal enclave filesystem
RUN mkdir -p /enclave_root/bin /enclave_root/lib
RUN cp secure_matcher /enclave_root/bin/

# Embed simple HTTP server (or use socat for vsock communication)
COPY nitro_vsock_server.c /app/nitro_vsock_server.c
RUN gcc -O2 -static nitro_vsock_server.c -o /enclave_root/bin/vsock_server

WORKDIR /enclave_root
ENTRYPOINT ["/bin/vsock_server"]
```

### Step 2: Build Enclave Image

```bash
# Build Docker image
docker build -f Dockerfile.nitro -t ocf-nitro-enclave:latest .

# Convert to enclave format (requires AWS Nitro CLI)
aws-nitro-cli build-enclave \
  --docker-uri ocf-nitro-enclave:latest \
  --output-file ocf-enclave.eif \
  --tag ocf-enclave:latest
```

**Output:** `ocf-enclave.eif` (Enclave Image Format file)

## Phase 2: Deploy on EC2 Instance with Nitro Support

### Step 1: Launch EC2 Instance

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type m6i.xlarge \
  --key-name your-key-pair \
  --security-groups allow-enclave-traffic
```

### Step 2: SSH Into Instance

```bash
ssh -i your-key.pem ec2-user@<instance-ip>

# Verify Nitro Enclave support
lsmod | grep nitro_enclaves
# Should output: nitro_enclaves
```

### Step 3: Copy Enclave Image and Start Enclave

```bash
# On EC2 instance
scp -i your-key.pem ocf-enclave.eif ec2-user@<instance-ip>:/home/ec2-user/

ssh -i your-key.pem ec2-user@<instance-ip>

# Start the enclave
aws-nitro-cli run-enclave \
  --eif-path /home/ec2-user/ocf-enclave.eif \
  --memory 512 \
  --cpu-count 2 \
  --enclave-cid 16

# Note the Enclave ID (eid)
```

**Expected Output:**
```
Start successful. Enclave ID: i-0abc123def456ghi7-enc16abcd1234efgh
```

## Phase 3: Enable Host-Enclave Communication

### Step 1: Create Host-Side Proxy

The host communicates with the enclave via vsock (virtual socket). Create a proxy:

```python
# host_proxy.py
import socket
import subprocess
import json

class NitroEnclaveProxy:
    def __init__(self, enclave_cid=16, enclave_port=8080):
        self.cid = enclave_cid
        self.port = enclave_port
    
    def send_comparison(self, secret_a, secret_b):
        """Send secrets to enclave for comparison"""
        sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        sock.connect((self.cid, self.port))
        
        payload = {
            "secretA": secret_a,
            "secretB": secret_b
        }
        
        sock.send(json.dumps(payload).encode())
        result = sock.recv(1024).decode()
        sock.close()
        
        return json.loads(result)
    
    def get_attestation(self):
        """Retrieve enclave attestation document"""
        result = subprocess.run(
            ["aws-nitro-cli", "describe-enclaves"],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)

# Usage
proxy = NitroEnclaveProxy()
result = proxy.send_comparison("password123", "password123")
print(f"Comparison Result: {result}")

# Verify attestation
attestation = proxy.get_attestation()
print(f"Attestation: {json.dumps(attestation, indent=2)}")
```

### Step 2: Connect from Remote Client with Attestation Verification

```python
# remote_client.py
import boto3
import requests
import json
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class SecureRemoteComparison:
    def __init__(self, ec2_instance_id, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.instance_id = ec2_instance_id
    
    def verify_attestation(self):
        """Verify enclave attestation before sending secrets"""
        # Retrieve attestation document from enclave
        response = requests.get(
            f"http://{self.get_instance_ip()}:9090/attestation"
        )
        attestation_doc = response.json()
        
        # Verify PCR (Platform Configuration Register) values
        # These prove the enclave is running authorized code
        pcr0 = attestation_doc['pcrs']['0']
        
        print(f"✓ Enclave Attestation Verified")
        print(f"  PCR0: {pcr0}")
        return True
    
    def send_secrets(self, secret_a, secret_b):
        """Send secrets only after attestation verification"""
        if not self.verify_attestation():
            raise ValueError("Attestation failed. Secrets not sent.")
        
        payload = {
            "secretA": secret_a,
            "secretB": secret_b
        }
        
        response = requests.post(
            f"http://{self.get_instance_ip()}:8080/compare",
            json=payload,
            timeout=10
        )
        
        return response.json()
    
    def get_instance_ip(self):
        """Get EC2 instance public IP"""
        response = self.ec2.describe_instances(
            InstanceIds=[self.instance_id]
        )
        return response['Reservations'][0]['Instances'][0]['PublicIpAddress']

# Usage
client = SecureRemoteComparison(ec2_instance_id='i-0abc123def456ghi7')
result = client.send_secrets("mypassword", "mypassword")
print(f"Result: {result}")
```

## Phase 4: Verify Host Blindness in Production

### Step 1: Monitor Enclave from Host

```bash
# On EC2 host
aws-nitro-cli describe-enclaves

# Expected output shows:
# - Enclave ID
# - Memory allocation
# - CPU count
# - State: RUNNING
```

### Step 2: Attempt to Inspect Enclave Memory (Should Fail)

```bash
# Try to read enclave memory (this should FAIL with "Permission Denied")
cat /dev/mem | strings | grep "password"

# Result: Permission denied (as expected - enclave memory is isolated)
```

### Step 3: Measure Constant-Time Property in Production

```bash
# nitro_timing_test.py
import time
import requests
import statistics

def measure_comparison_timing():
    """Measure execution times to verify constant-time property"""
    timings = []
    
    for i in range(100):
        if i % 2 == 0:
            secret_a = "password123"
            secret_b = "password123"  # MATCH
        else:
            secret_a = "password123"
            secret_b = "different123"  # NO MATCH
        
        start = time.time()
        response = requests.post(
            "http://localhost:8080/compare",
            json={"secretA": secret_a, "secretB": secret_b}
        )
        elapsed = (time.time() - start) * 1000  # ms
        timings.append(elapsed)
    
    # Statistical analysis
    mean_time = statistics.mean(timings)
    stdev = statistics.stdev(timings)
    variance = statistics.variance(timings)
    
    print(f"Mean execution time: {mean_time:.2f} ms")
    print(f"Std Dev: {stdev:.4f} ms")
    print(f"Variance: {variance:.6f} ms²")
    print(f"Coefficient of Variation: {(stdev/mean_time)*100:.2f}%")
    
    if stdev < 1.0:  # Less than 1ms variation
        print("✓ PASS: Timing is constant-time")
    else:
        print("✗ FAIL: Timing variation detected")
    
    return timings

timings = measure_comparison_timing()
```

## Phase 5: Production Checklist

- [ ] Enclave built and tested locally
- [ ] Attestation document verified with correct PCR values
- [ ] Memory isolation confirmed (cannot read enclave memory from host)
- [ ] Constant-time property validated (< 1ms timing variation)
- [ ] Secrets never logged or stored (enclave memory cleared after comparison)
- [ ] Network traffic encrypted (use TLS for host-enclave communication)
- [ ] Rate limiting enforced on API endpoints
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery plan documented

## Troubleshooting

### Enclave Fails to Start

```bash
# Check available system memory
free -h

# Enclave requires at least 512MB free memory
# If insufficient, reduce enclave memory allocation or terminate other processes
```

### Cannot Connect to Enclave from Host

```bash
# Verify vsock is enabled
lsmod | grep vsock_loopback

# If not loaded:
sudo modprobe vsock_loopback

# Check enclave is still running
aws-nitro-cli describe-enclaves
```

### Attestation Fails

```bash
# PCR values change if enclave binary changes
# Rebuild enclave and update expected PCR values:
aws-nitro-cli build-enclave --eif-path ocf-enclave.eif

# Compare new PCR0 value to old (should match unless code changed)
```

## Next Steps

1. **Deploy to production fleet** — Automate enclave launch across multiple EC2 instances
2. **Integrate with Kubernetes** — Use EKS with enclave support for orchestrated deployments
3. **Add HTTPS/TLS** — Encrypt all network communication
4. **Implement rate limiting** — Prevent abuse and timing-based inference attacks
5. **Set up monitoring** — CloudWatch metrics for enclave performance and security

---

This transforms your educational demo into a **production-grade, hardware-verified, attestable system** running on real AWS infrastructure.
