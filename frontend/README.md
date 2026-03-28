# Frontend Multi-Agent Prompt Pack

## Overview
This directory contains the frontend multi-agent system for the Herald Crypto exchange.
It extends the backend pack (27 agents) with 25 frontend agents covering mobile, web, and desktop surfaces.

## Contents

### Agents (25)
Located in `agents/` - each agent has a `system_prompt.md` defining:
- Identity (ID, title, mission)
- Inputs and outputs
- Dependencies on other agents
- Responsibilities
- Key principles

| ID | Agent | Surface Focus |
|----|-------|---------------|
| FE-00 | Frontend Orchestrator | All |
| FE-01 | Competitive Benchmark Translator | All |
| FE-02 | IA & Navigation Lead | All |
| FE-03 | Design System Lead | All |
| FE-04 | Realtime Data & State Lead | All |
| FE-05 | Mobile Shell Lead | Mobile |
| FE-06 | Mobile Trading Lead | Mobile |
| FE-07 | Mobile Wealth & Social Lead | Mobile |
| FE-08 | Web Trader Lead | Web |
| FE-09 | Web Wealth & Social Lead | Web |
| FE-10 | Desktop Shell Lead | Desktop |
| FE-11 | Charting & Market Data UI Lead | All |
| FE-12 | Order Entry & Execution UX Lead | All |
| FE-13 | Portfolio, Wallet & Transfer Lead | All |
| FE-14 | Options & Multi-Leg Lead | All |
| FE-15 | Security & Identity UX Lead | All |
| FE-16 | KYC, Region Gating & Compliance UX Lead | All |
| FE-17 | Notifications & Alerts Lead | All |
| FE-18 | Localization & Accessibility Lead | All |
| FE-19 | Performance & Reliability Lead | All |
| FE-20 | QA Automation Lead | All |
| FE-21 | Analytics & Experimentation Lead | All |
| FE-22 | Support, Help & Comms Lead | All |
| FE-23 | BFF / API Contract Liaison | All |
| FE-24 | Release & Rollout Lead | All |

### Implementation Prompts (37)
Located in `prompts/` - task prompts organized by phase:
- **FEP-000**: Cross-surface foundation prompts
- **FEP-1xx**: Mobile surface prompts
- **FEP-2xx**: Web surface prompts
- **FEP-3xx**: Desktop surface prompts
- **FEP-4xx**: Cross-cutting shared component prompts

### Review Templates (4)
Located in `reviews/` - quality gates for frontend work:
- **FER-001**: Design System & Accessibility Review
- **FER-002**: Performance & Reliability Review
- **FER-003**: Security & Compliance UX Review
- **FER-004**: Cross-Surface Parity Review

### Supporting Files
- `frontend_context.yaml` - Shared context, guardrails, and surface blueprints
- `phases/release_phases.md` - 5 release phases (MVP through GA-2)
- `MASTER_PROMPT.txt` - Master orchestration prompt for the frontend CTO

### Feature Parity Matrix
Located at `../docs/feature_parity_matrix.csv` - 68 rows mapping features to:
- Target surfaces (iOS, Android, Web, Desktop)
- Release phases (MVP, Beta, GA-1, GA-2)
- Priority and competitive benchmarks

## Architecture
- **Monorepo**: TypeScript with shared packages
- **Mobile**: React Native with native modules
- **Web**: React + TypeScript SPA
- **Desktop**: Tauri/Electron shell around web pro trader
- **Data**: WebSocket-first real-time, snapshot+diff market data
