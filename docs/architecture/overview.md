# Architecture Overview

## System Context
Herald Crypto is an institutional-grade multi-product crypto exchange supporting spot, dated futures, perpetuals, and European cash-settled options.

## Architectural Principles
1. Event-sourced with append-only journals for deterministic replay
2. Immutable double-entry ledger for all economic events
3. Single-writer per order book shard (no active-active matching)
4. Custody plane isolated from trading and public planes
5. Bounded failure domains with explicit RTO/RPO targets

## Bounded Contexts
- **Trading:** Order entry, matching, market data
- **Risk:** Pre-trade checks, margin, liquidation
- **Clearing:** Settlement, fees, PnL
- **Ledger:** Double-entry accounting, balances
- **Custody:** Wallet management, signing, chain adapters
- **Fiat:** Treasury, bank rails
- **Identity:** Authentication, authorization, sessions
- **Compliance:** KYC/KYB, sanctions, AML, Travel Rule
- **Surveillance:** Market abuse detection, evidence pipelines
- **Data:** Event schemas, CDC, analytics

## Technology Stack
- **Matching Engine:** Rust (zero-alloc hot path)
- **Services:** Go
- **Frontend:** TypeScript / React
- **Data:** ClickHouse, PostgreSQL, Redis
- **Messaging:** Kafka / Redpanda
- **Infrastructure:** Kubernetes (non-hot-path), bare metal (matching)

## Deployment Architecture
To be defined in ARCH-001 deliverables.
