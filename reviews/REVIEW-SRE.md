# REVIEW-SRE: Operability and Resilience Review

## Purpose
Review the target artifact for SLO fit, observability, failure-mode coverage, runbook completeness, failover impact, and operational simplicity.

## Checklist
- [ ] SLOs defined for availability, latency, and correctness
- [ ] RTO/RPO targets explicit and achievable (HC-012)
- [ ] Observability covers metrics, tracing, and structured logging
- [ ] Failure modes enumerated with recovery procedures
- [ ] Runbooks concrete enough for on-call use
- [ ] Alerts have defined severity and escalation paths
- [ ] Failover is tested and deterministic
- [ ] Recovery via journal replay produces identical state (HC-002)
- [ ] Failure domains are bounded (no cascading failures)
- [ ] Dashboards cover operational health indicators

## Output Format
- **Findings:** List of observations
- **Operational Risks:** Risks to production operations
- **Remediation:** Required fixes
- **Verdict:** PASS / FAIL
