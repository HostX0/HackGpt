<!-- HackGPT document -->
# 🚀 HackGPT Enterprise Release Notes — Version 2026.09.26

> [!IMPORTANT]
> ### 💖 Critical Notice: Support, Donations & Sponsorship Required
> HackGPT Enterprise is an independent open-source cybersecurity and AI penetration testing research project. To continuously maintain the platform, support multi-provider frontier AI integrations, and sustain security research infrastructure, **we require funds, donations, and sponsorships to maintain this project**.
>
> **Please consider donating and sponsoring HackGPT development!**
> - **GitHub Sponsors (Active)**: [Sponsor @yashab-cyber on GitHub Sponsors](https://github.com/sponsors/yashab-cyber)
> - **Cryptocurrency Transfers**: For crypto donations (Solana, Bitcoin, Ethereum, USDT, etc.), please email: **yashabalam707@gmail.com**
> - **Sponsorships & Inquiries**: Contact creator at: **yashabalam707@gmail.com**
> - **Full Guidelines & Tier Perks**: Please visit [DONATE.md](DONATE.md).

---

We are excited to announce the release of **HackGPT Enterprise Version 2026.09.26**! This release integrates the new **Evidence Workbench**, cross-platform reliability hardening, reviewable AI and adapter lifecycles, and a hardened CI pipeline contributed by **Abdulazeez A. Noaman** ([@HostX0](https://github.com/HostX0)) in Pull Request [#21](https://github.com/yashab-cyber/HackGpt/pull/21).

---

## 🌟 What's New in Version 2026.09.26

### 1. Evidence Workbench & Local Assessment Studio (`workbench/`)
* **Local Evidence-First Assessment Studio**: Self-contained local studio, reviewer interface, and web service for offline-capable, reviewable security assessments.
* **Privacy-Minimizing Scanner Parsers & Adapters**: Standardized adapter parsers for Semgrep, Nuclei, Trivy, and project metadata scanners that scrub raw targets, strip credentials, drop proprietary database row values, and generate minimal finding candidates.
* **Bounded Access-Control Matrix**: Strict matrix evaluator enforcing authorized targets and action boundaries.
* **Coverage-Aware Retest Engine**: Automated verification system linking remediation advice directly to historical evidence and diffs without falsifying test results.
* **Tamper-Evident Evidence Bundles**: Exportable review bundles signed with cryptographic digest integrity checks.

### 2. Reviewable Adapter Lifecycle & Execution Receipts
* **Durable Adapter Approval & Planning Lifecycle**: Pre-execution planning, explicit operator approval gates, and durable execution receipts.
* **Cooperative Cancellation & Wall-Clock Deadlines**: Cancellable network transports, shared deadlines, and interrupted run recovery with running checkpoints.
* **Bounded Native Execution Registry**: Closed execution registry with isolated environment runners and resource cleanup.

### 3. Cross-Platform Reliability & Launcher Hardening
* **Multi-Platform Launchers**: Native launch scripts for Linux, macOS (`workbench/start.command`), and Windows (`workbench/start.cmd`, `workbench/start.py`).
* **Container vs Host Installer Context**: Hardened `install.sh` supporting `HACKGPT_INSTALL_CONTEXT` (`host` vs `container`) to avoid side effects during Docker builds.
* **Backward-Compatible Legacy Entrypoints**: Retained `hackgpt.py` and `hackgpt_v2.py` alongside `advance_hackgpt.py` to preserve legacy tooling and automation workflows.

### 4. Hardened CI/CD & Automated Testing Matrix
* **Multi-Tier CI Matrix**: Added bounded Python 3.8 CI profile (`requirements-ci-py38.txt`) for legacy core contracts alongside full Python 3.9-3.11 test matrices.
* **Fail-Closed Black Code Quality Pipeline**: Uploads exact format diffs and automated candidate repair archives upon style divergence.
* **Expanded Verification**: 90+ core unit tests, comprehensive contract suites (`test_docker_contract.py`, `test_enterprise_ci_contract.py`, `test_requirements_compat.py`), and workbench E2E tests.

### 5. Community & Contributor Recognition
* **Special Thanks**: Full credit and gratitude to **Abdulazeez A. Noaman** ([@HostX0](https://github.com/HostX0)) for designing, implementing, and contributing Pull Request [#21](https://github.com/yashab-cyber/HackGpt/pull/21).

---

## 🛠️ Quick Start with Version 2026.09.26

1. **Launch Advance HackGPT**:
   ```bash
   python advance_hackgpt.py
   python advance_hackgpt.py --web
   python advance_hackgpt.py --api
   ```

2. **Launch Evidence Workbench**:
   ```bash
   python workbench/start.py
   ```

3. **Verify Installation & Test Suite**:
   ```bash
   pytest tests/unit/ -v --tb=short
   python test_installation.py --ci
   ```
