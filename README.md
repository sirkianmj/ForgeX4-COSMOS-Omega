# ForgeX4 COSMOS-Ω: Autonomous Synthesis of Formally Verified, Multi-Physics Containment Automata

<p align="center">
  <img src="https://img.shields.io/badge/Project%20Status-vNext%20Validated%20(115%20Targets)-brightgreen.svg" alt="Project Status">
  <img src="https://img.shields.io/badge/Lead%20Researcher-Kian%20Mansouri%20Jamshidi-blue.svg" alt="Lead Researcher">
  <a href="https://doi.org/10.36227/techrxiv.176055396.69060312/v1">
    <img src="https://img.shields.io/badge/DOI-10.36227%2Ftechrxiv.176055396.69060312%2Fv1-blue.svg" alt="TechRxiv DOI">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Kernel%20Enforcement-libseccomp%20%7C%20Landlock%20v10-orange.svg" alt="Kernel Enforcement">
  <img src="https://img.shields.io/badge/Verification-Z3%20SMT%20%7C%20Strict%20SHA--256-informational.svg" alt="Formal Verification">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL%20v3.0-blue.svg" alt="License: AGPL v3.0">
  </a>
</p>

<p align="center">
  <strong>A Multi-Physics Digital Immune System for Autonomous, Formally Verified Containment Across Heterogeneous Real-World Software.</strong>
</p>

---

> [!IMPORTANT]
> **vNext Milestone Validated (`f10dab7dbf054b8d`):** COSMOS-Ω has evolved from single-library calibration (`cJSON` / `mixed_workload.c`) into a **generalist kernel containment foundry** validated across **115 distinct real-world targets** (42 C/C++ libraries & parsers, 35 POSIX/document CLIs, 20 network daemons & multi-process clusters, and 18 AI/agent tool runners). Across **5 independent seeds (`575` target runs, `740` attack probes)**, COSMOS-Ω achieves **99.48% strict joint pass (`572/575`)**, **100.00% (`115/115`) zero-shot Leave-23-Targets-Out (`LOTO`) transfer**, and **575/575 strict native SHA-256 ledger integrity**, outperforming 2-float quantile bounds (`49.74%`, $p = 2.759 \times 10^{-48}$) and random policy search (`59.30%`, $p = 4.227 \times 10^{-32}$).

---

## 1. Overview: From Reactive Patching to Generative Kernel Containment

The prevailing doctrine of reactive cybersecurity—a resource-intensive cycle of patching vulnerabilities post-attack—is economically unsustainable against zero-day exploits, supply-chain compromises, living-off-the-land (LotL) execution, and automated attacks.

**ForgeX4 COSMOS-Ω** presents a practical, validated alternative: a **Multi-Physics Digital Immune System** that does not rewrite application source code, but **autonomously synthesizes minimal-privilege, formally verified containment policies (`PolicyIR`)** enforced directly by the Linux kernel.

Led by Project Director **Kian Mansouri Jamshidi**, this repository contains the complete vNext generalist engine (`cosmos/vnext/`), the C/Linux kernel enforcer (`sandbox/cosmos_enforcer.c`), declarative 115-target catalogs (`targets/catalog/`), independent verification scripts, unit tests, and immutable cryptographic ledgers.

---

## 2. Architecture & Core Scientific Contributions

