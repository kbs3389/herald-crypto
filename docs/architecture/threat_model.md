# Threat Model

## Overview
This document outlines the threat model for the Herald Crypto Exchange platform, identifying assets, threat actors, attack surfaces, and mitigations.

## Assets
1. Customer funds (crypto and fiat)
2. Private keys and signing material
3. Customer PII and account data
4. Trading data and order flow
5. System availability and integrity

## Threat Actors
1. External attackers (opportunistic and targeted)
2. Malicious insiders (employees, contractors)
3. Compromised third parties (vendors, APIs)
4. Nation-state actors
5. Malicious customers (market manipulation, fraud)

## Attack Surfaces
1. Public APIs (REST, WebSocket)
2. Institutional APIs (FIX, binary)
3. Admin interfaces
4. Blockchain integrations
5. Bank rail integrations
6. Supply chain (dependencies, build pipeline)

## Key Mitigations
- Hardware-backed admin authentication (HC-009)
- Custody plane isolation (HC-006)
- Zero-trust network segmentation
- Maker-checker for privileged operations
- Immutable audit logging (HC-015)
- Real-time sanctions screening
- Supply-chain controls (SBOM, artifact signing)

## Detailed Threat Analysis
To be completed by security_architect in SEC-001.
