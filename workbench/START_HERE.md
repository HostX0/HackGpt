# Start here: the existing Evidence Workbench

This is a simpler **additive launcher**, not a replacement application or an enterprise installer. All existing assessment, adapter, model, report and GUI modules remain in place.

## 1. Check and start

Extract the complete portable source archive, or use this fork's reviewed checkout. Python **3.11 or newer** is the only required application runtime. No pip packages, root access, cloud account, model or scanner download is required for the native no-AI path.

From the extracted repository/package root:

```sh
python workbench/start.py --check-install
python workbench/start.py --open-browser
```

Use `python3` instead of `python` where needed. The check tests application files, SQLite in memory, a temporary workspace write and loopback port availability. It creates the workspace/lock file if absent, but does **not** open, inspect or recover existing reports. With `--json`, failures identify a stable non-sensitive `check` and `code` such as `workspace_write` / `workspace_not_writable` or `loopback_port` / `loopback_port_unavailable`; workspace preparation and unsafe lock-object failures are separately reported under `workspace_lock`, without returning local filesystem/socket exception text. A successful check is not a full application, model or security validation.

Windows also has `workbench/start.cmd`. macOS/Linux has `workbench/start.command` (run `sh workbench/start.command` if executable permission was not retained). With no arguments these helpers request the browser; with arguments they pass them unchanged. OS download warnings, Python installation and native code signing are not bypassed. These are launch helpers, not signed native installers.

```sh
python workbench/start.py --port 8766 --data-dir ./local-workbench-data
python workbench/start.py --check-install --json
```

The default browser opens only with `--open-browser` or the helper's no-argument shortcut. Browser-launch success does not prove the page loaded. If it cannot open, use the private URL printed in the terminal. Keep the terminal running and stop with Ctrl+C. Never share the URL containing the session token, expose the server publicly or place it behind a tunnel.

## 2. Run the owned example without AI

In the existing GUI select **Built-in synthetic lab**, **Controlled verification**, enter a non-secret authorization reference and confirm authorization plus verification approval. Leave AI off. Run, review the observed/verified-in-lab distinction, open history and export the JSON/Markdown report. This demonstrates only the disposable owned fixture, not compromise of a real website. No external target is used by this walkthrough.

## 3. Connect AI explicitly

The existing **Detect**, **Check model** and **Test response** controls guide model selection. Detect/check do not infer; Test response is an explicit fixed-prompt inference probe. Nothing downloads or selects a model automatically. Ollama is the implemented reference adapter, not a permanent gateway requirement for future providers.

Choose a model deliberately; tool-directed synthetic verification requires reported tool capability. Cloud-backed inference needs the separate engagement-specific opt-in and disclosed minimized context. Localhost transport alone does not prove local inference. See [OLLAMA.md](OLLAMA.md).

AI can currently choose the finite approved synthetic-lab action or stop and supply validated commentary. It is **not** an unrestricted agent controlling every scanner. Reviewed project/web adapters already have a separate **plan -> approve exact request -> execute** GUI/API path. A clearer combined agent/operator journey is still outstanding, not silently claimed by this launcher.

## 4. Tools and reports

Native metadata checks need no external scanner. The reviewed Semgrep runner needs its exact separately provisioned image; startup does not pull it. Other scanner execution is limited as documented in [README.md](README.md) and [ADAPTERS.md](ADAPTERS.md). No model may introduce a shell command, expand scope or override approval/budgets.

Reports and adapter execution receipts remain available in the existing interface. Receipts are a separate audit trail. After a completed receipt, **Add to report** explicitly creates a normal review/export report without rerunning the adapter or AI. **View linked report** opens that report in the existing evidence panel; observations stay candidates. It cannot interrupt an active assessment or model test. Internal exports may contain sensitive assessment information and are not universally sanitized client handovers. No findings does not mean safe; no reproduction alone does not mean fixed.

## 5. Duplicate startup and recovery

This launcher takes an advisory local OS lock **before** report recovery. A second cooperating launch for the same data directory fails without opening the report database, even on another port. Process death releases the OS lock; do not delete `.starter.lock`. A busy port also fails a preflight before state initialization; the port check is point-in-time, not a reservation against other applications.

The original `python -m workbench`, `workbench.server`, `workbench.workspace_server` entry points and embedding APIs are deliberately unchanged. **They do not participate in this new lock.** Do not mix them with the managed launcher against the same data directory. This is not multi-user/distributed locking, malicious-local-user protection or a guarantee for network filesystems. Reports are not encrypted at rest.

See [PROGRESS.md](PROGRESS.md) for exact local/hosted evidence and remaining compatibility work. The inherited enterprise installer/CI remains separate; do not run it to start this Workbench.

## 6. Slow requests and reconnecting

Adapter inputs lock as soon as planning starts, so the displayed target stays aligned with the request being reviewed. Reset waits for pending approval or report linking. A partial/error/skipped adapter result remains visible even when receipt persistence succeeded; a completed HTTP request is not proof that the assessment completed.

After an interrupted connection, **Check run status** reads the existing adapter record without retrying execution. Unknown or executing states keep new execution disabled. If terminal receipt persistence fails after an adapter returns, the service does not relabel that as a successful durable run: it records an `interrupted` state when possible, exposes no receipt, and instructs the operator to check status instead of automatically running the tool again. Stop requests remain requests until the service confirms the terminal outcome. For the assessment panel, **Refresh** reconnects an unconfirmed run rather than starting another one. Late responses from an earlier selection cannot replace the current comparison or rename an export to a different report.
