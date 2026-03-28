# Developer Onboarding Guide

## Welcome to Herald Crypto

This guide helps new developers get up to speed with the Herald Crypto Exchange codebase and development workflow.

## Repository Structure

```
herald-crypto/
  agents/           # 27 agent definitions with system prompts
  phases/           # 7 execution phases with 60 task definitions
  reviews/          # 6 review prompt templates
  src/
    core/           # Core domain models
      domain/       # Value objects, entities, aggregates
      events/       # Domain events
      ledger/       # Double-entry ledger
      matching/     # Order book, matching engine, journal
      risk/         # Risk engine, margin calculations
      clearing/     # Settlement, fees
      custody/      # Wallet management
      fiat/         # Treasury, bank rails
      accounts/     # Account hierarchy
      assets/       # Instrument catalog
    services/       # Application services
    api/            # REST, WebSocket, FIX endpoints
    infrastructure/ # Messaging, persistence, cache, observability
  tests/            # Unit, integration, e2e, performance tests
  docs/             # ADRs, architecture, runbooks, onboarding
  scripts/          # Build, deploy, utility scripts
```

## Key Concepts

### Hard Constraints
There are 15 hard constraints (HC-001 through HC-015) that MUST be respected in all code. See `global_context.yaml` for the full list.

### Multi-Agent Architecture
Development is organized around 27 specialized agents across 7 phases. Each agent has a defined scope and responsibilities. See `agents/` for details.

### Event Sourcing
All state changes are captured as immutable events. The matching engine uses an append-only command journal for deterministic replay.

### Double-Entry Ledger
All economic events produce balanced ledger entries. Balances are always derived from ledger state, never manually set.

## Getting Started
1. Read `global_context.yaml` for project context and constraints
2. Read `agent_execution_protocol.yaml` for execution rules
3. Review the phase you're working on in `phases/`
4. Check the agent system prompt for your assigned tasks in `agents/`
5. Review applicable review templates in `reviews/`
