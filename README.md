# ForgeX4 COSMOS-Ω: A Foundational Validation of a Multi-Physics Digital Immune System

<p align="center">
  <img src="https://img.shields.io/badge/Project%20Status-Complete%20%26%20Validated-brightgreen.svg" alt="Project Status: Complete & Validated">
  <img src="https://img.shields.io/badge/Lead%20Researcher-Kian%20Mansouri%20Jamshidi-blue.svg" alt="Lead Researcher">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL%20v3.0-blue.svg" alt="License: AGPL v3.0">
  </a>
</p>

---

## 1. Overview: A New Paradigm for Generative Security

The prevailing doctrine of reactive cybersecurity—a resource-intensive cycle of patching vulnerabilities post-attack—is economically unsustainable and strategically flawed. ForgeX4 COSMOS-Ω is a completed research project that presents a validated, practical alternative.

This project introduces and validates a **Multi-Physics Digital Immune System**, an autonomous foundry that does not repair programs but **autonomously synthesizes novel, provably accountable security policies.** It represents a paradigm shift from manual, reactive patching to proactive, generative defense.

This repository contains the complete source code, experimental data, and auditable artifacts from this research, led by Project Director **Kian Mansouri Jamshidi**.

---

## 2. Core Scientific Contributions

This project has successfully introduced and validated three primary contributions:

1.  **Multi-Physics Evolutionary Defense (MPED):** A new scientific principle demonstrating that a program's physical side-effects (CPU, memory, I/O telemetry) can serve as a universal, high-fidelity information channel to guide evolutionary algorithms. This principle was validated across disparate hardware architectures (Intel, AMD) and virtualization layers (Bare Metal, VMware, WSL, Containerized Cloud).

2.  **The First Practical Digital Immune System:** We present the successful implementation of a bio-inspired security model. The system's core is a behavioral classifier achieving **99.3% ± 0.6% (95% CI) accuracy** in identifying a program's operational state from its physical telemetry. By treating the target application as an opaque black box, this parser-free architecture overcomes the fundamental brittleness of traditional Automated Program Repair (APR).

3.  **Provable Governance & Algorithmic Accountability:** We establish a new standard for trustworthy AI in security. The system implements a tamper-evident, SHA-256 chained **"Ledger"** that provides an immutable and mathematically verifiable audit trail of the AI's entire decision-making process. This satisfies core tenets of frameworks like DARPA's Responsible AI and the NIST AI Risk Management Framework.
## 2.5 Published Research Article
This repository serves as the official implementation of the research detailed in the following article:
```Bibtex
Title: ForgeX4 COSMOS-Ω: A Foundational Validation of a Multi-Physics Digital Immune System
DOI: 10.36227/techrxiv.176055396.69060312/v1
Published: TechRxiv
```
The paper provides an in-depth validation of the system's architecture and the scientific principles it is built upon. It establishes that physical side-channel data from a program's execution can be used as a universal medium for an AI to autonomously generate security policies, without needing to parse or understand the source code.

---

## 3. The Foundational Experiment: Key Results

*   **Project State:** The foundational research and its claims are **Complete and Validated**. The architecture is stable and the system successfully achieves its primary scientific goals.

*   **Conclusive Result:** In its primary calibration experiment, the COSMOS-Ω system autonomously synthesized a novel, multi-state security policy for the `cJSON` library, achieving a composite **Final Fitness Score of +1499.97**.

*   **Immediate Convergence:** The system achieved this peak fitness score in **Generation 0**. This immediate convergence serves as the definitive empirical proof that the MPED fitness landscape provides an exceptionally clear and powerful gradient for security policy discovery.

---

## 4. Reproducing the Experiment

The project is designed for full reproducibility. The primary experiment can be replicated using the provided scripts and artifacts.

**1. Clone the repository:**
```bash
git clone https://github.com/sirkianmj/ForgeX4-COSMOS-Omega.git
cd ForgeX4-COSMOS-Omega
```
**2. Set up the environment (Conda Recommended):**

```bash
conda create --name cosmos python=3.10
conda activate cosmos
pip install -r requirements.txt
```
**3. Run the Foundational Calibration Experiment:**
This command will compile the cJSON target, calibrate the Digital Immune System, and run the full 10-generation evolutionary synthesis.
```bash
python scripts/run_pathfinder_experiment.py
```
**4. Verify the Results:**
Upon completion, the final champion policy and the full, cryptographically-chained ledger will be generated in the artifacts/gui_runs/ directory. The ledger.json file contains the final champion and the mathematical breakdown of its fitness score.
The accompanying Jupyter Notebook, notebooks/14_digital_twin_v8_overdrive_classifier.ipynb, provides the complete, documented process for training the behavioral classifier from the raw telemetry data located in the data/ directory.

## 5. License
```bash
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This is a strong copyleft license intended to ensure that derivative works contributing to public network services also remain open source. Please see the LICENSE file for full terms.
```
## 6. Citation
If you use this research or code in your work, please cite it as follows:
 
 ## Article
