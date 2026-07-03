# Oblivious Compute Fabric: Getting Started Guide

Welcome to the **Oblivious Compute Fabric** deployment framework. This repository provides a blueprint for running high-integrity, side-channel-immune workloads inside hardware-isolated environments (Trusted Execution Environments / TEEs).

This guide serves as your end-to-end walkthrough to initialize, test, and run the complete secure simulation framework.

---

## 1. System Requirements & Architecture

Before executing the binaries, ensure your local development environment satisfies the following baseline dependencies:

* **Operating System:** Linux (Ubuntu 20.04 LTS or newer recommended) or macOS.
* **Compiler Toolchain:** g++ supporting C++17 optimization criteria (`-std=c++17`).
* **Runtime Engine:** Python 3.8 or newer (no external pip dependencies required).
* **Browser:** Any modern browser (Chrome, Firefox, Safari) for the web demo.

### Core Architectural Layers

The repository is split into two foundational demonstration zones:

1. **The Infrastructure Gatekeeper (`demos/reflective_loop/`):** An automated metrics-driven loop that intercepts raw code telemetry and arbitrates it against hardware safety constraints.

2. **The Execution Core (`demos/secret_matcher/`):** A branchless, constant-time calculation unit that solves the *Confidential Millionaires' Problem* without exposing memory states.

---

## 2. Sequential Execution Workflow

To evaluate the entire framework end-to-end, execute the following commands in sequence from your terminal root:

### Step A: Verify the Automated Reflection Pipeline

Verify how a continuous integration gatekeeper automatically flags microarchitectural timing leaks and forces code convergence:

```bash
# Execute the continuous telemetry feedback engine
python3 demos/reflective_loop/run_demo.py
```

**Expected Output:**
```
================================================================================
OBLIVIOUS COMPUTE FABRIC: AUTOMATED REFLECTIVE CORRECTION LOOP
================================================================================

[ℹ INFO] Running Verification Suite for Iteration #1

Telemetry Collected:
  Timing Leakage: 1420 ns
  Branches: 3
  Register Spills: 2

[✗ FAIL] Arbitration rejected code with 3 constraint violation(s)

--- (Loop continues) ---

[✓ PASS] Iteration #3 passed all architectural constraints!

================================================================================
✓ CONVERGENCE ACHIEVED
Pipeline locked. Code ready for enclave deployment.
================================================================================
```

**What This Demonstrates:**
- ✓ Automatic constraint validation
- ✓ Structured telemetry injection
- ✓ Code refinement through reflection prompts
- ✓ Convergence to deployment-ready state

---

### Step B: Compile the Constant-Time C++ Kernel

Compile the secure microarchitectural engine using high-level compiler optimizations (`-O2`) to lock down constant instruction-path mapping:

```bash
# Navigate to the secret matcher directory
cd demos/secret_matcher

# Compile the secure binary
g++ -O2 -std=c++17 secure_matcher.cpp -o secure_matcher

# Verify the binary was created
ls -lh secure_matcher
```

**Expected Output:**
```
-rwxr-xr-x  1 user  staff  12K Jul  3 23:30 secure_matcher
```

---

### Step C: Execute Direct Microarchitectural Tests

Verify that the underlying arithmetic shift logic (`((diff | -diff) >> 31) ^ 1`) operates cleanly across matching and non-matching payload invariants:

```bash
# Test 1: Matching Invariant
# Expected Output: MATCH_DETECTED, Exit Code: 0
./secure_matcher "AlphaSecret" "AlphaSecret"
echo "Kernel Exit Code: $?"

# Test 2: Mismatched Invariant
# Expected Output: NO_MATCH, Exit Code: 1
./secure_matcher "AlphaSecret" "BetaSecret"
echo "Kernel Exit Code: $?"

# Test 3: Empty String Edge Case
./secure_matcher "" ""
echo "Kernel Exit Code: $?"
```

**Expected Behavior:**

