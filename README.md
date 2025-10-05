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

**5. License**
```bash
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This is a strong copyleft license intended to ensure that derivative works contributing to public network services also remain open source. Please see the LICENSE file for full terms.
```
**6. Citation**
If you use this research or code in your work, please cite it as follows:
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
