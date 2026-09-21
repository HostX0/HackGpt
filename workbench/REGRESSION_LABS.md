# Regression lab catalog

This catalog maps owned/synthetic fixtures to the security property they validate. It is evidence about the workbench implementation, not proof that an external target has or lacks the same condition.

| Fixture | Property under test | Expected vulnerable/negative behavior | Expected corrected/control behavior | Network boundary |
|---|---|---|---|---|
| Authorization canary lab | Missing authorization can be demonstrated without customer data | Fresh synthetic marker is readable from the deliberately vulnerable route | Independent control denies access; fixed lab no longer demonstrates the condition | Loopback only |
| Native web-header logic fixture | Candidate header observations and honest coverage | Missing reviewed response-hardening header yields candidate observation | Header present yields no candidate for that rule | In-memory/owned test reader |
| Native web-header transport fixture | Production reader uses HEAD only, no redirects/body | Owned fixture receives at most the reviewed HEAD request | GET/body path is never used | Loopback with target-resolution/connect boundary redirected by the test |
| Project metadata fixture | Read-only bounded project inventory | Reviewed filename pattern can produce candidate metadata observation | Corrected fixture removes that observation | Temporary local directory; filenames/metadata only |
| Access-control matrix fixture | Role/resource expectation comparison | Unexpected allow remains a candidate access-control observation | Expected deny/control does not become a finding | Execution-neutral normalized fixture |
| Adapter parser fixtures | Malformed/oversized scanner data fails closed | Valid minimized Semgrep/Trivy/Nuclei fixture normalizes candidate findings | Malformed, truncated or oversized input is rejected/inconclusive | Offline only; no scanner process |
| DNS deadline/cancel fixture | Resolver cannot consume the whole assessment silently | Slow resolver is bounded/cancellable | Result arriving in budget is accepted and still subject to public-address validation | Synthetic resolver thread |
| Pending-connect fixture | TCP connect honors cancel/deadline | Pending connect exits within bounded budget | Normal owned connect proceeds | Owned/synthetic socket boundary |
| Silent TLS fixture | TLS handshake honors shared deadline/cancel | Silent peer cannot block indefinitely | Normal handshake path remains bounded | Loopback TCP peer |
| Slow HTTP fixture | Response wait honors deadline/cancel | Slow HEAD response is interrupted/bounded | Fast HEAD response completes | Loopback HTTP server |
| Slow model transport fixture | Model runtime honors attached deadline/cancel | Delayed protocol endpoint yields cancelled/deadline error | Timely synthetic protocol response is parsed | Loopback Ollama-protocol fixture |
| Persistence failure fixture | Final result is not falsely durable | Simulated storage failure marks terminal result memory-only and blocks review export/comparison | Successful transaction publishes sealed durable report | Temporary SQLite |
| Restart recovery fixture | Running job cannot become completed after crash | Stale active checkpoint recovers to interrupted/inconclusive | Clean terminal transaction retires checkpoint | Temporary SQLite |
| Retest comparison fixtures | Missing finding is not automatically fixed | Failed/skipped/unmapped or changed scope remains not_retested | Comparable completed recheck may yield not_reproduced; existing finding remains still_present | Offline report fixtures |

## Lab evidence rules

1. Every proof fixture is clearly labeled synthetic/owned.
2. A vulnerable fixture must have a denied/corrected control where the claim needs one.
3. A successful lab proof never changes the target label to an external host.
4. Ordinary customer rows, real credentials and reusable secrets are prohibited from regression fixtures.
5. Scanner parser fixtures do not imply the corresponding binary was executed.
6. Protocol doubles do not count as live local/cloud model inference.
7. DOM/fetch doubles do not count as browser-to-server E2E.
8. Timing tests must assert bounded behavior rather than requiring a race-sensitive server-side event to have happened.

## Missing release-lab evidence

Gate E still requires a documented real browser-to-loopback E2E/accessibility run, fresh-install smoke tests on documented operating systems, and a real-model compatibility check distinct from protocol doubles. Future third-party runners require pinned/licensed runner fixtures before they can be represented as executable capabilities.