| Test Case | Command | Expected Exit Code | Expected Output |
|-----------|---------|-------------------|-----------------|
| **Match** | `secure_matcher "A" "A"` | 0 | MATCH_DETECTED |
| **No Match** | `secure_matcher "A" "B"` | 1 | NO_MATCH |
| **Empty Match** | `secure_matcher "" ""` | 0 | MATCH_DETECTED |

---

### Step D: Launch the Interactive Web Demo

Boot the untrusted host simulation server and open the interactive web interface:

```bash
# Terminal 1: Start the server
python3 server.py

# Expected output:
# ================================================================================
# OBLIVIOUS SECRET MATCHER - UNTRUSTED HOST SIMULATION
# ================================================================================
#
# [INFO] Server starting on http://localhost:8080
# [INFO] Open your browser and navigate to http://localhost:8080
```

```bash
# Terminal 2: Open the web interface in your browser
# Manually navigate to: http://localhost:8080
# Or use a command like:
open http://localhost:8080          # macOS
xdg-open http://localhost:8080      # Linux
```

**Interactive Demo Steps:**

1. **User A:** Type "MyPassword123" in the first input field
   - Observe the real-time SHA-256 hash appearing below the input
2. **User B:** Type "MyPassword123" in the second input field
   - Observe matching hash values
3. **Click:** "COMPARE IN ENCLAVE" button
4. **Observe Server Logs:** 
   - Watch Terminal 1 show encrypted payload reception
   - Watch attempted RAM inspection returning gibberish
   - Watch constant-time execution delay (50ms)
5. **Result:** Web interface displays `✓ MATCH DETECTED`
6. **Repeat:** Try different passwords to see `✗ NO MATCH` result

**Server Console Output During Comparison:**
```
================================================================================
[UNTRUSTED HOST] Receiving encrypted network payloads...
================================================================================
[UNTRUSTED HOST] Payload A (encrypted): a1b2c3d4ef5678...
[UNTRUSTED HOST] Payload B (encrypted): 9z8x7c6v5b4a3...
[UNTRUSTED HOST] Attempting to read system RAM during enclave execution...
[UNTRUSTED HOST] RAM Inspection Result: [?? ?? ?? ?? ?? ??]
[UNTRUSTED HOST] Status: Unable to read plaintext data. Access denied by hardware.

[ENCLAVE] Delegating to secure computation core...
[ENCLAVE] Decrypting payloads into secure registers...
[ENCLAVE] Executing branchless bitwise XOR comparison...
[ENCLAVE] Result computed. Purging registers.
[UNTRUSTED HOST] Received result from enclave: 1
[UNTRUSTED HOST] Result type: Single bit (no timing information leaked)
================================================================================
```

---

## 3. Global Security Verification Checklist

Every component within this fabric must uphold a zero-compromise microarchitectural footprint. When customizing or scaling these kernels, your code must never violate the following boundaries:

### Hard Constraints (Non-Negotiable)

- [ ] **Data-Dependent Branches:** Exactly 0
  - Conditional statements (`if/else`) must never evaluate secret values
  - All comparison logic must use branchless bitwise operations
  - Verify with: `objdump -d secure_matcher | grep -i "je\|jne\|jz\|jnz"`

- [ ] **Timing Side-Channels:** Zero Variance
  - Clock-cycle execution patterns must remain identical across all data inputs
  - Execution time must not correlate with input values
  - Verify with: CPU cycle profilers (perf, VTune, Intel PIN)

- [ ] **State Isolation:** Complete Memory Cleanup
  - Temporary values must be zeroed immediately after use
  - No secret data persists in registers, stack, or cache after computation
  - Verify with: Memory inspection during enclave execution

### Verification Commands

```bash
# 1. Check for conditional branches in compiled binary
objdump -d demos/secret_matcher/secure_matcher | grep -E "^\s+[0-9a-f]+:\s+(74|75|7c|7d|7e|7f)" && \
  echo "WARNING: Data-dependent branches detected!" || \
  echo "✓ PASS: No data-dependent branches found"

# 2. Measure execution timing (requires Intel VTune or perf)
# perf stat -e cycles,instructions,cache-misses ./demos/secret_matcher/secure_matcher A A

# 3. Inspect register usage
objdump -d demos/secret_matcher/secure_matcher | grep -E "rsp|rax|rbx" | wc -l
```

