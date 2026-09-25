// HackGPT script module
// HackGPT Landing Page Interactive Logic

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navbar Scroll Effect & Mobile Navigation Toggle
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 30) {
            navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    });

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            const icon = navToggle.querySelector('i');
            if (icon.classList.contains('fa-bars')) {
                icon.classList.replace('fa-bars', 'fa-xmark');
            } else {
                icon.classList.replace('fa-xmark', 'fa-bars');
            }
        });
    }

    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (navMenu) navMenu.classList.remove('active');
            const icon = navToggle ? navToggle.querySelector('i') : null;
            if (icon) icon.classList.replace('fa-xmark', 'fa-bars');
        });
    });

    // 2. Hero Window Tab Switcher
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const tabId = btn.getAttribute('data-tab');
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            const activeTab = document.getElementById(tabId);
            if (activeTab) activeTab.classList.add('active');
        });
    });

    // 3. Interactive 6-Phase Pipeline Tabs
    const pipelineSteps = {
        1: {
            badge: 'PHASE 01 // INTELLIGENCE GATHERING',
            heading: 'Passive & Active Reconnaissance',
            desc: 'Discovers attack surfaces, identifies live subdomains, performs DNS enumeration, and catalogs exposed web ports and services using integrated tools.',
            module: 'ai_engine/providers.py & cloud/service_registry.py',
            caps: 'Subdomain discovery, Banner Grabbing, Port Scanning, Service Mapping',
            code: 'python3 advance_hackgpt.py --target company.com --recon --verbose'
        },
        2: {
            badge: 'PHASE 02 // VULNERABILITY SCANNING',
            heading: 'Active Enumeration & Flaw Detection',
            desc: 'Scans target endpoints for known CVEs, misconfigurations, outdated HTTP headers, exposed API routes, and SSL/TLS cipher vulnerabilities.',
            module: 'exploitation/zero_day_detector.py & database/manager.py',
            caps: 'CVE Matching, Nuclei Template Auditing, Directory Bruteforce, Header Checks',
            code: 'python3 advance_hackgpt.py --target company.com --scan-level deep'
        },
        3: {
            badge: 'PHASE 03 // AI THREAT INTELLIGENCE',
            heading: 'LLM-Powered Exploit Modeling',
            desc: 'Feeds vulnerability observations into OpenAI / Llama-3 model providers to generate context-aware threat models and non-destructive PoC verification strategies.',
            module: 'ai_engine/model_registry.py & ai_engine/advanced_engine.py',
            caps: 'AI Threat Graph Construction, Attack Path Synthesis, PoC Query Generation',
            code: 'python3 advance_hackgpt.py --target company.com --ai-provider openai --model gpt-4o'
        },
        4: {
            badge: 'PHASE 04 // SAFE EXPLOITATION',
            heading: 'Controlled Payload & PoC Verification',
            desc: 'Executes non-destructive exploits safely to confirm vulnerability exploitability without risking system downtime or using unsanitized shell calls.',
            module: 'exploitation/advanced_engine.py',
            caps: 'Safe Proof of Concept, Privilege Escalation Check, Zero shell=True Vulnerability',
            code: 'python3 advance_hackgpt.py --target company.com --safe-exploit'
        },
        5: {
            badge: 'PHASE 05 // ZERO-DAY ANOMALY ML',
            heading: 'DBSCAN & Isolation Forest Log Clustering',
            desc: 'Applies Machine Learning algorithms to analyze access logs, network traffic, and system calls to flag unknown zero-day anomaly indicators.',
            module: 'exploitation/zero_day_detector.py',
            caps: 'DBSCAN Log Clustering, Isolation Forest Anomaly Detection, Outlier Scoring',
            code: 'python3 advance_hackgpt.py --target company.com --zero-day-ml --log-file system.log'
        },
        6: {
            badge: 'PHASE 06 // EXECUTIVE REPORTING',
            heading: 'Automated PDF & HTML Audit Generation',
            desc: 'Compiles technical findings, severity metrics, and remediation guidance into polished PDF and HTML audit reports mapped to OWASP, NIST, and PCI-DSS.',
            module: 'reporting/dynamic_reports.py & reporting/realtime_dashboard.py',
            caps: 'Executive PDF Generation, Compliance Mapping (OWASP/NIST), HTML Web Dashboard',
            code: 'python3 advance_hackgpt.py --target company.com --report pdf,html --output audit-report.pdf'
        }
    };

    const pipeSteps = document.querySelectorAll('.pipe-step');
    pipeSteps.forEach(stepBtn => {
        stepBtn.addEventListener('click', () => {
            pipeSteps.forEach(s => s.classList.remove('active'));
            stepBtn.classList.add('active');

            const stepNum = stepBtn.getAttribute('data-step');
            const data = pipelineSteps[stepNum];
            if (data) {
                document.getElementById('pipeBadge').innerText = data.badge;
                document.getElementById('pipeHeading').innerText = data.heading;
                document.getElementById('pipeDesc').innerText = data.desc;
                document.getElementById('pipeModule').innerText = data.module;
                document.getElementById('pipeCaps').innerText = data.caps;
                document.getElementById('pipeCode').innerText = data.code;
            }
        });
    });

    // 4. Live AI Threat Analyzer Simulator
    const presets = {
        sqli: `// ExpressJS Route Vulnerability
app.get('/api/users/search', async (req, res) => {
    const { query } = req.query;
    const result = await db.query("SELECT * FROM users WHERE name = '" + query + "'");
    res.json(result.rows);
});`,
        k8s: `# Kubernetes Unauthenticated API Service
apiVersion: v1
kind: Pod
metadata:
  name: admin-workload
spec:
  containers:
  - name: app
    image: nginx
    securityContext:
      privileged: true`,
        docker: `# Docker Socket Exposure in Docker Compose
version: '3.8'
services:
  app:
    image: node:18
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock`,
        jwt: `// Insecure JWT Verification
const jwt = require('jsonwebtoken');
const SECRET_KEY = "123456"; // Hardcoded weak secret key

function verifyUserToken(token) {
    return jwt.verify(token, SECRET_KEY, { algorithms: ['HS256', 'none'] });
}`,
        rce: `# Python Command Injection Risk
import subprocess

def ping_host(user_supplied_ip):
    # Unsanitized string concatenation into shell execution
    command = f"ping -c 1 {user_supplied_ip}"
    output = subprocess.check_output(command, shell=True)
    return output`
    };

    const presetBtns = document.querySelectorAll('.preset-btn');
    const analyzerInput = document.getElementById('analyzerInput');
    const runAiAnalysisBtn = document.getElementById('runAiAnalysisBtn');
    const analyzerOutput = document.getElementById('analyzerOutput');
    const aiStatusBadge = document.getElementById('aiStatusBadge');

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            presetBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const presetKey = btn.getAttribute('data-preset');
            if (presets[presetKey] && analyzerInput) {
                analyzerInput.value = presets[presetKey];
            }
        });
    });

    if (runAiAnalysisBtn) {
        runAiAnalysisBtn.addEventListener('click', () => {
            const text = analyzerInput.value.trim();
            if (!text) return;

            if (aiStatusBadge) {
                aiStatusBadge.innerText = 'ANALYZING...';
                aiStatusBadge.style.color = '#00f0ff';
                aiStatusBadge.style.borderColor = '#00f0ff';
            }

            analyzerOutput.innerHTML = `<div class="line t-purple"><i class="fa-solid fa-spinner fa-spin"></i> HackGPT AI Router selecting optimal LLM provider (OpenAI GPT-4o)...</div>
            <div class="line t-blue">[+] Synthesizing code semantics and vulnerability attack vectors...</div>`;

            setTimeout(() => {
                let analysisHTML = '';
                if (text.includes('SELECT') || text.includes('query')) {
                    analysisHTML = `
<div class="line t-red"><strong>[CRITICAL FINDING] SQL Injection (CWE-89 / OWASP A03:2021)</strong></div>
<div class="line">--------------------------------------------------</div>
<div class="line"><strong>CVSS v3.1 Base Score:</strong> <span class="t-red">9.8 (CRITICAL)</span></div>
<div class="line"><strong>Attack Vector:</strong> Parameter concatenation in SQL string query allows unauthenticated remote data extraction or database compromise.</div>
<br>
<div class="line t-cyan"><strong>[PoC Exploit Vector]</strong></div>
<div class="line"><code>/api/users/search?query=admin' OR '1'='1</code></div>
<br>
<div class="line t-green"><strong>[HackGPT AI Remediation]</strong></div>
<div class="line">Use parameterized SQL queries:</div>
<div class="line"><code>const result = await db.query("SELECT * FROM users WHERE name = $1", [query]);</code></div>
<br>
<div class="line t-purple"><strong>Compliance Mapping:</strong> OWASP A03:2021 | PCI-DSS v4.0 Req 6.2.4 | NIST SP 800-53 SI-10</div>`;
                } else if (text.includes('docker.sock')) {
                    analysisHTML = `
<div class="line t-red"><strong>[HIGH FINDING] Container Breakout via Docker Socket Exposure (CWE-250)</strong></div>
<div class="line">--------------------------------------------------</div>
<div class="line"><strong>CVSS v3.1 Base Score:</strong> <span class="t-red">8.8 (HIGH)</span></div>
<div class="line"><strong>Attack Vector:</strong> Mounting <code class="inline-code">/var/run/docker.sock</code> into container grants host root access via Docker API call.</div>
<br>
<div class="line t-green"><strong>[HackGPT AI Remediation]</strong></div>
<div class="line">Remove host socket mount or use rootless Docker sockets with strict RBAC access controls.</div>
<br>
<div class="line t-purple"><strong>Compliance Mapping:</strong> CIS Docker Benchmark 2.1 | NIST SP 800-190 Sec 4.2</div>`;
                } else {
                    analysisHTML = `
<div class="line t-yellow"><strong>[VULNERABILITY DETECTED] High Severity Execution Risk</strong></div>
<div class="line">--------------------------------------------------</div>
<div class="line"><strong>CVSS v3.1 Base Score:</strong> <span class="t-yellow">8.1 (HIGH)</span></div>
<div class="line"><strong>Attack Vector:</strong> Unsanitized input leads to privilege escalation or unauthorized security boundary bypass.</div>
<br>
<div class="line t-green"><strong>[HackGPT AI Remediation]</strong></div>
<div class="line">Enforce strict input validation whitelist and enforce principle of least privilege.</div>
<br>
<div class="line t-purple"><strong>Compliance Mapping:</strong> OWASP Top 10 | NIST SP 800-53</div>`;
                }

                analyzerOutput.innerHTML = analysisHTML;
                if (aiStatusBadge) {
                    aiStatusBadge.innerText = 'ANALYSIS COMPLETE';
                    aiStatusBadge.style.color = '#00ff66';
                    aiStatusBadge.style.borderColor = '#00ff66';
                }
            }, 1200);
        });
    }

    // 5. Interactive Terminal Simulator
    const terminalInput = document.getElementById('terminalInput');
    const interactiveTerminal = document.getElementById('interactiveTerminal');

    if (terminalInput && interactiveTerminal) {
        terminalInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const cmdText = terminalInput.value.trim();
                terminalInput.value = '';

                if (cmdText) {
                    processCommand(cmdText);
                }
            }
        });
    }

    function writeLine(text, cssClass = '') {
        const line = document.createElement('div');
        line.className = 'line' + (cssClass ? ' ' + cssClass : '');
        line.innerHTML = text;

        const inputLine = interactiveTerminal.querySelector('.terminal-input-line');
        interactiveTerminal.insertBefore(line, inputLine);
        interactiveTerminal.scrollTop = interactiveTerminal.scrollHeight;
    }

    function processCommand(cmd) {
        writeLine(`<span class="t-cyan">guest@hackgpt:~$</span> ${cmd}`);
        const lowerCmd = cmd.toLowerCase().trim();

        if (lowerCmd === 'clear') {
            const lines = interactiveTerminal.querySelectorAll('.line');
            lines.forEach(l => l.remove());
            return;
        }

        if (lowerCmd === 'help') {
            writeLine('HackGPT Security Shell Commands:');
            writeLine('  <span class="t-cyan">help</span>             - Show list of available commands');
            writeLine('  <span class="t-cyan">about</span>            - Display HackGPT architecture overview');
            writeLine('  <span class="t-cyan">run</span>              - Simulate full 6-phase pentest session');
            writeLine('  <span class="t-cyan">ai-analyze</span>       - Run AI Threat Analysis module');
            writeLine('  <span class="t-cyan">zero-day</span>         - Execute DBSCAN ML anomaly detector');
            writeLine('  <span class="t-cyan">compliance</span>       - View OWASP / NIST / PCI-DSS compliance state');
            writeLine('  <span class="t-cyan">version</span>          - Print HackGPT framework release info');
            writeLine('  <span class="t-cyan">clear</span>            - Clear terminal screen');
            return;
        }

        if (lowerCmd === 'about') {
            writeLine('<strong>HackGPT Enterprise Framework v2026.09.26</strong>');
            writeLine('Created by Yashab Alam. HackGPT is an AI-driven penetration testing platform combining multi-provider LLMs, safe exploitation engines, and machine learning zero-day log clustering.');
            return;
        }

        if (lowerCmd === 'run' || lowerCmd.startsWith('scan')) {
            writeLine('[+] Initiating HackGPT 6-Phase Pentest Engine...', 't-blue');
            setTimeout(() => writeLine('[+] Phase 1: Reconnaissance complete. Discovered 3 open ports (80, 443, 8080).', 't-green'), 400);
            setTimeout(() => writeLine('[+] Phase 2: Vulnerability Enumeration complete. 1 Critical SQLi found.', 't-yellow'), 800);
            setTimeout(() => writeLine('[!] Phase 3: AI Threat Intelligence synthesized non-destructive PoC.', 't-purple'), 1200);
            setTimeout(() => writeLine('[+] Phase 4: Safe Exploitation verified. Database admin access confirmed.', 't-green'), 1600);
            setTimeout(() => writeLine('[+] Phase 5: Zero-Day ML clustering completed. 2 anomaly logs grouped.', 't-cyan'), 2000);
            setTimeout(() => writeLine('[+] Phase 6: PDF Audit Report generated successfully!', 't-green'), 2400);
            return;
        }

        if (lowerCmd === 'ai-analyze') {
            writeLine('[+] Invoking Multi-Provider AI Threat Intelligence Router...', 't-purple');
            setTimeout(() => {
                writeLine('<strong>[AI Threat Report]</strong> Target: production-api.net', 't-cyan');
                writeLine('  - Vulnerability: Unauthenticated JWT Algorithm Switch ("none")', 't-red');
                writeLine('  - Severity: HIGH (CVSS 8.5)', 't-yellow');
                writeLine('  - Remediation: Enforce strict RS256 algorithm validation in auth middleware.', 't-green');
            }, 800);
            return;
        }

        if (lowerCmd === 'zero-day') {
            writeLine('[+] Executing DBSCAN & Isolation Forest log anomaly detector...', 't-blue');
            setTimeout(() => {
                writeLine('[+] Processed 14,250 HTTP access log entries.', 't-cyan');
                writeLine('[!] Identified 3 outlier clusters matching potential zero-day payload probes.', 't-yellow');
                writeLine('[✓] Anomaly report attached to audit output.', 't-green');
            }, 900);
            return;
        }

        if (lowerCmd === 'compliance') {
            writeLine('Enterprise Compliance Standard Status:');
            writeLine('  - OWASP Top 10 (2021) : <span class="t-green">PASS</span> (A01, A03, A05 mapped)');
            writeLine('  - NIST SP 800-53     : <span class="t-green">PASS</span> (SI-10, SI-11 controls active)');
            writeLine('  - PCI-DSS v4.0       : <span class="t-red">FAIL</span> (Req 6.2.4 SQLi vulnerability detected)');
            writeLine('  - ISO/IEC 27001      : <span class="t-green">PASS</span> (A.12.6.1 Vulnerability management)');
            return;
        }

        if (lowerCmd === 'version') {
            writeLine('HackGPT Enterprise v2026.09.26 (Python 3.14 / Node 18 runtime)', 't-green');
            return;
        }

        writeLine(`bash: command not found: ${cmd}. Type <span class="t-cyan">help</span> for available commands.`, 't-red');
    }
});

// Copy snippet helper
function copyText(elementId, btnElement) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const textToCopy = el.innerText || el.textContent;
    navigator.clipboard.writeText(textToCopy).then(() => {
        if (btnElement) {
            const originalHTML = btnElement.innerHTML;
            btnElement.innerHTML = '<i class="fa-solid fa-check text-green"></i> Copied!';
            setTimeout(() => {
                btnElement.innerHTML = originalHTML;
            }, 2000);
        }
    });
}

function copyPipeCode() {
    const codeEl = document.getElementById('pipeCode');
    if (codeEl) {
        navigator.clipboard.writeText(codeEl.innerText).then(() => {
            alert('CLI command copied to clipboard!');
        });
    }
}