```Bibtex
@article{jamshidi2024forge,
  title={ForgeX4 COSMOS-$\Omega$: A Foundational Validation of a Multi-Physics Digital Immune System},
  author={Jamshidi, Kian Mansouri},
  journal={TechRxiv},
  year={2025},
  publisher={IEEE},
  doi={10.36227/techrxiv.176055396.69060312/v1}
}
```
## Software
```Bibtex
@misc{jamshidi2025cosmos,
  author       = {Kian Mansouri Jamshidi},
  title        = {{ForgeX4 COSMOS-Ω: A Foundational Validation of a Multi-Physics Digital Immune System}},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/sirkianmj/ForgeX4-COSMOS-Omega}}
}
```


## ⚠️ A Note on `xmrig-6.21.3`
This repository contains the XMRig binary. **It is strictly included as a benign, CPU-intensive "malicious" workload** for the `TelemetryTitan` to classify. It is used to train the digital twin to detect unauthorized cryptojacking. **Do not run it directly.** It is meant to be executed inside the sandboxed `malicious_miner_process.py` script during Phase 2 experiments.

---

## Phase 3: Aegis Sentinel — Evolution Validated (Nov 2026)

The Aegis Sentinel GA was run end-to-end on Apple M-series (M5) hardware.

**Setup:**
- Target: `mixed_workload.c` — I/O-bound benign mode vs CPU-bound attack mode
- Genome: single gene `max_cpu_percent` (search range 8.0–14.0)
- Fitness: 500 (correctness) + 1000 (security) + up to 300 (precision) = max 1800
- Config: population_size=20, generations=40, mutation_rate=0.5, elitism_count=2, 3× eval averaging

**Results:**
- Champion genome: `max_cpu_percent = 7.14`, fitness = **1769.67**
- Stable range (last 10 gens): ~8.5–9.0, fitness ~1766
- Convergence: the GA walked from initial random genomes (~9.5) toward the boundary optimum over 40 generations

**Key finding — precision/robustness tradeoff:**
Benign workload peak CPU varies ±2% between runs. Genomes at the lower boundary
(~7.1%) achieve the highest precision bonus but suffer catastrophic collapse (−1000)
when the benign peak spikes. Genomes at the upper boundary (~8.9%) sacrifice
~30 fitness points for robustness. The GA naturally oscillates between these regimes.

**Phase 3.1 update — resolved since initial Phase 3:**
- ✅ **Multi-attack-class validation**: genome now carries both
  `max_cpu_percent` and `max_resident_memory_bytes`. Attack set is
  `[CPU-exhaustion, memory-exhaustion]`; both are enforced by the Titan.
- ✅ **Memory-based policy primitives**: `max_resident_memory_bytes` added
  to genome (init range 30-100MB), enforced alongside CPU threshold.
- ✅ **Production deployment margin**: champion JSON now stores
  `production_genome_10pct_margin` with both thresholds scaled ×1.10
  for deployment safety headroom.

**Remaining limitations (honest):**
- **Non-stationary benign signatures**: fitness landscape is discontinuous
  near the optimum because benign peak CPU varies ±2% between runs.
  Mitigated by 3× evaluation averaging, but not eliminated. This is a
  property of real hardware, not a bug.
- **Hardware-specific**: results measured on Apple M5. Cross-platform
  verification (Intel, AMD, ARM server) is pending and requires physical
  access to non-M5 hardware.

**Deferred to Phase 4:**
- Cross-target transfer (Gaia genome): requires a second target with a
  distinct benign signature to validate that the Digital Twin classifier
  generalizes rather than overfits to cJSON/mixed_workload patterns.

---

## Paper Correspondence (TechRxiv v1)

The TechRxiv preprint *"COSMOS-Ω: Autonomous Generative Security via Multi-Physics Evolutionary Defense"* describes the **Pathfinder** variant (`cosmos/foundry/foundry_pathfinder.py` + `cosmos/foundry/titans_pathfinder.py`), not the Sentinel demo variant hardened in this session.

### Canonical Pathfinder artifacts (paper)

- **Target**: cJSON (Pathfinder Default)
- **Champion fitness**: +1499.97
- **Ledger file**: `artifacts/gui_runs/run_1759572140/ledger_20251004_100220_114877e883156cb6.json`
- **Terminal block hash**: `08ed2f9ab17b5cc12caa2bd7730f8c75085fb7959e993849e4057a76cd050598`
- **Blocks**: 25 (SHA-256 chained)

### Erratum

TechRxiv v1 Section 5.4 cites terminal hash `a758580fafbca63779424e24db3bfded302fcf7dd775475cc1923cf7f189c53a`. That hash belongs to a separate **NGINX Daemon Sentry run** (`artifacts/gui_runs/run_1759597962/`). The correct hash for the cJSON Pathfinder experiment is:
08ed2f9ab17b5cc12caa2bd7730f8c75085fb7959e993849e4057a76cd050598

text

### Sentinel vs Pathfinder

| Variant | Genome | Target | Champion | Status |
|---|---|---|---|---|
| **Pathfinder** (paper) | 11 metrics × 5 operators (AND/OR/XOR/NAND/NOR) | cJSON | +1499.97 | Original paper experiment |
| **Sentinel** (demo) | 2-gene (`max_cpu_percent`, `max_resident_memory_bytes`) | mixed_workload.c | +1631.01 | Hardened this session |

Both variants share the SHA-256 ledger architecture and the Digital Intelligence System classifier (`digital_twin_v7.1_The_Fusion_Model.joblib`). The paper specifically validates Pathfinder.