---

## 4. Architecture Deep-Dive

### The Constant-Time Algorithm

The heart of the secure matcher is this branchless comparison:

```cpp
uint32_t diff = secretA ^ secretB;              // XOR: 0 if equal
uint32_t match = ((diff | -diff) >> 31) ^ 1;   // Constant-time normalization
```

**How It Works:**

1. **XOR Difference:** If inputs are identical, `diff = 0x00000000`. If different, `diff = 0xNONZERO`.
2. **Arithmetic Shift:** `(diff | -diff)` sets all bits if `diff != 0`, leaves all zeros if `diff == 0`.
3. **Sign Extraction:** `>> 31` extracts the sign bit (1 if non-zero, 0 if zero).
4. **Inversion:** `^ 1` flips the result to get 1 for match, 0 for no match.
5. **Result:** Every instruction executes every time, regardless of input. No branching. No timing leak.

**Why Traditional Code Leaks:**

```cpp
// VULNERABLE: Branch prediction leaks match status
if (secretA == secretB) {
    return 1;  // Fast: ~10 cycles (correct prediction)
} else {
    return 0;  // Slow: ~100 cycles (misprediction penalty)
}
```

An attacker timing this function can:
- Fast execution (~10 cycles) → Secrets matched
- Slow execution (~100 cycles) → Secrets didn't match

---

### The Reflection Loop Architecture

The `run_demo.py` orchestrator demonstrates how an LLM-driven system ensures code compliance:

```
Code Generation → Profiling → Constraint Validation → PASS?
                                    ↓ NO
                          Telemetry Injection
                                    ↓
                          LLM Reflection Prompt
                                    ↓
                          Code Refinement (Loop)
```

**The Three Iterations:**

| Iteration | Timing (ns) | Branches | Spills | Status |
|-----------|-------------|----------|--------|--------|
| #1 | 1420 | 3 | 2 | ✗ FAIL |
| #2 | 230 | 0 | 1 | ✗ FAIL |
| #3 | 0 | 0 | 0 | ✓ PASS |

Each failure generates a structured reflection prompt that the LLM reads and uses to improve the next iteration.

---

## 5. Next Steps & Extensions

### Immediate Actions (30 minutes)
- [ ] Run all three demos (reflective loop, command-line matcher, web interface)
- [ ] Verify output matches expected results
- [ ] Read inline comments in `secure_matcher.cpp`
- [ ] Study server logs to understand host blindness

### Short-Term (1-2 hours)
- [ ] Modify constraint thresholds in `run_demo.py` and observe convergence behavior
- [ ] Change the reflection prompt template to test LLM response patterns
- [ ] Add new test cases to the secret matcher
- [ ] Customize the web UI colors and styling

### Medium-Term (1 day)
- [ ] Integrate real CPU profilers (Intel VTune, Linux perf)
- [ ] Connect to a live LLM service (OpenAI, Claude, Ollama)
- [ ] Deploy the kernel to AWS Nitro Enclaves or Intel SGX
- [ ] Add cryptographic attestation document generation

### Long-Term (Production)
- [ ] Extend to multi-party computation (3+ parties)
- [ ] Bind validated kernels to hardware attestation
- [ ] Integrate into continuous deployment pipelines
- [ ] Monitor for constraint violations in production
- [ ] Scale to distributed enclave networks

---

## 6. Troubleshooting

### Problem: "Python command not found"
```bash
# Verify Python 3 is installed
python3 --version

# If not installed:
# Ubuntu/Debian: sudo apt-get install python3
# macOS: brew install python3
```

### Problem: "g++ command not found"
```bash
# Verify g++ is installed
g++ --version

# If not installed:
# Ubuntu/Debian: sudo apt-get install build-essential
# macOS: xcode-select --install
```

### Problem: "Port 8080 already in use"
```bash
# Option 1: Kill the process using port 8080
lsof -i :8080
kill -9 <PID>

# Option 2: Use a different port
# Modify server.py: httpd = HTTPServer(('localhost', 9000), ...)
```

