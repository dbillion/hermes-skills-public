# Effective Java — 12-Week Study Plan

---

## Overview
This plan covers all 90 items from *Effective Java* (3rd Edition) over 12 weeks.

**Time commitment:** ~5-7 hours per week  
**Prerequisites:** Comfortable with Java basics (classes, interfaces, inheritance)

---

## Phase 1: Foundations (Weeks 1–3)

### Week 1: Object Creation (Items 1–9)
- Read Chapter 2 guide
- Run `BuilderPattern.java`, `SingletonPattern.java`, `DependencyInjection.java`, `TryWithResources.java`
- **Exercise:** Refactor a class with many constructor parameters to use Builder pattern
- **Exercise:** Convert a singleton to use enum pattern

### Week 2: Core Methods (Items 10–14)
- Read Chapter 3 guide
- Run `EqualsAndHashCode.java`
- **Exercise:** Implement `equals`, `hashCode`, `toString`, `compareTo` for a value class
- **Exercise:** Write unit tests for `equals` contract (reflexive, symmetric, transitive)

### Week 3: Class Design (Items 15–25)
- Read Chapter 4 guide
- Run `CompositionOverInheritance.java`
- **Exercise:** Refactor an inheritance hierarchy to use composition
- **Exercise:** Create an immutable value class with defensive copies

---

## Phase 2: Advanced Types (Weeks 4–6)

### Week 4: Generics (Items 26–33)
- Read Chapter 5 guide
- Review `PECS.md` cheatsheet
- **Exercise:** Write a generic `Stack` class with `pushAll` and `popAll` using PECS
- **Exercise:** Create a typesafe heterogeneous container (Favorites pattern)

### Week 5: Enums and Annotations (Items 34–41)
- Read Chapter 6 guide
- Run `PlanetEnum.java`
- **Exercise:** Create an enum with data and behavior (like Planet)
- **Exercise:** Implement the Strategy enum pattern

### Week 6: Lambdas and Streams (Items 42–48)
- Read Chapter 7 guide
- Run `StreamExamples.java`
- **Exercise:** Refactor a loop-based algorithm to use streams
- **Exercise:** Write a stream pipeline that groups, filters, and transforms data

---

## Phase 3: Professional Practices (Weeks 7–12)

### Week 7: Methods (Items 49–56)
- Read Chapter 8 guide
- Run `DefensiveCopy.java`
- **Exercise:** Add parameter validation to all public methods in a class
- **Exercise:** Review a codebase and fix methods that return null instead of empty collections

### Week 8: General Programming (Items 57–68)
- Read Chapter 9 guide
- **Exercise:** Profile a program and optimize string concatenation
- **Exercise:** Replace `float`/`double` monetary calculations with `BigDecimal`

### Week 9: Exceptions (Items 69–77)
- Read Chapter 10 guide
- **Exercise:** Review exception handling in a project; fix anti-patterns
- **Exercise:** Add proper exception documentation to all public APIs

### Week 10: Concurrency (Items 78–84)
- Read Chapter 11 guide
- Run `ConcurrencyExamples.java`
- **Exercise:** Convert a thread-based program to use `ExecutorService`
- **Exercise:** Replace `synchronized` collections with `ConcurrentHashMap`

### Week 11: Serialization (Items 85–90)
- Read Chapter 12 guide
- **Exercise:** Replace Java serialization with JSON (Jackson) in a project
- **Exercise:** Implement the serialization proxy pattern

### Week 12: Review and Application
- Review all 3 cheatsheets
- **Final Project:** Code review a real project applying all 90 items
- **Quiz yourself:** Can you explain each item without looking at notes?
- **Teach someone:** Explain your top 10 items to a peer

---

## Daily Habits

- **Monday:** Read one chapter guide (30 min)
- **Tuesday:** Run code examples (30 min)
- **Wednesday:** Apply one item to your current project (1 hour)
- **Thursday:** Review cheatsheet (15 min)
- **Friday:** Write notes or blog post about what you learned (30 min)
- **Weekend:** Work on exercises or final project (2-3 hours)

---

## Progress Tracker

| Week | Items | Completed | Notes |
|------|-------|-----------|-------|
| 1 | 1–9 | ☐ | |
| 2 | 10–14 | ☐ | |
| 3 | 15–25 | ☐ | |
| 4 | 26–33 | ☐ | |
| 5 | 34–41 | ☐ | |
| 6 | 42–48 | ☐ | |
| 7 | 49–56 | ☐ | |
| 8 | 57–68 | ☐ | |
| 9 | 69–77 | ☐ | |
| 10 | 78–84 | ☐ | |
| 11 | 85–90 | ☐ | |
| 12 | Review | ☐ | |

---

## Assessment Questions

After completing the plan, you should be able to answer:

1. Why is the Builder pattern better than telescoping constructors?
2. What's the contract for `equals` and `hashCode`?
3. When should you use composition over inheritance?
4. What does PECS stand for and when do you use each wildcard?
5. Why are enums better than `int` constants?
6. When should you use parallel streams?
7. What's failure atomicity and how do you achieve it?
8. What's the difference between checked and unchecked exceptions?
9. Why should you avoid Java serialization?
10. What's the serialization proxy pattern?
