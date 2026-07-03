# Oblivious Compute Fabric: Demos Directory Guide

The demos/ directory contains interactive, production-grade implementations designed to showcase advanced confidential computing mechanics, microarchitectural side-channel mitigations, and automated verification loops.

## Directory Tree

```text
demos/
├── README.md                        # Master documentation for all repository demos
├── reflective_loop/                 # Automated LLM Reflection & Arbitration Loop
│   ├── README.md                    # Operational metrics and context for the loop
│   └── run_demo.py                  # Python orchestration harness (Step 5 Framework)
└── secret_matcher/                  # Visual Cryptographic Matcher Engine
    ├── client.html                  # Dark-mode frontend for secure user input
    ├── secure_matcher.cpp           # Constant-time, branchless C++ matching kernel
    └── server.py                    # Untrusted host simulation logging RAM blindness
```

## Module Breakdowns

### 1. Reflective Loop Framework (demos/reflective_loop/)

This module demonstrates an automated continuous integration guardrail that enforces microarchitectural constraints on generated code blocks.

* **run_demo.py**: The core orchestration harness. It simulates a 3-iteration optimization cycle, evaluating code against hard gates (timing leakage variance ≤ 10 ns, zero data-dependent branches, zero register spills). It automatically structures raw telemetry failures into LLM reflection prompts until full metric convergence is achieved.
* **README.md**: Provides the technical specification sheet detailing the mathematical primitives used to achieve constant-time path convergence.

### 2. Secure Secret Matcher (demos/secret_matcher/)

A practical implementation of the *Confidential Millionaires' Problem*. It allows two untrusted parties to verify if their secret payloads match without ever exposing the raw inputs to the host operating system or system RAM.

* **secure_matcher.cpp**: A branchless C++ compilation unit that leverages bitwise XOR (⊕) and arithmetic bit-shifting (`((diff | -diff) >> 31) ^ 1`) to execute uniform clock-cycle comparisons.
* **server.py**: Acts as the untrusted hypervisor/host proxy. It captures incoming network data, routes it directly into the secure execution memory space, and loops dummy read cycles to prove total system blindness.
* **client.html**: A clean, accessible web layer that hashes client inputs locally before transmission, mirroring authentic zero-trust frontend architectures.

## Global Verification Matrix

All assets within the demos/ space are audited against the following core infrastructure invariants:

| Demo Target | Verification Metric | Enforced Boundary | Hardware Primitive |
|---|---|---|---|
| **Reflective Loop** | Static Compilation Gates | Zero Register Spilling | SIMD Allotment Audits |
| **Secret Matcher** | Side-Channel Immunity | Constant-Time Execution | Branchless Bitwise Masks |

## Deployment and Testing Guide

To spin up the entire demo framework sequentially from the repository root:

```bash
# 1. Execute the automated reflective correction loop
python3 demos/reflective_loop/run_demo.py

# 2. Compile the secure microarchitectural matching kernel
g++ -O2 -std=c++17 demos/secret_matcher/secure_matcher.cpp -o demos/secret_matcher/secure_matcher

# 3. Boot the untrusted host telemetry logging server
python3 demos/secret_matcher/server.py
```

## Quick Reference

### Running Individual Demos

**Reflective Correction Loop:**
```bash
cd demos/reflective_loop
python3 run_demo.py
```

Expected output: Iteration 1 & 2 fail → Iteration 3 converges → DEPLOYMENT READY

**Secret Matcher Server (Simulated Untrusted Host):**
```bash
cd demos/secret_matcher
python3 server.py
```

Opens web interface at `http://localhost:8080` with real-time system RAM inspection during oblivious computation.

**Secret Matcher Kernel (Standalone):**
```bash
cd demos/secret_matcher
g++ -O2 -std=c++17 secure_matcher.cpp -o secure_matcher
./secure_matcher "secret1" "secret2"
```

## Architecture Summary

### Reflective Loop Data Flow
```
Code Generation → Profiling → Constraint Validation → PASS? 
                                      ↓ NO
                            Telemetry Injection
                                      ↓
                            LLM Reflection Prompt
                                      ↓
                            Code Refinement (Loop)
```

### Secret Matcher Data Flow
```
Client Input → Local Hash → Network Transmission (Encrypted)
                                      ↓
                            Host (Blind to Plaintext)
                                      ↓
                            Enclave Core (Constant-Time XOR)
                                      ↓
                            Result (MATCH/NO_MATCH)
```

## Testing Checklist

- [ ] Reflective loop converges in exactly 3 iterations
- [ ] Secret matcher kernel executes in constant time
- [ ] Server logs show encrypted payloads only (host blindness)
- [ ] HTML client successfully hashes inputs before transmission
- [ ] No data-dependent branches detected in compiled matcher
- [ ] All demos run without external API keys or cloud dependencies

## Next Steps

1. **Run both demos** to verify they execute successfully
2. **Study the code comments** to understand constant-time algorithms
3. **Modify constraint thresholds** in `run_demo.py` to test convergence behavior
4. **Integrate real profilers** (perf, VTune) to measure actual hardware metrics
5. **Connect live LLM service** to replace mock telemetry with real code generation

---

For detailed technical documentation on each module, see:
- `reflective_loop/README.md` — Microarchitectural constraints and arbitration gates
- `secret_matcher/` — Individual file comments for algorithm details
