# Phase 04: Options

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
