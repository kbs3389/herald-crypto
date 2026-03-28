# Phase 02: Spot Trading Core

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
