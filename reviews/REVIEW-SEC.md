# REVIEW-SEC: Security Review

## Purpose
Review the target artifact for authn/authz strength, trust boundaries, secrets handling, abuse resistance, auditability, and privileged-action controls.

## Checklist
- [ ] Admin auth requires hardware-backed credentials (HC-009)
- [ ] Retail auth defaults to passkeys/WebAuthn (HC-010)
- [ ] Trust boundaries align with architecture plane separation
- [ ] No secrets in code, config, or logs
- [ ] Privileged actions require maker-checker approval
- [ ] All auth/authz events are immutably logged
- [ ] No hidden bypasses for house accounts or internal desks (HC-007)
- [ ] API keys support scoped permissions and IP whitelisting
- [ ] Supply chain controls enforced (artifact signing, SBOM)
- [ ] Session management is secure (no fixation, proper expiry)

## Output Format
- **Findings:** List of observations
- **Severity:** Critical / Major / Minor / Info
- **Exploit Narrative:** How could an attacker exploit this?
- **Remediation:** Required fixes
- **Verdict:** PASS / FAIL