```text
                       COSMOS-Ω vNext Pipeline

  ┌──────────────────────────────────────────────────────────────────┐
  │                     Host Controller (Mac / Linux)                │
  │                                                                  │
  │   [PolicyIR Candidate] ──► [Z3 SMT Formal Invariant Gate]        │
  │                                      │ (Proved Safe in <1 ms)    │
  │                                      ▼                           │
  │   [Cross-Target Digital Twin] ──► [Online Surrogate Screening]   │
  │                                      │ (kernel_hash Memoized)    │
  │                                      ▼                           │
  │                      [Pre-Warmed Sandbox HTTP / Socket]          │
  └──────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │            Linux Kernel Sandbox (cosmos-sandbox:v3)              │
  │                                                                  │
  │   Target Process (NGINX, Gunicorn, Redis, Git, Ghostscript, C)   │
  │     ├── Syscalls & Net: libseccomp USER_NOTIF (execve, fork,     │
  │     │                   bind vs outbound connect, fchmod, ptrace)│
  │     ├── Filesystem:     Landlock LSM (ABI v10 path isolation)    │
  │     ├── Resource Caps:  POSIX setrlimit (CPU, AS, FSIZE, NOFILE) │
  │     └── Physics:        wait4() kernel rusage (cpu_ms, rss_kb)   │
  └──────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │              Immutable SHA-256 Audit Ledger                      │
  │   [Deepcopied Record] ──► [SHA-256 Digest] ──► [Chained Event]   │
  └──────────────────────────────────────────────────────────────────┘
```

1. **Multi-Physics Evolutionary Defense (MPED) + Capability Containment:**
   Bridges discrete kernel capability enforcement (`libseccomp` `SECCOMP_RET_USER_NOTIF` + **Landlock ABI v10**) with continuous execution physics (`wait4()` `cpu_ms`, `max_rss_kb`, `wall_ms`, page faults). Low-and-slow mimicry attacks (`<1%` CPU, `<10 MB` RAM) are killed at the syscall/filesystem boundary in milliseconds, while algorithmic and resource exhaustion bombs are bounded by kernel rlimits and physics envelopes.
2. **Static Formal Verification (Z3 SMT Solver):**
   Every candidate `PolicyIR` is checked by Z3 against non-escalation, anti-exfiltration (`allow_net_bind` vs `allow_net_outbound`, `fs_unrestricted`), and benign floor invariants *before* touching the sandbox.
3. **Zero-Shot Cross-Target Digital Twin:**
   A thread-safe `CrossTargetDigitalTwin` trained on calibration telemetry and policy structure predicts policy fitness across heterogeneous archetypes, enabling zero-shot transfer to completely unseen software targets (`LOTO-23`).
4. **Strict Tamper-Evident Provenance (`AuditLedger`):**
   Every synthesis decision, Z3 proof hash, baseline comparison, and per-probe `cpu_ms`/`wall_ms` outcome is deep-copied at record time into an unbroken, strictly verifiable SHA-256 hash chain.

---

## 3. Large-Scale Empirical Validation: 115 Real Targets (`5` Seeds = `575` Runs)

Canonical verified ledger: [`artifacts/vnext_logs/ledger_journal115_20261121_103606_f10dab7dbf054b8d.json`](artifacts/vnext_logs/ledger_journal115_20261121_103606_f10dab7dbf054b8d.json)  
All 5 seeds (`100`–`104`) ran sequentially on a single thermal-safe worker (`--workers 1 --pace-ms 25`, total `1274.2s`).

### 3.1. Archetype Summary vs. Baselines

| Software Archetype | Targets | Runs ($5\times$) | COSMOS Benign | COSMOS Block | 2-Float Block | COSMOS Joint Pass | 2-Float Joint Pass | Random Joint Pass |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Parsers & Native Engines** | 42 | 210 | **100.0%** | **100.0%** | 65.9% | **100.0%** (`210/210`) | 54.8% (`115/210`) | 68.1% (`143/210`) |
| **POSIX & System CLIs** | 35 | 175 | **100.0%** | **100.0%** | 45.7% | **100.0%** (`175/175`) | 31.4% (`55/175`) | 58.9% (`103/175`) |
| **Networked Daemons** | 20 | 100 | **100.0%** | **97.0%** | 76.0% | **97.0%** (`97/100`) | 71.0% (`71/100`) | 40.0% (`40/100`) |
| **AI / Agent Tool Runners** | 18 | 90 | **100.0%** | **100.0%** | 63.0% | **100.0%** (`90/90`) | 50.0% (`45/90`) | 61.1% (`55/90`) |
| **Composite Total** | **115** | **575** | **100.0%** | **99.48%** | — | **99.48%** (`572/575`) | **49.74%** (`286/575`) | **59.30%** (`341/575`) |

