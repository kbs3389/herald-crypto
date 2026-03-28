import os
os.chdir('/home/ubuntu/herald-crypto')

phases = {
    'phases/phase_01_foundation/tasks.md': """# Phase 01: Platform, Identity, and Financial Foundation

## Objective
Set up repo, schemas, identity, ledger, accounts, custody, fiat, and asset metadata foundations.

## Tasks

### PLAT-001 - Design repo topology, build system, environments, and CI/CD bootstrap
- **Agent:** platform_builder
- **Depends On:** ARCH-001, DOMAIN-001
- **Status:** pending

### DATA-001 - Design canonical event schemas, message contracts, and schema governance
- **Agent:** data_builder
- **Depends On:** DOMAIN-001
- **Status:** pending

### IAM-001 - Design user auth, admin auth, sessions, and API credential lifecycles
- **Agent:** iam_builder
- **Depends On:** ARCH-001, SEC-001
- **Status:** pending

### IAM-002 - Design delegated permissions, account roles, and operational authorization
- **Agent:** iam_builder
- **Depends On:** IAM-001
- **Status:** pending

### LEDGER-001 - Design the immutable double-entry ledger and chart of accounts
- **Agent:** ledger_builder
- **Depends On:** DOMAIN-001, ARCH-001
- **Status:** pending

### LEDGER-002 - Design reservations, holds, releases, and reconciliation flows
- **Agent:** ledger_builder
- **Depends On:** LEDGER-001
- **Status:** pending

### ACC-001 - Design the full account hierarchy and house account system
- **Agent:** accounts_builder
- **Depends On:** LEDGER-001, IAM-001
- **Status:** pending

### CUST-001 - Design the custody plane, wallet tiers, and signing control architecture
- **Agent:** custody_builder
- **Depends On:** ARCH-001, SEC-001
- **Status:** pending

### CUST-002 - Design chain adapters, deposit watchers, withdrawal release, and reorg handling
- **Agent:** custody_builder
- **Depends On:** CUST-001
- **Status:** pending

### FIAT-001 - Design fiat treasury, bank rail state machines, and break handling
- **Agent:** fiat_builder
- **Depends On:** LEDGER-001, ACC-001
- **Status:** pending

### ASSET-001 - Design canonical asset and instrument reference data plus listing lifecycle
- **Agent:** asset_builder
- **Depends On:** DOMAIN-001
- **Status:** pending
""",

    'phases/phase_02_spot/tasks.md': """# Phase 02: Spot Trading Core

## Objective
Implement spot trading from ingress to matching, clearing, market data, retail API, UI, admin tools, and surveillance.

## Tasks

### EDGE-001 - Design edge ingress, gateways, normalization, and pre-sequencing controls
- **Agent:** edge_builder
- **Depends On:** ARCH-001, IAM-001
- **Status:** pending

### MATCH-001 - Design the deterministic spot matching engine shard
- **Agent:** matching_builder
- **Depends On:** ARCH-001, DOMAIN-001
- **Status:** pending

### MATCH-002 - Design ingress journaling, snapshots, replay, and failover for spot shards
- **Agent:** matching_builder
- **Depends On:** MATCH-001
- **Status:** pending

### RISK-001 - Design spot pre-trade risk, balance checks, and price-protection rules
- **Agent:** risk_builder
- **Depends On:** LEDGER-001, MATCH-001
- **Status:** pending

### CLEAR-001 - Design spot clearing, fees, and post-trade ledger integration
- **Agent:** clearing_builder
- **Depends On:** LEDGER-001, MATCH-001
- **Status:** pending

### MD-001 - Design the spot market data plant and private execution stream
- **Agent:** market_data_builder
- **Depends On:** MATCH-001
- **Status:** pending

### API-001 - Design the retail REST and WebSocket trading and account APIs
- **Agent:** api_builder
- **Depends On:** EDGE-001, MATCH-001, IAM-001
- **Status:** pending

### FRONT-001 - Design the retail trading UX, wallet UX, and account information architecture
- **Agent:** frontend_builder
- **Depends On:** API-001
- **Status:** pending

### BACK-001 - Design the initial backoffice consoles
- **Agent:** backoffice_builder
- **Depends On:** IAM-002, ACC-001
- **Status:** pending

### SURV-001 - Design day-1 spot market surveillance and account-behavior detection
- **Agent:** surveillance_builder
- **Depends On:** MATCH-001, CLEAR-001
- **Status:** pending

### COMP-002 - Design onboarding, sanctions, AML monitoring, and restriction workflows
- **Agent:** compliance_builder
- **Depends On:** IAM-001, ACC-001, COMP-001
- **Status:** pending

### ORCH-002 - Run the spot launch readiness gate
- **Agent:** orchestrator
- **Depends On:** All Phase 02 tasks
- **Status:** pending
""",

    'phases/phase_03_derivatives/tasks.md': """# Phase 03: Futures and Perpetuals

## Objective
Implement derivatives contracts, mark/index/funding, margin, liquidation, institutional connectivity, and derivatives surveillance.

## Tasks

### INSTR-001 - Design dated futures and perpetual contract frameworks
- **Agent:** asset_builder
- **Depends On:** ASSET-001, MATCH-001
- **Status:** pending

### ORACLE-001 - Design index price, mark price, and funding-rate services
- **Agent:** market_data_builder
- **Depends On:** MD-001, INSTR-001
- **Status:** pending

### RISK-002 - Design derivatives margin, maintenance thresholds, and bounded cross-margin groups
- **Agent:** risk_builder
- **Depends On:** RISK-001, INSTR-001
- **Status:** pending

### LIQ-001 - Design liquidation flows, bankruptcy logic, insurance fund usage, and ADL/default waterfall
- **Agent:** risk_builder
- **Depends On:** RISK-002
- **Status:** pending

### CLEAR-002 - Design derivatives clearing, positions, funding settlement, and realized PnL accounting
- **Agent:** clearing_builder
- **Depends On:** CLEAR-001, INSTR-001, RISK-002
- **Status:** pending

### MD-002 - Design derivatives public/private feeds, mark/index distribution, and private risk streams
- **Agent:** market_data_builder
- **Depends On:** MD-001, ORACLE-001
- **Status:** pending

### API-002 - Design institutional FIX, binary order entry, and drop-copy connectivity
- **Agent:** api_builder
- **Depends On:** API-001, INSTR-001
- **Status:** pending

### MM-001 - Design compliant market-making APIs and safe quoting frameworks
- **Agent:** market_making_builder
- **Depends On:** API-002, MATCH-001
- **Status:** pending

### SURV-002 - Design derivatives surveillance including mark/index abuse and cross-account patterns
- **Agent:** surveillance_builder
- **Depends On:** SURV-001, INSTR-001, ORACLE-001
- **Status:** pending

### QA-001 - Design the end-to-end verification harness for spot plus derivatives
- **Agent:** qa_builder
- **Depends On:** MATCH-001, MATCH-002, CLEAR-001, CLEAR-002
- **Status:** pending

### ORCH-003 - Run the derivatives launch readiness gate
- **Agent:** orchestrator
- **Depends On:** All Phase 03 tasks
- **Status:** pending
""",

    'phases/phase_04_options/tasks.md': """# Phase 04: Options

## Objective
Implement European cash-settled options, vol/greeks, bounded portfolio risk, settlement, and options UX.

## Tasks

### OPT-001 - Design European cash-settled options contract model and lifecycle
- **Agent:** asset_builder
- **Depends On:** INSTR-001
- **Status:** pending

### OPT-002 - Design vol surface, greeks, and options valuation services
- **Agent:** market_data_builder
- **Depends On:** ORACLE-001, OPT-001
- **Status:** pending

### RISK-003 - Design options scenario margin and bounded portfolio grouping
- **Agent:** risk_builder
- **Depends On:** RISK-002, OPT-001
- **Status:** pending

### CLEAR-003 - Design options premium accounting, expiry, and cash settlement flows
- **Agent:** clearing_builder
- **Depends On:** CLEAR-002, OPT-001
- **Status:** pending

### MM-002 - Design compliant options market making and hedging workflows
- **Agent:** market_making_builder
- **Depends On:** MM-001, OPT-001
- **Status:** pending

### FRONT-002 - Design the options trading, risk, and portfolio UX
- **Agent:** frontend_builder
- **Depends On:** FRONT-001, OPT-001, OPT-002
- **Status:** pending

### QA-002 - Design options-specific scenario, replay, and shock testing
- **Agent:** qa_builder
- **Depends On:** QA-001, OPT-001
- **Status:** pending

### ORCH-004 - Run the options launch readiness gate
- **Agent:** orchestrator
- **Depends On:** All Phase 04 tasks
- **Status:** pending
""",

    'phases/phase_05_hardening/tasks.md': """# Phase 05: Cross-Cutting Hardening

## Objective
Implement analytics, compliance ops, zero trust, supply-chain hardening, DR, chaos, and performance engineering.

## Tasks

### DATA-002 - Design CDC, warehouse, lakehouse, and analytics marts
- **Agent:** data_builder
- **Depends On:** DATA-001, CLEAR-001, CLEAR-002
- **Status:** pending

### COMP-003 - Design Travel Rule handling, case management, and evidence retention
- **Agent:** compliance_builder
- **Depends On:** COMP-002
- **Status:** pending

### SURV-003 - Design on-chain/off-chain graph fusion and link analysis
- **Agent:** surveillance_builder
- **Depends On:** SURV-002
- **Status:** pending

### SEC-002 - Design zero-trust segmentation, admin planes, and privileged-access hardening
- **Agent:** security_architect
- **Depends On:** SEC-001, IAM-002
- **Status:** pending

### SEC-003 - Design secrets management, artifact signing, SBOM, and supply-chain controls
- **Agent:** security_architect
- **Depends On:** SEC-001, PLAT-001
- **Status:** pending

### SRE-002 - Design multi-region failover, backups, and disaster recovery
- **Agent:** sre_builder
- **Depends On:** SRE-001, ARCH-001
- **Status:** pending

### SRE-003 - Design runbooks, alert routing, tabletop exercises, and chaos validation
- **Agent:** sre_builder
- **Depends On:** SRE-002
- **Status:** pending

### PERF-001 - Design hot-path benchmarks and end-to-end performance harnesses
- **Agent:** performance_builder
- **Depends On:** MATCH-001, MATCH-002
- **Status:** pending

### PERF-002 - Design the multi-million-user session, API, and market-data scale plan
- **Agent:** performance_builder
- **Depends On:** PERF-001, API-001, MD-001
- **Status:** pending
""",

    'phases/phase_06_final_readiness/tasks.md': """# Phase 06: Final Operational Readiness

## Objective
Publish operating manuals, complete go-live reviews, and lock in the scale plan.

## Tasks

### DOC-002 - Publish operating manuals, service catalogs, runbook index, and onboarding guides
- **Agent:** docs_builder
- **Depends On:** DOC-001, SRE-003
- **Status:** pending

### ORCH-005 - Run the final operational acceptance review and release decision
- **Agent:** orchestrator
- **Depends On:** DOC-002, PERF-002, SRE-003, SEC-003, COMP-003, SURV-003
- **Status:** pending
""",

    'phases/phase_task_index.md': """# Phase Task Index

## Overview
- **Total Phases:** 7 (Phase 00 through Phase 06)
- **Total Tasks:** 60
- **Total Agents:** 27
- **Total Reviews:** 6

## Phase Summary

| Phase | Name | Tasks |
|---|---|---|
| 00 | Bootstrap | 7 |
| 01 | Foundation | 11 |
| 02 | Spot | 12 |
| 03 | Derivatives | 11 |
| 04 | Options | 8 |
| 05 | Hardening | 9 |
| 06 | Final | 2 |

## Status Legend
- `pending` - Not yet started
- `in_progress` - Currently being executed
- `review` - Awaiting review
- `blocked` - Blocked by unresolved findings
- `complete` - Deliverables produced and reviews passed
"""
}

for path, content in phases.items():
    with open(path, 'w') as f:
        f.write(content)
    print(f'Created {path}')

print('ALL PHASES DONE')
