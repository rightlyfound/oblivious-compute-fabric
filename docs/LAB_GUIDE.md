# OCF Lab Guide: Confidential Computing & Constant-Time Algorithms

**For:** Computer Science educators, security researchers, and hands-on learners  
**Duration:** 60-90 minutes (full sequence) or modular (15-20 min labs)  
**Level:** Upper-level undergrad to graduate level

---

## Table of Contents

1. [Learning Objectives](#learning-objectives)
2. [Pre-Lab Setup](#pre-lab-setup)
3. [Conceptual Warm-Up: The Timing Attack](#conceptual-warm-up)
4. [Lab 1: The Reflective Correction Loop](#lab-1-reflective-correction-loop)
5. [Lab 2: Secret Matcher — Interactive Constant-Time](#lab-2-secret-matcher)
6. [Challenge Exercises](#challenge-exercises)
7. [Assessment & Discussion](#assessment-discussion)
8. [Instructor Notes](#instructor-notes)

---

## Learning Objectives

By the end of this lab, students will be able to:

- **Understand** how timing variations leak secrets (side-channel attacks)
- **Recognize** the difference between algorithmic correctness and microarchitectural security
- **Implement** branchless bitwise algorithms for constant-time execution
- **Verify** security properties through automated constraint checking
- **Deploy** and test secure computation in isolated environments
- **Apply** these concepts to real-world confidential computing scenarios

---

## Pre-Lab Setup

### System Requirements

```bash
# Check Python version (3.8+)
python3 --version

# Check g++ compiler (7.0+)
g++ --version

# Verify git is installed
git --version
```

### Clone and Navigate

```bash
git clone https://github.com/rightlyfound/oblivious-compute-fabric.git
cd oblivious-compute-fabric
```

### Verify Directory Structure

```bash
# Should see:
# demos/
#   ├── reflective_loop/
#   │   ├── run_demo.py
#   │   └── README.md
#   └── secret_matcher/
#       ├── client.html
#       ├── server.py
#       ├── secure_matcher.cpp
#       └── README.md

ls -la demos/*/
```

**✓ If all files are present, you're ready to begin.**

---

## Conceptual Warm-Up: The Timing Attack

**Duration:** 10-15 minutes

### The Problem: Information Leakage Through Time

#### Scenario
Two password managers want to verify if your stored password matches what you typed. The obvious approach:

```cpp
// VULNERABLE CODE
bool check_password(string stored, string typed) {
    if (stored == typed) {
        return true;   // Found a match!
    } else {
        return false;  // No match
    }
}
```

#### The Attack

An attacker cannot read the password directly. But they can **measure execution time**:

- **Fast execution (~10 cycles):** Probably matched → password is correct
- **Slow execution (~100+ cycles):** Probably didn't match → wrong password

Why? Because:
1. **Branch prediction:** CPU predicts which branch to take. Correct guess = fast. Wrong guess = slow (pipeline flush).
2. **Cache timing:** Different code paths hit/miss the cache differently.
3. **Power consumption:** More computation = more power drain (measurable).

#### Visualization

```
Traditional Code (VULNERABLE):
Input: "password123" vs "password123"
Execution: 10 cycles (FAST - branch predicted correctly)
Attacker inference: "Passwords match!"

Input: "password123" vs "wrongpass456"
Execution: 100 cycles (SLOW - branch mispredicted)
Attacker inference: "Passwords don't match!"

Timing alone reveals the result, even without reading memory!
```

### Discussion Question 1

**"How would an attacker measure execution time from outside your system?"**

*Possible answers:*
- Network timing (measure request/response latency)
- Power consumption (use EM probes on the chip)
- Cache timing (use Flush+Reload or Prime+Probe attacks)
- Electromagnetic radiation

---

## Lab 1: Reflective Correction Loop

**Duration:** 15-20 minutes  
**Objective:** Understand automated constraint validation and self-correcting code generation

### Step 1: Run the Loop

```bash
cd demos/reflective_loop
python3 run_demo.py
```

### Step 2: Observe the Output

Watch as the system:
1. **Generates code** (mock iteration 1)
2. **Profiles it** against constraints:
   - Timing leakage: ≤ 10 ns
   - Data-dependent branches: 0
   - Register spills: 0
3. **Fails arbitration** (too many violations)
4. **Generates reflection prompt** with raw telemetry
5. **Refines code** (iterations 2 → 3)
6. **Passes all constraints** → DEPLOYMENT READY

### Step 3: Trace the Iterations

Copy the output to a text file and annotate:

```
ITERATION 1:
- Timing Leakage: 1420 ns (FAIL - needs to be ≤ 10 ns)
- Branches: 3 (FAIL - needs to be 0)
- Spills: 2 (FAIL - needs to be 0)

ITERATION 2:
- Timing Leakage: 230 ns (FAIL - still too high)
- Branches: 0 (PASS!)
- Spills: 1 (FAIL - needs to be 0)

ITERATION 3:
- Timing Leakage: 0 ns (PASS!)
- Branches: 0 (PASS!)
- Spills: 0 (PASS!)
→ CONVERGENCE ACHIEVED
```

### Step 4: Discussion Question 2

**"Why can't the system just get it right the first time? What is it learning?"**

*Guided discussion:*
- Trade-offs between readability and security
- Microarchitectural constraints require specific code patterns
- Iterative refinement is more realistic than perfection on first try
- This mirrors real hardware debugging workflows

### Step 5: Code Analysis

Look at the reflection prompt (printed in the output):

```
--- MANDATORY DIRECTIVE ---
Rewrite the code segment using bitwise selection primitives or mask blending to 
completely eliminate data-dependent code paths. Do not use standard loop evaluations 
or conditional jumps.
```

**Question:** What is the system telling the LLM to do differently?

*Answer:* Replace `if/else` (branches) with bitwise XOR and masking (no branches).

---

## Lab 2: Secret Matcher — Interactive Constant-Time

**Duration:** 30-45 minutes  
**Objective:** Understand constant-time algorithms and verify host blindness in real-time

### Part A: Compilation & Standalone Testing

#### Step 1: Compile the Kernel

```bash
cd demos/secret_matcher
g++ -O2 -std=c++17 secure_matcher.cpp -o secure_matcher
```

#### Step 2: Test Matching Cases

```bash
# Test 1: Identical strings (should MATCH)
./secure_matcher "MySecret" "MySecret"
echo "Exit code: $?"  # Should be 0

# Test 2: Different strings (should NOT MATCH)
./secure_matcher "MySecret" "OtherSecret"
echo "Exit code: $?"  # Should be 1

# Test 3: Case sensitivity (should NOT MATCH)
./secure_matcher "MySecret" "mysecret"
echo "Exit code: $?"  # Should be 1

# Test 4: Empty strings (should MATCH)
./secure_matcher "" ""
echo "Exit code: $?"  # Should be 0

# Test 5: Special characters
./secure_matcher "p@ssw0rd!#" "p@ssw0rd!#"
echo "Exit code: $?"  # Should be 0
```

**✓ If all exit codes match expectations, the kernel is working correctly.**

### Part B: Interactive Web Demo

#### Step 1: Start the Server

```bash
# Terminal 1
python3 server.py
```

**Expected output:**
```
================================================================================
OBLIVIOUS SECRET MATCHER - UNTRUSTED HOST SIMULATION
================================================================================

[INFO] Server starting on http://localhost:8080
[INFO] Open your browser and navigate to http://localhost:8080
```

#### Step 2: Open the Web Interface

```bash
# Terminal 2 (or just open in browser)
open http://localhost:8080        # macOS
xdg-open http://localhost:8080    # Linux
# Or manually navigate to http://localhost:8080
```

#### Step 3: Guided Interaction (Scenario 1: Match)

**Setup:**
1. User A enters: `ConfidentialPassword2024`
2. User B enters: `ConfidentialPassword2024`

**Observation:**
- Watch the hash values appear in real-time
- Both hashes should be **identical**
- Click "COMPARE IN ENCLAVE"
- Watch Terminal 1 logs:
  ```
  [UNTRUSTED HOST] Receiving encrypted network payloads...
  [UNTRUSTED HOST] Payload A (encrypted): a1b2c3d4ef56789...
  [UNTRUSTED HOST] Payload B (encrypted): a1b2c3d4ef56789...  ← Same hash
  [UNTRUSTED HOST] Attempting to read system RAM during enclave execution...
  [UNTRUSTED HOST] RAM Inspection Result: [?? ?? ?? ?? ?? ??]
  [ENCLAVE] Executing branchless bitwise XOR comparison...
  [ENCLAVE] Result computed. Purging registers.
  [UNTRUSTED HOST] Received result from enclave: 1
  ```
- Result displays: **✓ MATCH DETECTED**

**Discussion Question 3:**

**"The server received encrypted hashes. Why couldn't it just decrypt them and read the passwords?"**

*Answer:* The encryption keys are held by the client and the enclave. The server never receives the decryption keys—only the encrypted payload to forward.

---

#### Step 4: Guided Interaction (Scenario 2: No Match)

**Setup:**
1. User A enters: `ConfidentialPassword2024`
2. User B enters: `DifferentPassword9999`

**Observation:**
- Watch the hash values: **They are DIFFERENT**
- Click "COMPARE IN ENCLAVE"
- Watch Terminal 1 logs:
  ```
  [UNTRUSTED HOST] Payload A (encrypted): a1b2c3d4ef56789...
  [UNTRUSTED HOST] Payload B (encrypted): 9z8x7c6v5b4a3...   ← Different hash
  [UNTRUSTED HOST] Attempting to read system RAM...
  [UNTRUSTED HOST] RAM Inspection Result: [?? ?? ?? ?? ?? ??]
  [ENCLAVE] Executing branchless bitwise XOR comparison...
  [ENCLAVE] Result computed. (Timing: 50ms - CONSTANT)
  [UNTRUSTED HOST] Received result from enclave: 0
  ```
- Result displays: **✗ NO MATCH**

**Critical Observation:**
- **Execution time is identical** (50ms both times)
- If timing varied, the server could infer the result
- By using constant-time code, we hide whether secrets matched

---

#### Step 5: The Server Blindness Proof

**Question:** "Is the server really blind to the plaintext?"

**Experiment:**

1. Add a test password with obvious patterns: `AAAABBBBCCCCDDDD`
2. Have User A enter this password
3. Have User B enter: `EEEEFFFFGGGGHHHHH`
4. Click compare
5. Look at Terminal 1 logs

**Observation:**
```
[UNTRUSTED HOST] Payload A: f7d3c9a2e1b5...  ← Encrypted; no pattern visible
[UNTRUSTED HOST] Payload B: 8b1f4e7a2c9d...  ← Encrypted; no pattern visible
```

The plaintext pattern `AAAABBBBCCCC` is **completely hidden** by the hash/encryption.

**Discussion Question 4:**

**"What if we removed the encryption step and sent raw plaintext to the server? What would happen?"**

*Answer:* The server would immediately see the passwords, defeating the entire security model.

---

### Part C: Constant-Time Verification

#### Step 1: Measure Execution Time

Run multiple times and check Terminal 1 logs:

```
Test 1 (Match):    [ENCLAVE] Result computed. (Timing: 50ms - CONSTANT)
Test 2 (No Match): [ENCLAVE] Result computed. (Timing: 50ms - CONSTANT)
Test 3 (Match):    [ENCLAVE] Result computed. (Timing: 50ms - CONSTANT)
```

**Observation:** Timing is always **exactly the same**, regardless of match/no-match.

**This is the security guarantee:** No timing variation = no information leaked.

#### Step 2: Inspect the Algorithm

Open `secure_matcher.cpp` and find the core comparison:

```cpp
uint32_t diff = secretA ^ secretB;
uint32_t match = ((diff | -diff) >> 31) ^ 1;
```

**Walkthrough:**

| Input | diff | (diff \| -diff) | >> 31 | ^ 1 | Result |
|-------|------|-----------------|--------|-----|--------|
| A == B (all 0s) | 0x00000000 | 0x00000000 | 0 | 1 | **1 (MATCH)** |
| A != B (non-zero) | 0xNONZERO | 0xFFFFFFFF | 1 | 0 | **0 (NO MATCH)** |

**Key insight:** Both branches execute **the same instructions** in **the same order**. No `if/else`. No branching. No timing leak.

---

## Challenge Exercises

### Challenge 1: Modify the Matcher Algorithm

**Difficulty:** Medium  
**Time:** 15-20 minutes

**Task:** Modify `secure_matcher.cpp` to compare two strings up to the first 5 characters only, but **still maintain constant-time execution**.

**Hint:** You'll need to loop exactly 5 times and XOR each character, then combine the results.

**Starter Code:**
```cpp
uint32_t diff = 0;
for (int i = 0; i < 5 && i < secretA.length() && i < secretB.length(); i++) {
    diff |= (secretA[i] ^ secretB[i]);
}
uint32_t match = ((diff | -diff) >> 31) ^ 1;
```

**Verification:**
- `./secure_matcher "password123" "password456"` should output MATCH (first 5 chars match)
- `./secure_matcher "passXXXXXX" "pasYYYYYYY"` should output NO_MATCH

### Challenge 2: Break the Constant-Time Guarantee

**Difficulty:** Hard  
**Time:** 20-30 minutes

**Task:** Intentionally rewrite the matcher using traditional `if/else` logic. Observe the difference.

**Instructions:**
1. Create a copy: `cp secure_matcher.cpp secure_matcher_vulnerable.cpp`
2. Modify the comparison to use branches:
```cpp
bool vulnerable_compare(string a, string b) {
    if (a == b) return true;
    else return false;
}
```
3. Compile both versions
4. Use a profiler to measure timing differences:
```bash
# Using Linux 'time' command
time ./secure_matcher "A" "A"
time ./secure_matcher_vulnerable "A" "A"
time ./secure_matcher "A" "B"
time ./secure_matcher_vulnerable "A" "B"
```

**Expected Finding:** Vulnerable version has **measurably different** execution times for match vs. no-match.

**Discussion:** Why is this a security problem?

### Challenge 3: Customize the Reflection Loop

**Difficulty:** Medium  
**Time:** 15-20 minutes

**Task:** Modify `demos/reflective_loop/run_demo.py` to change the constraint thresholds and observe convergence behavior.

**Instructions:**

1. Open `run_demo.py`
2. Find the `HARD_CONSTRAINTS` dictionary:
```python
HARD_CONSTRAINTS = {
    "MAX_TIMING_LEAKAGE_NS": 10,      # Change this to 100
    "DATA_DEPENDENT_BRANCHES": 0,
    "REGISTER_SPILLS": 0
}
```
3. Change `MAX_TIMING_LEAKAGE_NS` from 10 to 100
4. Run the demo again
5. Observe how the iteration telemetry changes

**Question:** Did the system converge faster? Why or why not?

**Advanced:** Try changing all constraints to be more strict (5 ns, still 0 branches, 0 spills). Does it still converge in 3 iterations?

### Challenge 4: Add a New Demo Test Case

**Difficulty:** Easy  
**Time:** 10-15 minutes

**Task:** Add a new test case to the secret matcher for edge cases.

**Instructions:**

1. Add these test cases to `secure_matcher.cpp`:
   - Very long strings (1000+ characters)
   - Unicode characters (emojis, accents)
   - Null bytes in the middle

2. Test and verify they still work:
```bash
./secure_matcher "$(python3 -c 'print("A"*1000)')" "$(python3 -c 'print("A"*1000)')"
./secure_matcher "café" "café"
./secure_matcher $'A\x00B' $'A\x00B'
```

**Discussion:** Should all of these produce consistent, constant-time results?

---

## Assessment & Discussion

### Post-Lab Reflection Questions

**For all students:**

1. **Explain the timing attack** in your own words. Why is execution time a security vulnerability?

2. **What is the purpose of the branchless algorithm?** How does `((diff | -diff) >> 31) ^ 1` prevent timing leaks?

3. **Why does the reflection loop need multiple iterations?** Could the LLM get it right on the first try?

4. **If the server is "blind," how does it know whether secrets matched or not?** What information is it receiving?

5. **Real-world application:** Name one scenario where you would use constant-time comparison (besides passwords).

---

### Group Discussion (15-20 minutes)

**Scenario:** Your company stores encrypted health records in the cloud. A researcher wants to query the database to find all records matching certain criteria, but doesn't want to reveal which records they're interested in.

**Questions:**
- What could go wrong if you used traditional code for the comparison?
- How would constant-time algorithms help?
- What other security concerns exist (beyond timing)?
- Could the reflection loop help automate security compliance?

---

### Assessment Rubric

**For graded lab submissions:**

| Criterion | Excellent (10-9) | Good (8-7) | Satisfactory (6-5) | Needs Work (<5) |
|-----------|------------------|-----------|-------------------|-----------------|
| **Understands timing attacks** | Explains with examples | Explains concept | Understands generally | Confused |
| **Implements constant-time code** | Correct & optimal | Correct | Works, suboptimal | Incorrect |
| **Verifies constant-time property** | Multiple tests passed | Basic tests passed | Partial success | Failed |
| **Explains reflection loop** | Deep understanding | Understands iterations | Recognizes pattern | Unclear |
| **Challenge exercises** | All completed correctly | Most correct | Some attempted | Not attempted |

---

## Instructor Notes

### Timing

- **Full sequence (all labs + challenges):** 90-120 minutes
- **Quick version (Labs 1-2 only):** 45-60 minutes
- **Individual labs:** 15-20 minutes each

### Common Student Misconceptions

1. **"If code is encrypted, it's secure."**
   - *Correction:* Encryption alone is not enough. Even encrypted data can leak information through timing, cache behavior, and memory access patterns.

2. **"Constant-time means the code is fast."**
   - *Correction:* Constant-time means execution time doesn't vary with input. It may be slower than optimized variable-time code.

3. **"The reflection loop is AI magic."**
   - *Correction:* It's a structured feedback system. The LLM reads telemetry and refines code based on constraints. Systematic, not magical.

4. **"You can detect if secrets matched by watching the network."**
   - *Correction:* Not if the output is minimal (1 bit) and constant-time. The server has no information to leak.

### Discussion Prompts

- What if we added a 1-5ms random delay to throw off timing attacks? Why is that not a complete solution?
- How would a cache-timing attack work on this system? (Flush+Reload, Prime+Probe)
- What happens if the attacker has physical access to the chip and can measure power consumption?
- Is constant-time always necessary, or only when secrets are involved?

### Extension Activities

**For advanced students:**

1. **Implement oblivious RAM (ORAM):** Hide which memory locations are accessed
2. **Add multi-party computation:** Extend the matcher to 3+ parties
3. **Integrate real profilers:** Use `perf` or VTune to measure actual CPU cycles
4. **Deploy to AWS Nitro Enclaves:** Move the demo to actual hardware

### Troubleshooting

**"The server won't start"**
- Port 8080 in use: `lsof -i :8080; kill -9 <PID>`
- Python version issue: ensure Python 3.8+
- Missing dependencies: none required (uses standard library only)

**"The constant-time guarantee seems broken"**
- Check if compiler optimizations are enabled (`-O2`)
- Run multiple times to ensure timing consistency
- Use `perf` or `time` command for precise measurements

**"Students don't understand the XOR trick"**
- Walk through a concrete example: `0x5 ^ 0x3 = 0x6` (binary visualization helps)
- Draw the truth table for XOR
- Explain why `(diff | -diff) >> 31` extracts the sign bit

### Suggested Adaptations by Level

**Introductory (High School / First-Year):**
- Skip the challenge exercises
- Focus on Labs 1-2 only
- Emphasize the conceptual warm-up

**Intermediate (Upper-Level Undergrad):**
- Complete all labs + 1-2 challenge exercises
- Discuss real-world applications
- Connect to cryptography / systems courses

**Advanced (Graduate / Research):**
- All labs + all challenges
- Integrate real hardware profilers
- Explore multi-party computation extensions
- Research paper connections (ORAM, side-channel attacks)

---

## References

- **Constant-Time Implementations:** [bearssl.org/ctmul.html](https://bearssl.org/ctmul.html)
- **Spectre & Meltdown:** [spectreattack.com](https://spectreattack.com/)
- **AWS Nitro Enclaves:** [aws.amazon.com/ec2/nitro/nitro-enclaves/](https://aws.amazon.com/ec2/nitro/nitro-enclaves/)
- **Intel SGX:** [www.intel.com/content/www/us/en/architecture-and-technology/software-guard-extensions.html](https://www.intel.com/content/www/us/en/architecture-and-technology/software-guard-extensions.html)
- **Confidential Computing Consortium:** [confidentialcomputing.io](https://confidentialcomputing.io/)

---

**Ready to teach confidential computing. Your feedback helps improve this guide.**