*Strict Joint Pass = `100%` benign functional pass + `100%` attack containment + `z3_verified == True`.*

### 3.2. Statistical Significance (Non-Parametric Mann–Whitney U)

| Baseline Comparison | Metric Evaluated | Sample Size | Mann–Whitney U $p$-value |
| :--- | :--- | :---: | :---: |
| **COSMOS-Ω vs. 2-Float Quantile Sentinel** | Strict Joint Pass | $575$ vs. $575$ | **$p = 2.759 \times 10^{-48}$** |
| **COSMOS-Ω vs. Random Policy Search** | Strict Joint Pass | $575$ vs. $575$ | **$p = 4.227 \times 10^{-32}$** |
| **COSMOS-Ω vs. Random Policy Search** | Multi-Objective Fitness | $575$ vs. $575$ | **$p = 5.370 \times 10^{-77}$** |

### 3.3. Threat-Class Containment Breakdown (`740` Attack Probes)

```text
Threat Class         Probes   Blocked   Containment
───────────────────────────────────────────────────
algo_dos               75       75      100.0%
capability_execve     220      220      100.0%
fs_escape             130      130      100.0%
memory_dos             95       95      100.0%
mimicry_exfil         115      115      100.0%
cpu_dos               105      102       97.1%
───────────────────────────────────────────────────
COMPOSITE             740      737       99.59%
```

### 3.4. Zero-Shot Leave-23-Targets-Out (`LOTO`) Transfer

* **Training Partition (`train_92`):** `457 / 460` strict joint pass = **`99.35%`**
* **Unseen Held-Out Partition (`unseen_loto_23`):** **`115 / 115` strict joint pass = `100.00%`** (`23/23` across all 5 seeds)

### 3.5. Complex Multi-Process & CVE-Class Application Suite (`15` Targets)

In isolation (`scripts/run_vnext_complex.py`, `22.1s`), COSMOS-Ω achieved **`15/15` (`100.0%`)** across real multi-process and CVE-class applications (`NGINX worker_processes=2`, `Gunicorn -w 2 + Flask + SQLite3`, `Flask SSTI`, `Flask SSRF`, `Git` alias RCE, `Ghostscript %pipe%`, `Poppler pdftotext`, `ImageMagick convert`, `cJSON -DCJSON_NESTING_LIMIT=100000`, and real C stack overflow, integer overflow, path traversal, and command injection targets), compared to **`5/15` (`33.3%`)** for both the 2-Float Sentinel and Random Search.

### 3.6. Measured Containment Gap Finding (`cpu_ms` vs. `wall_ms`)

Across all 575 evaluations, only 3 probes failed containment (`seq 263` and `seq 378` on `nginx_api_static`; `seq 425` on `nginx_multiprocess_cluster`), all under `http_flood_60x` (`cpu_dos`). Kernel `rusage` instrumentation confirms why:

* `seq 263`: `wall_ms = 53 ms`, **`cpu_ms = 6.651 ms`** (vs. `18.69 ms` CPU budget)
* `seq 378`: `wall_ms = 43 ms`, **`cpu_ms = 7.003 ms`** (vs. `250.0 ms` CPU budget)
* `seq 425`: `wall_ms = 43 ms`, **`cpu_ms = 9.652 ms`** (vs. `500.0 ms` CPU budget)

Because asynchronous NGINX workers spend most of an HTTP flood waiting on socket I/O, active core `cpu_ms` remains under 10 ms—demonstrating an honest, empirically measured limitation of CPU-time budgets against I/O-bound request floods.

<details>
<summary><strong>View Full 115-Target Catalog Composition</strong></summary>