### Problem: "Connection refused" when opening http://localhost:8080
```bash
# Verify the server is running
# Check Terminal 1 for error messages
# Make sure you ran: python3 demos/secret_matcher/server.py
# Try again in 2 seconds (server takes a moment to start)
```

### Problem: "Compilation error: -std=c++17 not recognized"
```bash
# Use alternative C++ standard flag
g++ -O2 -std=c++1z demos/secret_matcher/secure_matcher.cpp -o demos/secret_matcher/secure_matcher

# Or upgrade g++ to version 7 or newer
g++ --version
```

---

## 7. Security Model Summary

| Component | Threat Model | Defense | Verified By |
|-----------|--------------|---------|------------|
| **Client Input** | Host interception | Client-side hashing | Browser console inspection |
| **Network Transport** | Eavesdropping | Encrypted payloads | Server logs (encrypted only) |
| **Host System** | RAM inspection | Enclave boundary | Attempted inspection returns gibberish |
| **Computation** | Timing side-channel | Constant-time algorithm | Identical execution every time |
| **Code Quality** | Functional bugs | Automated constraints | Reflective loop arbitration |

---

## 8. File Reference

```
oblivious-compute-fabric/
├── GETTING_STARTED.md               # This file
├── README.md                        # High-level overview
├── demos/
│   ├── README.md                    # Demos directory guide
│   ├── reflective_loop/
│   │   ├── run_demo.py             # Execute this first
│   │   └── README.md               # Technical deep-dive
│   └── secret_matcher/
│       ├── client.html             # Open in browser
│       ├── server.py               # Run in Terminal 1
│       ├── secure_matcher.cpp      # Compile this
│       └── README.md               # Detailed documentation
├── ocf_agent.rs                     # Rust agent prototype
├── ocf_daemonset.yaml               # Kubernetes deployment
├── ocflib.py                        # Python library
├── ole_vulkan_complete.cpp          # GPU acceleration
└── rfa_kernel.comp                  # Shader kernels
```

---

## 9. Key Concepts Recap

**Constant-Time Execution:** Code that takes identical CPU cycles regardless of secret input values. This prevents timing side-channel attacks.

**Host Blindness:** The untrusted host system receives only encrypted data and single-bit results, making it mathematically unable to infer secrets.

**Automated Verification:** Continuous integration loops that check code against hard constraints before deployment, with LLM-driven self-correction on failures.

**Microarchitectural Security:** Defense against low-level attacks (cache timing, branch prediction, power consumption) through branchless algorithms and constant-time primitives.

---

## 10. Resources & References

- **AWS Nitro Enclaves Documentation:** [aws.amazon.com/ec2/nitro/nitro-enclaves/](https://aws.amazon.com/ec2/nitro/nitro-enclaves/)
- **Intel SGX Documentation:** [www.intel.com/content/www/us/en/architecture-and-technology/software-guard-extensions.html](https://www.intel.com/content/www/us/en/architecture-and-technology/software-guard-extensions.html)
- **Constant-Time Crypto:** [bearssl.org/ctmul.html](https://bearssl.org/ctmul.html)
- **Spectre & Meltdown:** [spectreattack.com](https://spectreattack.com/)
- **Confidential Computing Consortium:** [confidentialcomputing.io](https://confidentialcomputing.io/)
- **Oblivious RAM (ORAM):** [eprint.iacr.org/papers/](https://eprint.iacr.org/papers/)

---

## 11. Support & Contributing

**Questions?**
- Check the detailed README in each demo directory
- Review inline code comments in `secure_matcher.cpp` and `run_demo.py`
- Verify system requirements match your environment

**Found an issue?**
- Check the Troubleshooting section above
- Verify all dependencies are installed
- Make sure you're following the sequential execution workflow

**Ready to contribute?**
- Extend the reflection loop with live LLM integration
- Add real hardware profiler support
- Deploy to actual enclave environments (Nitro, SGX)
- Implement multi-party computation

---

**You're now ready to explore the Oblivious Compute Fabric. Execute the demos, study the code, and discover how computation can happen over secrets while revealing nothing. Welcome.**
