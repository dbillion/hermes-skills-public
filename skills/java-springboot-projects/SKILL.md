---
name: java-springboot-projects
description: Expert implementation of Java Spring Boot applications across all versions. Leverages DDD for microservice readiness, integrates automated Mermaid visualization, and enforces real-world API research.
---

# Java Spring Boot Architectural Restoration Guide

This skill provides procedural guidance for implementing and restoring Spring Boot applications. It emphasizes "Microservice-Ready" modularization using Domain-Driven Design (DDD) principles and automated visualization.

## Core Architectural Mandates

### 1. DDD & Microservice Readiness
- **Modular Monolith**: Build every project as a self-contained domain module.
- **Bounded Contexts**: Strictly define boundaries between the core domain and supporting contexts (e.g., External APIs, Infrastructure).
- **Aggregate Roots**: Identify a single entry point for every entity cluster to ensure transactional integrity.

### 2. High-Performance Execution (Java 25+)
- **Virtual Threads**: ALWAYS enable via `spring.threads.virtual.enabled=true`.
- **Structured Concurrency**: Use `StructuredTaskScope` for all parallel processing (e.g., simulations, multi-API fetching).

### 3. "The 5 Vital Diagrams" Protocol
Every project MUST include these 5 diagrams in `docs/diagrams/` to be considered "Restored":
1.  **`contextMap.mmd`**: (Strategic) Defines the service boundary and external dependencies.
2.  **`aggregateDiagram.mmd`**: (Tactical) Identifies the Aggregate Root and transactional unit.
3.  **`erDiagram.mmd`**: (Physical) Maps the actual database schema and table connectivity.
4.  **`crcCards.mmd`**: (Logic) Details the Responsibilities and Collaborators of the "Brain" service.
5.  **`eventFlow.mmd`**: (Behavioral) Visualizes how the system reacts to async domain events.

*See [diagram-templates.md](references/diagram-templates.md) for standard Mermaid patterns.*

### 4. Real-World Research Protocol
- **Data Integrity**: Never use "mock" data structures. Use `context7` or `nlm` to find official SDK/API payloads (e.g., Binance, Plaid, HL7).
- **Industry Standards**: Align model fields with real-world counterparts to ensure the portfolio is enterprise-ready.

## Implementation Workflow

### 1. Discovery & Strategic Design
- Research domain patterns using `context7`.
- Create the `contextMap.mmd` and `crcCards.mmd` to define the "Brain" logic.

### 2. Physical & Tactical Design
- Implement Entities and Repositories.
- Create the `erDiagram.mmd` and `aggregateDiagram.mmd`.

### 3. Development & Modernization
- Implement the Service logic using Virtual Threads and Pattern Matching.
- Implement the Controller with Swagger/OpenAPI support.

### 4. Automated Visualization
- Run `node scripts/generate_diagrams.cjs` to convert all `.mmd` files into SVGs.
- Embed the raw `.mmd` blocks in `README.md` for native GitHub rendering.

## Verification
- **Unit Tests**: Pass `./mvnw test` with 80%+ coverage.
- **Microservice Audit**: Verify that the `contextMap` defines a clean boundary for extraction.
- **Thread Check**: Verify `isVirtual() == true` in execution logs.
