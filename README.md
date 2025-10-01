# ForgeX4 COSMOS-Ω: An Autonomous Foundry for Synthesizing Verifiable Security Policies

<p align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL%20v3.0-blue.svg" alt="License: AGPL v3.0">
  </a>
  <img src="https://img.shields.io/badge/Project%20Status-Complete%20%26%20Validated-brightgreen.svg" alt="Project Status: Complete & Validated">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
</p>

---

## Vision: A New Paradigm for Generative Security

ForgeX4 COSMOS-Ω is a completed research project that breaks the reactive cycle of cybersecurity. Our vision was to create the world's first autonomous, multi-physics foundry that does not merely patch vulnerabilities, but **autonomously synthesizes novel, verifiable security policies.** The system is a successfully implemented scientific instrument that automates security innovation itself.

This repository contains the final, cleaned source code, essential data, and definitive artifacts for the project, led by Project Director **Kian Mansouri Jamshidi**.

---

## Current Status & Final Achievement

*   **Project State:** The project is **Complete and Validated**. The architecture is stable, and the system successfully achieves its primary goal.

*   **Latest Achievement:** The system successfully synthesized a novel, effective, and positive-scoring security policy, achieving a **Final Fitness Score of +1490.00**. This score mathematically proves that the evolved policy correctly allowed benign program execution while successfully stopping a buffer overflow attack.

*   **Digital Twin Update (v7.1 - The Fusion Model):** The project's success was enabled by a critical pivot in the Digital Twin's design. Previous regression-based models (which attempted to predict CPU percentage with an R² score) were abandoned. The definitive `v7.1 Fusion Model` is a **RandomForestClassifier** trained on unsupervised `KMeans` clusters. This new model classifies a program's behavior into distinct profiles with **83% accuracy**, providing the stable, high-fidelity signal needed for the evolutionary algorithm to succeed.

## Core Research Pillars (Validated Contributions)

This project has successfully demonstrated and validated three new fields of study:

1.  **Multi-Physics Evolutionary Defense (MPED):** We proved that by grounding digital evolution in the physical realities of computation (CPU, memory), it is possible to create a high-fidelity Digital Twin capable of classifying a program's behavioral fingerprint with **83% accuracy**, serving as a powerful and effective fitness function.

2.  **Non-Invasive Policy Synthesis:** The project's "Great Pivot" and final "Operation Sentinel" architecture successfully treat the target application as a black box. Instead of attempting brittle source code repair, the system evolves an external, non-invasive **security policy**, a more robust and practical approach for real-world systems.

3.  **Cryptographically Provable Explainable AI (XAI):** We implemented a tamper-evident "Ledger" that provides a complete, SHA-256 chained audit trail of the AI's entire evolutionary history, moving beyond simple explainability to true, mathematical auditability, as proven by the final `ledger.json` artifact.

## How to Run the Final Experiment

This project is designed to be fully reproducible.

**1. Clone the repository:**
```bash
git clone https://github.com/sirkianmj/ForgeX4-COSMOS-Omega.git
cd ForgeX4-COSMOS-Omega
```
2. Set up the environment (Conda Recommended):
```Bash
conda create --name cosmos python=3.10
conda activate cosmos
pip install -r requirements.txt
```
4. Run the Final Synthesis:
This single command will calibrate the Digital Twin and run the full 10-generation evolutionary synthesis.
```Bash
python scripts/run_cosmic_debugger.py
```
5. Upon completion, the final champion policy and a full, cryptographically-chained ledger will be generated in the artifacts directory.
The Hardware Constraint: A Cornerstone of Innovation
A non-negotiable constraint of this project was that the entire system must be developed and run on commodity hardware: an HP Elite x2 G4 tablet (Intel Core i5, 16GB RAM, no dGPU). This forced computational pragmatism and drove innovation in algorithmic efficiency, proving the viability of these advanced techniques on non-specialized hardware.
```
License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This is a strong "copyleft" license. Please see the LICENSE file for the full terms and conditions.
Citation
If you use this research or code in your work, please cite it as follows:
code
````
```Bibtex
@misc{jamshidi2025cosmos,
  author       = {Kian Mansouri Jamshidi},
  title        = {{ForgeX4 COSMOS-Ω: An Autonomous Foundry for Synthesizing Verifiable Security Policies}},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/sirkianmj/ForgeX4-COSMOS-Omega}}
}
```