* **`targets/catalog/batch1_50.yaml` (50 Targets):** `cJSON` (parser, deep), `libexpat`, `libxml2` (DOM, XPath), `zlib` (inflate, deflate), `pcre2` (regex, email), `libyaml`, `libpng`, `libjpeg-turbo`, `libarchive`, `sqlite3` C API, `OpenSSL` (EVP, Bignum), `Lua 5.4` (sandbox, table VM), POSIX `fnmatch`/`regcomp`, `jq`, `tar`, `sqlite3`, `gawk`, `unzip`, `curl`, `gzip`, `bzip2`, `xz`, `grep`, `sed`, `find`, `base64`, `bc`, `perl`, `patch`, `diff`, `sort`, `split`, `python3`, `nginx` (2 configs), `lighttpd`, `redis-server`, `memcached`, and 5 Python HTTP services.
* **`targets/catalog/batch2_50.yaml` (50 Targets):** 18 AI/agent tool runners (`PyYAML`, file tool, SQL tool, `eval` calc, `Jinja2`, `lxml` XML/XPath, markdown, `pickle`, `zipfile`, `tarfile`, regex, JSON schema, CSV, `pbkdf2_hmac`, HTTP fetcher, IP/ping wrapper, graph planner), 16 C/library harnesses (`cJSON` merge, `expat` attrs, `libxml2` HTML, `zlib` gzip, `pcre2` URL, `libyaml` emitter, `libpng` CRC, `libjpeg` roundtrip, `libarchive` create, `sqlite3` FTS, `OpenSSL` AES-GCM/HMAC, `Lua 5.4` coro/string, `qsort`, `strtod`), and 16 POSIX/HTTP services (`dd`, `tee`, `cp`, `tar` create, `sha256sum`, `sed -i`, `gawk`, `perl`, `python3`, `sqlite3` WAL, 6 Python HTTP APIs).
* **`targets/catalog/complex_apps_15.yaml` (15 Targets):** `nginx_multiprocess_cluster`, `gunicorn_flask_cluster`, `flask_ssti_app`, `flask_ssrf_webhook_app`, `git_vcs_cli`, `ghostscript_ps_engine`, `poppler_pdftotext`, `imagemagick_convert`, `python_doc_pipeline_cli`, `c_real_stackoverflow_parser`, `c_real_int_overflow_img`, `c_real_path_traversal_fs`, `cjson_deep_recursion_vuln`, `c_real_cmd_injection_parser`, `lua_c_embedded_app`.

</details>

---

## 4. Quickstart & Independent Verification

### 4.1. Prerequisites & Setup

Tested on **macOS (Apple Silicon via OrbStack)** and **Linux (`arm64` / `x86_64`)**.

```bash
git clone https://github.com/sirkianmj/ForgeX4-COSMOS-Omega.git
cd ForgeX4-COSMOS-Omega

conda create --name cosmos python=3.10 -y
conda activate cosmos
pip install -r requirements.txt

docker build -t cosmos-sandbox:v3 sandbox/
```

### 4.2. Unit Tests (`0.1s`, Zero Docker Load)

```bash
python -m unittest discover -s tests -v
```

### 4.3. Verify Strict SHA-256 Ledger & Recompute All Paper Metrics

```bash
# 1. Confirms 575/575 unbroken prev_hash links AND 575/575 strict payload SHA-256 digests
python verify_ledger.py

# 2. Independently recomputes LOTO-23, 740-probe threat histogram, gap diagnostics, and Mann-Whitney U p-values
python scripts/verify_paper_metrics.py
```

#### Strict SHA-256 Verification Snippet

