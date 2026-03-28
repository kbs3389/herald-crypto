# Phase 03: Futures and Perpetuals

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
