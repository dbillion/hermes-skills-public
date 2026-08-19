# Mermaid Architectural Templates for Java Spring Boot

Use these templates to ensure consistent, microservice-ready documentation across all 67 projects.

## 1. Bounded Context Map (`contextMap.mmd`)
**Purpose**: Defines service boundaries and external communication.
```mermaid
graph LR
    subgraph "Core Domain"
        PrimaryContext[Primary Domain Context]
    end
    
    subgraph "Supporting Domains"
        SecondaryContext[External API / Mock Context]
    end
    
    PrimaryContext -- "Uses (Upstream)" --> SecondaryContext
    SecondaryContext -- "Replies (Downstream)" --> PrimaryContext
```

## 2. Aggregate Root Diagram (`aggregateDiagram.mmd`)
**Purpose**: Defines transactional boundaries and entity ownership.
```mermaid
classDiagram
    class AggregateRoot {
        <<Aggregate Root>>
        +Long id
        +process()
    }
    class ValueObject {
        <<Value Object>>
        +String data
    }
    class Entity {
        <<Entity>>
        +Long id
    }
    
    AggregateRoot "1" *-- "many" Entity : owns
    AggregateRoot "1" o-- "1" ValueObject : contains
```

## 3. Physical ER Diagram (`erDiagram.mmd`)
**Purpose**: Shows physical table connectivity and database schema.
```mermaid
erDiagram
    USERS ||--o{ CHAT_SESSIONS : "owns"
    CHAT_SESSIONS ||--o{ CHAT_MESSAGES : "contains"
    
    USERS {
        long id PK
        string username
        string email
    }
    CHAT_SESSIONS {
        uuid id PK
        long user_id FK
        datetime created_at
    }
```

## 4. CRC Cards (`crcCards.mmd`)
**Purpose**: Defines Responsibilities and Collaborators for core "Brain" logic.
```mermaid
classDiagram
    class BrainService {
        <<CRC Card>>
        Responsibilities:
        - Logic A
        - Logic B
        Collaborators:
        - ExternalService
        - Repository
    }
```

## 5. Domain Event Flow (`eventFlow.mmd`)
**Purpose**: Visualizes async scaling and reactive state changes.
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : DomainEventReceived
    Processing --> Completed : TaskFinished
    Processing --> Failed : ErrorOccurred
    Completed --> [*]
```
