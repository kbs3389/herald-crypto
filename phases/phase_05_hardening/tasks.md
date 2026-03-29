# Phase 05: Cross-Cutting Hardening

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
