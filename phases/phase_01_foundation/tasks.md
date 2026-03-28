# Phase 01: Platform, Identity, and Financial Foundation

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