```python
import hashlib, json

ledger_file = "artifacts/vnext_logs/ledger_journal115_20261121_103606_f10dab7dbf054b8d.json"
data = json.load(open(ledger_file))
prev_hash = "0" * 64

for event in data["events"]:
    assert event["prev_hash"] == prev_hash, f"Hash break at sequence {event['seq']}"
    unhashed = {k: v for k, v in event.items() if k != "hash"}
    computed = hashlib.sha256(json.dumps(unhashed, sort_keys=True).encode("utf-8")).hexdigest()
    assert computed == event["hash"], f"Tamper detected at sequence {event['seq']}"
    prev_hash = event["hash"]

print(f"Audit Verified: {len(data['events'])} events pass strict SHA-256 verification.")
```

*Canonical Terminal Block Hash (`f10dab7dbf054b8d`, `seq 574`):*
`0ad2de678bce13d6af3818632d564e4ee1e42c8a69de26a0e760619e185fcc39`

### 4.4. Run the Benchmarks Yourself

```bash
# Complex 15-App Multi-Process & CVE Suite (~22s, 1 worker)
python scripts/run_vnext_complex.py --pace-ms 25

# Full 115-Target 5-Seed Benchmark (Thermal-safe 1-worker, ~21 min)
python scripts/run_vnext_100_journal.py --seeds 5 --workers 1 --pace-ms 25
```

---

## 5. Repository Structure

```text
ForgeX4-COSMOS-Omega/
├── cosmos/
│   ├── vnext/                      # Unified Generalist COSMOS-Ω Engine
│   │   ├── policy_ir.py            # PolicyIR, kernel_hash memoization, privilege surface
│   │   ├── verifier.py             # Thread-safe Z3 SMT invariant verifier
│   │   ├── audit_ledger.py         # Deepcopy-immutable SHA-256 hash-chained ledger
│   │   ├── sandbox_client.py       # Client to pre-warmed cosmos-sandboxd
│   │   ├── drivers.py              # Generic Parser, CLI, Daemon, Agent drivers
│   │   └── foundry.py              # Synthesis loop, CrossTargetDigitalTwin, baselines
│   ├── foundry/                    # Legacy Phase 1-3 Pathfinder & Sentinel engines
│   └── ledger/                     # Legacy Phase 1-3 ledger
├── sandbox/
│   ├── Dockerfile                  # cosmos-sandbox:v3 container definition
│   ├── cosmos_enforcer.c           # libseccomp USER_NOTIF + Landlock v10 + setrlimit
│   └── sandbox_daemon.py           # Pre-warmed HTTP/TCP sandbox worker daemon
├── targets/catalog/
│   ├── batch1_50.yaml              # Targets 1-50
│   ├── batch2_50.yaml              # Targets 51-100
│   ├── complex_apps_15.yaml        # Targets 101-115 (Multi-process & real CVE patterns)
│   └── core_16.yaml                # Quick 16-target smoke suite
├── scripts/
│   ├── run_vnext_100_journal.py    # 115-target multi-seed + LOTO journal runner
│   ├── run_vnext_complex.py        # 15 complex apps runner
│   ├── verify_paper_metrics.py     # Independent raw-ledger paper verifier
│   └── ...                         # Legacy Phase 1-3 scripts
├── artifacts/vnext_logs/
│   ├── ledger_journal115_20261121_103606_f10dab7dbf054b8d.json
│   ├── results_115.csv
│   └── paper_tables_115.tex
├── tests/
│   └── test_vnext_core.py          # Fast unit tests (0.10s)
├── verify_ledger.py                # Strict SHA-256 chain & payload checker
└── requirements.txt                # Pinned Python dependencies
```

---

## 6. Historical Lineage (Phases 1–3) & TechRxiv v1 Correspondence

To maintain full scientific continuity with earlier releases:

