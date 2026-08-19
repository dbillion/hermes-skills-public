# Java 21 & Spring Boot 3 Implementation Guide (Enterprise-Grade)

This skill provides procedural guidance for implementing high-performance, maintainable Spring Boot 3 applications using Java 21 features, MANDATING a design-first approach (HLD/LLD).

## Core Mandate: Design First
**DO NOT write code** until a `DESIGN.md` file (based on `java-springboot-projects/DESIGN_TEMPLATE.md`) is created and approved for the project.
- **HLD**: Requirements, Use Cases, Architecture Overview.
- **LLD**: UML Class Diagrams (Mermaid), Domain Modeling, Inheritance vs. Composition, Design Patterns.
- **The Whys/Hows/Whats**: Detailed testing strategy must be documented.

## Core Architectural Mandates

### 1. High-Performance Concurrency (Project Loom)
- **Virtual Threads**: ALWAYS enable virtual threads for web request handling.
  - `spring.threads.virtual.enabled=true`
- **Thread Pinning Prevention**: Avoid `synchronized` blocks in code that performs blocking I/O. Use `java.util.concurrent.locks.ReentrantLock` instead.

### 2. High-Performance Data Access (JPA/Hibernate)
- **Connection Management**: Use HikariCP; set `hibernate.connection.provider_disables_autocommit=true`.
- **JDBC Batching**: Enable global batching (`batch_size=50`) and statement ordering.
- **Avoid IDENTITY**: Use `SEQUENCE` identifiers to keep batching enabled.
- **DTO Projections**: Use Java **Records** for read-only projections.

### 3. Intermediate/Advanced Security
- **No Security in Basics**: Basic projects must remain simple without security overhead.
- **JWT for Intermediary/Advanced**: Implement stateless JWT-based authentication.
- **Role-Based Access**: Use Spring Security's method-level security or `SecurityFilterChain`.

### 4. Modern Java & Clean Architecture
- **No Lombok**: Use Records for DTOs and standard boilerplate for Entities.
- **Pattern Matching**: Leverage Java 21's exhaustive `switch` expressions.
- **Layered Architecture**: Strict separation between Controller, Service, and Repository.

## Technical Stack Standards

| Category | Recommended Technology |
| :--- | :--- |
| **Framework** | Spring Boot 3.4+ |
| **Language** | Java 21 (LTS) |
| **Security** | Spring Security + JJWT |
| **Testing** | JUnit 5 + Testcontainers |
| **Monitoring** | Spring Boot Actuator |

## Verification Checklist
- [ ] `DESIGN.md` created and approved?
- [ ] Virtual threads enabled?
- [ ] JDBC batching enabled?
- [ ] No Lombok used (Records for DTOs)?
- [ ] Positive and negative tests documented (Whys/Hows/Whats)?
- [ ] `CLAUDE.md` updated?
