# ForgeX4 COSMOS-Ω: An Autonomous Foundry for Synthesizing Verifiable Security Policies

<p align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL%20v3.0-blue.svg" alt="License: AGPL v3.0">
  </a>
  <img src="https://img.shields.io/badge/Project%20Status-Complete%20%26%20Ready%20for%20Publication-brightgreen.svg" alt="Project Status: Complete & Ready for Publication">
  <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg" alt="Contributions: Welcome">
</p>

---

## Vision: A New Paradigm for Generative Security

ForgeX4 COSMOS-Ω is a completed research project that breaks the reactive cycle of cybersecurity. Our vision was to create the world's first autonomous, multi-physics foundry that does not merely patch vulnerabilities, but **autonomously synthesizes novel, verifiable security policies.** The system is a successfully implemented scientific instrument that automates security innovation itself.

This repository contains the complete source code, experimental data, research notebooks, and final artifacts for the project, led by Project Director  **Kian Mansouri Jamshidi**.

---

## Core Research Pillars (Validated Contributions)

This project has successfully demonstrated and validated three new fields of study:

*   **Multi-Physics Evolutionary Defense (MPED):** We proved that by grounding digital evolution in the physical realities of computation (CPU utilization), it is possible to create a high-fidelity Digital Twin (**R² = 0.8860**) that serves as a powerful fitness function for evolving robust and efficient software.

*   **Full-Stack Co-Evolution & Non-Invasive Defense:** The project's final "Operation Sentinel" architecture successfully implements a co-evolutionary arms race. In a critical pivot from traditional methods, the system treats the target application as a black box, evolving an external, non-invasive **security policy** rather than attempting to repair its source code.

*   **Cryptographically Provable Explainable AI (XAI):** We have implemented and validated a tamper-evident "Explainability Ledger" that provides a complete, SHA-256 chained audit trail of the AI's entire evolutionary history, moving beyond explainability to true, mathematical auditability.

## Final Architecture: Operation Sentinel

The project's initial goal of parsing and repairing C code was proven to be a dead end due to the complexities of real-world source. The project's "Great Pivot" led to the final, successful, parser-free architecture.

#### 1. Instrumented Execution
The pipeline begins by running the unmodified target application (e.g., `cJSON.c`) in a sandboxed environment. The **ExecutionTitan** uses `strace` and `psutil` to capture a complete record of the application's behavior and its physical (CPU) footprint.

#### 2. The Foundry: A Multi-Agent Evolutionary Core
This is the heart of the system where the evolution of a **security policy genome** (a set of rules) occurs. The foundry orchestrates a multi-objective optimization process, guided by a Council of Titans.

#### 3. Governance and Fitness Evaluation
The evolution is guided by a sophisticated, multi-objective fitness function that balances conflicting goals:
*   **JanusTitan:** Analyzes `strace` logs for behavioral anomalies (crashes, rule violations) to measure security effectiveness.
*   **PerformanceTitan:** Uses the high-fidelity Digital Twin (v5.3) to score the performance overhead of the policy, providing the MPED signal.
*   **Fitness Score:** A final score is calculated that heavily rewards security and correctness while penalizing performance degradation and false positives.

#### 4. Artifact Generation
The evolutionary process yields two final, unassailable artifacts:
*   **The Aegis Sentinel:** The champion genome itself—a **synthesized security policy** (e.g., `{'max_total_syscalls': 54}`) that can be deployed by a monitoring agent.
*   **Explainability Ledger:** A cryptographically secure `ledger.json` providing a verifiable and tamper-proof audit trail of the entire evolutionary history.


## The Hardware Constraint: A Cornerstone of Innovation

A non-negotiable constraint of this project was that the entire system must be developed and run on commodity hardware: an **HP Elite x2 G4 tablet (Intel Core i5, 16GB RAM, no dGPU)**. This forced computational pragmatism and drove innovation in algorithmic efficiency, proving the viability of these advanced techniques on non-specialized hardware.

---

## Development Roadmap (Completed)

This project followed a rigorous, phased development plan, which is now complete.

- [x] **Phase 0: Foundation & Environment Setup**
- [x] **Phase 1: The Minimal Viable Foundry** (Building the core evolutionary loop)
- [x] **Phase 2: The Sentient Foundry** (Implementing the Digital Twin and advanced agents)
- [x] **Phase 3: The Unassailable Artifact** (Final benchmarking and synthesis)
- [ ] **Phase 4 (Current): Publication & The Future**

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

This is a strong "copyleft" license. In short, you are free to use, study, and share the software. If you modify the source code, you must also release your modifications under the same AGPL-3.0 license. If you run a modified version of this software on a server and let other users interact with it, you must make the source code of your modified version available to them.

Please see the [LICENSE](LICENSE) file for the full terms and conditions.

---

## Citation

If you use this research or code in your academic or professional work, please cite it as follows.

```bibtex
@misc{jamshidi2025cosmos,
  author       = {Kian Mansouri Jamshidi},
  title        = {{ForgeX4 COSMOS-Ω: An Autonomous Foundry for Synthesizing Verifiable Security Policies}},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/sirkianmj/ForgeX4-COSMOS-Omega}}
}```

