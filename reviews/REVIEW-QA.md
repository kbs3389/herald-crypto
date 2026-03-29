# REVIEW-QA: Verification Review

## Purpose
Review the target artifact for testability, invariant coverage, replayability, determinism, and scenario completeness.

## Checklist
- [ ] Happy paths covered with expected outcomes
- [ ] Failure paths covered with error handling verification
- [ ] Recovery paths covered with state restoration checks
- [ ] Edge conditions and boundary values tested
- [ ] Deterministic replay produces identical results
- [ ] Domain invariants are machine-verifiable
- [ ] Fuzzing covers all external input surfaces
- [ ] Property-based tests cover domain logic
- [ ] Performance characteristics verified under load
- [ ] Cross-component integration scenarios defined

## Output Format
- **Gaps:** Missing test coverage
- **Proposed Tests:** New tests to add
- **Formal Invariant Candidates:** Properties for formal verification
- **Verdict:** PASS / FAIL