### 6.1. Published TechRxiv v1 Article (Phase 1–2 Pathfinder)
The foundational preprint (*"ForgeX4 COSMOS-Ω: A Foundational Validation of a Multi-Physics Digital Immune System"*, DOI: [`10.36227/techrxiv.176055396.69060312/v1`](https://doi.org/10.36227/techrxiv.176055396.69060312/v1)) validates the **Pathfinder** variant (`cosmos/foundry/foundry_pathfinder.py` + `cosmos/foundry/titans_pathfinder.py`) on `cJSON`:
* **Champion Fitness:** `+1499.97` (Immediate Generation-0 convergence; verified range `~1480–1500` across Apple M-series runs)
* **Canonical Pathfinder Ledger:** `artifacts/gui_runs/run_1759572140/ledger_20251004_100220_114877e883156cb6.json`
* **Terminal Block Hash:** `08ed2f9ab17b5cc12caa2bd7730f8c75085fb7959e993849e4057a76cd050598` (`25` SHA-256 chained blocks)
* **Behavioral Classifier:** `notebooks/14_digital_twin_v8_overdrive_classifier.ipynb` (`99.3% ± 0.6%` 95% CI accuracy)

#### TechRxiv v1 Erratum
TechRxiv v1 Section 5.4 cites terminal hash `a758580fafbca63779424e24db3bfded302fcf7dd775475cc1923cf7f189c53a`, which belongs to a separate NGINX Daemon Sentry run (`artifacts/gui_runs/run_1759597962/`). The correct terminal hash for the `cJSON` Pathfinder experiment is:
`08ed2f9ab17b5cc12caa2bd7730f8c75085fb7959e993849e4057a76cd050598`

### 6.2. Phase 3: Aegis Sentinel
Validated evolutionary bounds (`max_cpu_percent`, `max_resident_memory_bytes`) on `mixed_workload.c` with 5× evaluation averaging and `1.10×` deployment margin (`artifacts/final_run_logs/aegis_sentinel_champion.json`).

### Variant Evolution Summary

| Variant | Genome / Policy | Mechanism | Target Scope | Formal Proof | Status |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Pathfinder** *(TechRxiv v1)* | 11 metrics × 5 logic ops | `psutil` sampling | 1 (`cJSON`) | Heuristic | Historical paper baseline |
| **Sentinel** *(Phase 3)* | 2 scalars (`cpu%`, `rss`) | `psutil` sampling | 1 (`mixed_workload.c`) | None | Phase 3 demo baseline |
| **COSMOS-Ω vNext** *(Current)* | Stateful `PolicyIR` + `rusage` | `libseccomp` + Landlock v10 + `RLIMIT` | **115 Targets** | **Z3 SMT + Strict SHA-256** | **Canonical Release** |

---

## 7. Security & Artifact Notices

> [!CAUTION]
> **Note on `xmrig-6.21.3` and Adversarial Probes:**
> * `xmrig-6.21.3` is retained strictly as a historical Phase 2 CPU-intensive cryptojacking test workload for `malicious_miner_process.py`. **Do not execute it directly on a host.**
> * `targets/catalog/` contains controlled decompression bombs, ReDoS inputs, and capability-boundary probes designed exclusively for execution inside the unprivileged, Landlock-restricted `cosmos-sandbox` container.

---

## 8. Citation

If you use COSMOS-Ω, its Multi-Physics Evolutionary Defense principles, or the 115-target benchmark in your work, please cite:

```bibtex
@article{jamshidi2024forge,
  title={{ForgeX4 COSMOS-$\Omega$: A Foundational Validation of a Multi-Physics Digital Immune System}},
  author={Jamshidi, Kian Mansouri},
  journal={TechRxiv},
  year={2025},
  publisher={IEEE},
  doi={10.36227/techrxiv.176055396.69060312/v1}
}

@software{jamshidi2026cosmos_vnext,
  author       = {Kian Mansouri Jamshidi},
  title        = {{COSMOS-$\Omega$ vNext: Formally Verified Multi-Physics Containment Automata across 115 Heterogeneous Targets}},
  year         = {2026},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/sirkianmj/ForgeX4-COSMOS-Omega}}
}
```

---

## 9. License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file for full legal terms.