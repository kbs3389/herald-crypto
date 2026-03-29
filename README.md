# Herald Crypto Exchange

## Institutional Grade Multi-Product Crypto Exchange

An institutional-grade crypto exchange supporting **spot**, **dated futures**, **perpetuals**, and **European cash-settled options** with an ultra-low-latency matching core, bank-grade internal accounting, custody isolation, compliant institutional connectivity, and multi-million-user scale.

Built using a **multi-agent architecture** with 27 specialized agents across 7 execution phases.

See `agents/` for agent definitions, `phases/` for task orchestration, and `src/` for core implementation.

## Hard Constraints

- One active writer per order book or shard. No active-active matching.
- Stateful trading commands must be sequenced and replayable from an append-only journal.
- All economic events land in an append-only immutable double-entry ledger.
- Balances derived from ledger state and controlled reservations, not manual edits.
- Matching loop must not make synchronous DB calls or remote network calls.
- Custody, wallet signing, and key material isolated from public app and trading planes.
- Market makers and house accounts must not bypass risk, surveillance, or audit controls.
- Kubernetes is not allowed inside the matching hot path.
- Admin access requires phishing-resistant hardware-backed authentication.
- Retail auth defaults to passkeys/WebAuthn; admins require hardware keys.
- Institutional APIs support cancel-on-disconnect, kill switch, drop copy, idempotency.
- Design for deterministic recovery, bounded failure domains, explicit RTO/RPO targets.
- Compliant market making only. No spoofing, layering, wash trading, or manipulation.
- Day-1 portfolio margin bounded to well-defined risk groups.
- All admin/risk/wallet/listing/compliance actions must be auditable.

## Project Structure

```
herald-crypto/
├── agents/              # 27 agent definitions with system prompts
├── phases/              # 7 execution phases with task definitions
├── src/core/            # Core domain models and business logic
├── src/services/        # Application services
├── src/api/             # API layer (REST, WebSocket, FIX)
├── src/infrastructure/  # Messaging, persistence, cache, observability
├── docs/                # ADRs, architecture, threat model, runbooks
├── reviews/             # Review prompt templates
├── tests/               # Unit, integration, e2e, performance tests
└── scripts/             # Build, deploy, and utility scripts
```

## How to Use

1. Pick the next phase from `phases/` and select a task whose dependencies are met.
2. Load `global_context.yaml`, `agent_execution_protocol.yaml`, the agent's `system_prompt.md`, and the task.
3. Pass agent system_prompt as system message and task_prompt as user message.
4. Provide dependency artifacts as additional context.
5. After each task, run review templates from `reviews/`.
6. The orchestrator blocks promotion when critical findings are unresolved.
