# REVIEW-ARCH: Architecture Conformance Review

## Purpose
Review the target artifact for consistency with global_context, state ownership, and bounded contexts.

## Checklist
- [ ] Consistent with target-state architecture from ARCH-001
- [ ] No dual writes or ambiguous state ownership
- [ ] Single-writer rule respected for all order book shards (HC-001)
- [ ] No invalid sync/async coupling across bounded contexts
- [ ] Failure domains are bounded and explicitly defined
- [ ] Matching hot path has no synchronous I/O (HC-005)
- [ ] Kubernetes not used in matching hot path (HC-008)
- [ ] Custody plane properly isolated (HC-006)
- [ ] Event sourcing patterns correctly applied (HC-002)

## Output Format
- **Findings:** List of observations
- **Severity:** Critical / Major / Minor / Info
- **Required Changes:** Must-fix items before promotion
- **Suggested ADR Updates:** New decisions to document
- **Verdict:** PASS / FAIL
