# Personalizing Claude Code: A Body-Content Guide

> You have agents, commands, rules and skills that work. They encode generic best practices. This guide helps you fill them with **your** knowledge -- the domain context, team decisions, personal taste, and hard-won lessons that turn a generic assistant into a colleague who already knows how you work. Updated April 2026.

---

## Table of Contents

- [How to Use This Guide](#how-to-use-this-guide)
- [Personalizing Rules](#1-personalizing-rules)
- [Personalizing Agents](#2-personalizing-agents)
- [Personalizing Skills](#3-personalizing-skills)
- [Personalizing Commands](#4-personalizing-commands)
- [Cross-Cutting: Your Personal Layer](#5-cross-cutting-your-personal-layer)
- [Sources](#sources)

---

## How to Use This Guide

Each section follows the same structure:

1. **What the body is for** -- the role this content plays.
2. **What's already standard** -- what generic templates give you.
3. **The personalization gap** -- what they're missing.
4. **Self-assessment questions** -- exhaustive questions to ask yourself, grouped by theme. Answer them, and you have the raw material for your personalized content.
5. **Before/After examples** -- how answers translate into concrete body content.

**The process:** Pick a type. Read the questions. Answer the ones that feel relevant. Edit the body. The questions you skip are the ones that don't matter for your context -- that's fine.

---

## 1. Personalizing Rules

### What the body is for

A rule's body is **declarative instructions** loaded into Claude's context. It tells Claude how things are done here -- not how they're done in general, but how **your team** does them. Rules apply passively: Claude reads them at session start and follows them when relevant.

### What's already standard

Generic rules describe universal conventions:
- "Use RSpec with FactoryBot"
- "Keep models thin"
- "Return Result objects from services"

### The personalization gap

Standard rules describe what Claude already knows from training. The value of a personalized rule is encoding **decisions Claude can't infer from the code**: your "why", your overrides to convention, your scars from past incidents.

### Self-Assessment Questions

#### Domain & Business Context

- What is this product, in one sentence? (e.g., "B2B marketplace for industrial parts")
- What are the 3-5 core domain concepts and how do they relate? (e.g., "Organization -> User -> Listing -> Order")
- Is there a ubiquitous language the team uses? What terms must Claude get right? (e.g., "We say 'tenant', never 'account'. A 'listing' is not a 'product'.")
- Are there domain invariants that must never be violated? (e.g., "An Order can never exist without a parent Organization. Prices are always in cents, never floats.")
- Are there regulated or compliance-sensitive areas of the codebase? (e.g., "Anything in `app/services/billing/` touches PCI data -- never log params.")

#### Codebase Conventions That Diverge from Defaults

- Do you use UUIDs, integer IDs, or something else as primary keys?
- Do you use soft deletes? Which gem? (Discard, Paranoia, custom?)
- Do you have a tenancy strategy? (ActsAsTenant, manual scoping, database-level?)
- What's your enum convention? (Hash with integers? Array? String values?)
- What's your `dependent:` strategy on associations? `:destroy` vs `:delete_all` vs `:nullify`?
- Do you have a base class hierarchy? (ApplicationService, ApplicationQuery, etc.)
- Do you use STI anywhere? Where, and what are the rules for when to use it vs. polymorphism?
- Do you have custom linter rules (RuboCop overrides) that Claude should know about?

#### Testing Conventions Beyond "Use RSpec"

- What's your test data strategy? (FactoryBot only? Fixtures? Seeds?)
- Do you prefer `build` or `create` by default? When do you use each?
- Do you use `let` or explicit setup inside each test?
- How do you handle time-dependent tests? (`freeze_time`? `travel_to`?)
- Do you use database cleaner? Which strategy? (transaction, truncation, deletion?)
- What's your shared example convention? How do you name them?
- Do you have test helpers specific to your domain? (e.g., `sign_in_as_admin`, `with_tenant`)
- What does your CI run that local doesn't? (e.g., system specs, performance tests)
- Are there tests that are slow or flaky? Tags to skip locally?

#### Error Handling & Edge Cases

- What's your error handling philosophy? (Result objects? Exceptions? Both?)
- Do you use custom exception classes? What's the hierarchy?
- How do you handle 404s? (raise `ActiveRecord::RecordNotFound`? Custom `NotFoundError`?)
- How do you handle authorization failures? (Pundit rescues? Custom handler?)
- Do you have a standard error JSON format for APIs?

#### Hard-Won Lessons (The Scars)

- What bugs have bitten you before that Claude should watch for? (e.g., "N+1 on the dashboard page cost us 3 days")
- What conventions exist because of a past incident? (e.g., "We always use `freeze_time` because flaky CI wasted a sprint")
- What's something a new developer always gets wrong in the first week?
- Are there parts of the codebase that are fragile or surprising? (e.g., "The `Order#total` method triggers a callback chain -- never call it in a loop")

### Before / After

**Standard rule (testing.md):**
```markdown
# Testing Conventions
- TDD approach: RED -> GREEN -> REFACTOR
- Use FactoryBot: `build` over `create` when persistence isn't needed
- One behavior per `it` block
```

**Personalized rule (testing.md):**
```markdown
# Testing Conventions
- TDD approach: RED -> GREEN -> REFACTOR
- Use FactoryBot: `build` over `create` when persistence isn't needed
- One behavior per `it` block

## Our Specifics
- Always wrap time-dependent tests in `freeze_time { }` (flaky CI burned us for 2 weeks in Jan 2026)
- Use `create_list(:entity, 3)` for collections, never manual loops
- Every request spec must include a `context "when not authenticated"` block
- Use the `with_tenant(organization)` helper for all tests touching tenant-scoped models
- Tag slow system specs with `:slow` -- CI runs them, local `rspec` skips them by default
- Shared examples are named after behaviors: `it_behaves_like "a soft-deletable record"`,
  not after implementations: `it_behaves_like "discardable"`
- We mock external APIs (Stripe, SendGrid) with WebMock. Never VCR -- we've had stale cassette bugs.
```

---

## 2. Personalizing Agents

### What the body is for

An agent's body is a **system prompt** -- it defines who the agent is, how it thinks, what it knows about your codebase, and what output it should produce. The body runs in an isolated context window, so it needs to be self-contained: the agent doesn't see your conversation history.

### What's already standard

Generic agent bodies describe universal patterns:
- "You are an expert in ActiveRecord model design"
- "Create services following SOLID principles"
- Textbook code examples (ApplicationService, Result objects, factory patterns)

### The personalization gap

A generic agent knows Rails. A personalized agent knows **your Rails app**: your base classes, your domain models, your naming conventions, the patterns your team has chosen, and the anti-patterns that have burned you. The personalization gap falls into five categories.

### Self-Assessment Questions

#### A. Role & Persona

- What's the agent's personality? Should it be cautious and ask before acting, or decisive and autonomous?
- Should it explain its reasoning, or just produce output silently?
- When it encounters ambiguity, should it make a judgment call or ask?
- Should it proactively suggest improvements it notices, or stay strictly on task?
- Is there a senior developer on the team whose style this agent should emulate?

#### B. Domain Knowledge

- What does this agent need to know about your business domain that isn't in the code?
- What are the key models and relationships this agent will interact with?
- Are there naming conventions specific to your domain? (e.g., "We call them 'engagements', not 'sessions'")
- Are there domain rules this agent must never violate? (e.g., "Never create an Order without validating inventory")
- What external systems does this agent's code interact with? (Stripe, Twilio, a legacy API?)

#### C. Your Team's Patterns (Not Textbook Patterns)

- Do you have a base class this agent should always inherit from? What does it provide?
- What's the exact method signature convention? (e.g., `self.call(...)` vs `self.perform(...)`)
- What return type convention do you use? (Result objects? Plain values? Tuples?)
- What error handling pattern does your team use? (Result failure? Raise + rescue? Either monad?)
- What's your file organization convention? (e.g., `app/services/entities/create_service.rb` vs `app/services/create_entity.rb`)
- What's your namespace convention? (Module per domain? Flat? Nested only past 3 files?)
- Do you have code generation templates or snippets the agent should match?
- Are there gems that change how this layer works? (e.g., Interactor, Dry-rb, AASM, Pundit)

#### D. Quality Bar & Output Expectations

- What must every output include? (e.g., "Always create the spec alongside the implementation")
- What does "done" look like for this agent? (e.g., "Code passes RuboCop, tests pass, no Brakeman warnings")
- Are there automated checks the agent should run before finishing? (linters, tests, type checks?)
- What's the maximum acceptable file length? (e.g., "Models > 200 lines need splitting")
- Should the agent create the migration too, or leave that to the migration-agent?

#### E. Boundaries & Handoffs

- What should this agent explicitly NOT do? (e.g., "The model-agent should never write business logic")
- When should it hand off to another agent? What are the trigger conditions?
- Are there dangerous operations this agent must never perform? (e.g., "Never drop a column", "Never delete data")
- What files should this agent never modify? (e.g., "Don't touch `config/routes.rb` -- the controller-agent handles that")

#### F. Context About the Actual Codebase

- What existing code should this agent read before creating something new? (e.g., "Always read `app/services/application_service.rb` first")
- Are there existing examples in the codebase this agent should follow? (e.g., "Look at `Entities::CreateService` as the canonical service pattern")
- What directories does this agent operate in? Where does it put its output?
- Are there README files, ADRs, or internal docs this agent should reference?

### Before / After

**Standard agent body (service-agent):**
```markdown
## Your Role

You are an expert in Service Object design for Rails applications.
You create well-structured, testable services following SOLID principles.

## Service Structure

```ruby
class ApplicationService
  def self.call(...) = new(...).call
  # ...generic Result pattern
end
```
```

**Personalized agent body (service-agent):**
```markdown
## Your Role

You are the service layer architect for Acme Marketplace.
You create services that orchestrate business logic between our tenant-scoped models.
You ALWAYS write the RSpec test alongside the service. You NEVER commit without tests passing.

## Our Base Class

Read `app/services/application_service.rb` before creating any service. It provides:
- `self.call(...)` class method
- `success(data)` / `failure(error)` returning a `Result` (Data.define)
- Transaction support via `with_transaction { }`

Do NOT redefine these methods. Just inherit and use them.

## Our Domain Context

This is a multi-tenant B2B marketplace. Key concepts:
- **Organization** is the tenant. ALL queries must be scoped to it.
- **Listing** belongs to Organization (not User). Users manage listings on behalf of their org.
- **Order** transitions: draft -> submitted -> approved -> fulfilled -> closed
- Orders in `submitted` state lock the associated Listing inventory.

## Naming & File Organization

- Namespace by domain: `Orders::SubmitService`, not `SubmitOrderService`
- One service per file. File mirrors class: `app/services/orders/submit_service.rb`
- Constructor takes keyword arguments only: `def initialize(order:, user:)`
- External API calls are always injected: `def initialize(order:, notifier: SlackNotifier)`

## What Goes in a Service vs. Elsewhere

- Service: orchestration, transactions, side effects (emails, jobs, API calls)
- Model: validations, associations, scopes, simple predicates (`published?`)
- Query: complex SELECT logic (joins, aggregations, CTEs)
- Job: anything that takes > 100ms or can retry independently

## Error Handling

- Business logic failures: `return failure("Listing is out of stock")`
- System failures: let the exception propagate (Sentry catches it)
- NEVER rescue `StandardError` or `Exception` in a service
- Wrap multi-model writes in `with_transaction`; re-raise on rollback

## Our Anti-Patterns (Things That Burned Us)

- Don't call `order.save!` inside a `with_transaction` -- use `order.save` and return failure on false
- Don't enqueue jobs inside transactions -- they fire before the commit. Use `after_commit` or enqueue in the success path.
- Don't call services from model callbacks. If you feel the urge, the logic belongs in a higher-level service.

## Canonical Example

Read `app/services/orders/submit_service.rb` for our standard pattern.

## Testing Expectations

- Every service gets `spec/services/domain/service_name_spec.rb`
- Test structure: describe `.call` -> context success/failure for each branch
- Use `instance_double` for injected dependencies
- Assert on `result.success?`, `result.data`, `result.error`
- Run `bundle exec rspec spec/services/` before declaring done
```

---

## 3. Personalizing Skills

### What the body is for

A skill's body is a **task playbook** -- step-by-step instructions for a specific workflow. Unlike rules (passive context) or agents (persistent persona), skills are **episodic**: they activate for one task, execute, and return results. The body should read like a runbook that a smart colleague could follow without asking questions.

### What's already standard

Generic skills describe universal procedures:
- "Run Brakeman and report findings"
- "Analyze code quality against SOLID principles"
- "Create a feature specification"

### The personalization gap

Standard skills tell Claude *what* to do. Personalized skills tell Claude *how your team does it*: which tools you actually use, what your quality bar is, what format you want the output in, and what live context to inject.

### Self-Assessment Questions

#### A. Workflow Definition

- What are the exact steps of this workflow when a human does it today?
- In what order do those steps happen? Are any parallelizable?
- What information does the workflow need upfront? (arguments, file paths, branch names?)
- What decisions does the workflow require? Can you encode them as rules, or must the human decide?
- What's the "happy path"? What are the 2-3 most common failure modes?
- Where does the output go? (stdout, a file, a PR, a Slack message?)

#### B. Tools & Context Injection

- What shell commands does this workflow need to run? (git, curl, psql, docker, custom scripts?)
- What live data should be injected before Claude sees the prompt? (git status, test results, deployment status, API health?)
- Does this workflow need to read specific files to do its job? Which ones?
- Does this workflow need external tools? (GitHub CLI, Sentry CLI, Heroku CLI?)
- Can you replace any human judgment with a shell command? (e.g., "check test status" -> `` !`bundle exec rspec --dry-run 2>&1 | tail -1` ``)

#### C. Output Format & Quality Bar

- What does the ideal output look like? Can you write a concrete example?
- Do you want structured output? (markdown table, JSON, checklist, numbered findings?)
- Should the output include severity levels? Categories? Action items?
- What's the minimum acceptable quality? (e.g., "At least check all OWASP Top 10")
- Who is the audience for this output? (you, your team, a PR reviewer, a non-technical stakeholder?)

#### D. Your Team's Specific Criteria

- What are the 3-5 things this skill should ALWAYS check that are specific to your codebase?
- What are your team's unique quality criteria beyond industry standard? (e.g., "Every controller action must have a Pundit `authorize` call")
- What past mistakes should this skill specifically watch for?
- What's your team's nomenclature for severity/priority? (P0-P3? Critical/High/Medium/Low? Blocking/Non-blocking?)
- Does this workflow have a "definition of done"? What is it?

#### E. Invocation & Guard Rails

- Should this skill run automatically when Claude detects relevance, or only when you type `/name`?
- What should this skill NEVER do? (e.g., "Never modify production configs", "Never auto-commit")
- Are there preconditions that must be true before this skill makes sense? (e.g., "Don't run if there are uncommitted changes")
- Should this skill run in the main conversation (inline) or in an isolated subagent (forked)?
- Does this skill have side effects? (sending emails, creating PRs, deploying?)

#### F. Integration With Your Workflow

- What happens after this skill runs? What's the next step in the workflow?
- Does this skill produce output that feeds into another skill or command?
- Should this skill reference other skills or agents? (e.g., "If you find authorization issues, suggest using the policy-agent")
- How often is this skill used? Daily? Per-PR? Occasionally?

### Before / After

**Standard skill body (security-audit):**
```markdown
# Security Audit

You are an expert in Rails application security.

## Process
1. Run Brakeman
2. Run bundler-audit
3. Manual code review against OWASP Top 10
4. Report findings
```

**Personalized skill body (security-audit):**
```markdown
# Security Audit for Acme Marketplace

You are auditing a multi-tenant B2B marketplace handling payment data.
You NEVER modify code. You NEVER access production credentials.

## Live Context

- Branch: !`git branch --show-current`
- Changed files since main: !`git diff main --name-only 2>/dev/null || echo "(no changes)"`
- Last Brakeman run: !`bin/brakeman --no-pager --format json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d.get(\"warnings\",[]))} warnings, confidence: {[w[\"confidence\"] for w in d.get(\"warnings\",[])]}')" 2>/dev/null || echo "not available"`

## Our Specific Risks (check these FIRST)

1. **Tenant isolation** (P0): Every database query in controllers and services
   MUST be scoped to `current_organization`. Grep for `.all`, `.find(`, `.where(`
   without tenant scope. This is our #1 security risk.
2. **Pundit authorization** (P0): Every controller action must call `authorize`.
   Check for missing `authorize` or `policy_scope`. We've had 2 incidents from this.
3. **Payment data** (P0): Nothing in `app/services/billing/` should log params.
   Check for `Rails.logger` or `puts` in billing code.
4. **Mass assignment** (P1): All `params.permit` calls must be explicit.
   No `.permit!` anywhere. No `params.to_unsafe_h`.

## Standard OWASP Checks (after our specifics)

Run through OWASP Top 10 as usual (injection, auth, XSS, etc.)

## Output Format

For each finding:
```
### [P0|P1|P2|P3] Finding Title
- **File:** path/to/file.rb:123
- **Risk:** What could go wrong
- **Evidence:** The specific code
- **Fix:** Concrete code showing the fix
```

End with: `## Summary: X critical, Y high, Z medium, W low`
If any P0: "BLOCKS DEPLOYMENT -- fix before merge"
```

---

## 4. Personalizing Commands

### What the body is for

A command's body is a **prompt template** -- a reusable instruction that Claude expands when you type `/command-name`. Commands and skills are now unified (skills are the successor), but if you have existing `.claude/commands/` files, they keep working.

### What's already standard

Generic commands describe broad procedures:
- "Create a feature specification"
- "Plan the implementation"
- "Review the spec for completeness"

### The personalization gap

Standard commands describe a generic process. Personalized commands encode **your team's specific workflow**, ask **your specific questions**, use **your terminology**, and produce output in **your format**.

### Self-Assessment Questions

#### A. Workflow Steps

- What are the exact steps a human on your team follows for this task today?
- What questions does a human ask before starting? (These become the command's interview phase)
- What information do you always need upfront? (file path, issue number, branch name?)
- What are the checkpoints where a human would pause and ask "does this look right?"

#### B. Templates & Formats

- Does your team have a template for this output? (PR template, spec format, ADR structure?)
- What sections must the output include? What's optional?
- What metadata does your team expect? (author, date, status, version?)
- Is there an existing document in your repo that shows the ideal format?

#### C. Team-Specific Interview Questions

- What domain-specific questions does this command need to ask? (e.g., "Which tenant model does this affect?")
- Are there decisions that must be made explicitly, not assumed? (e.g., "Should this be behind a feature flag?")
- What constraints does your team care about that a generic command wouldn't ask? (e.g., "Does this touch billing?", "Does this need a data migration?")
- What's the simplest version of this feature? (helps prevent over-engineering)

#### D. Quality Criteria

- What makes a good output for this command, specifically for your team?
- What are common mistakes when doing this task? What should the command warn about?
- Are there prerequisites that must be met before this command makes sense?
- What happens after this command produces its output? (feeds into another command? Goes into a PR? Gets reviewed by a specific person?)

### Before / After

**Standard command body (feature-spec):**
```markdown
# Feature Specification Writer

You are an expert feature specification writer.
Ask questions first, then generate a spec.

## Questions to Ask
- What's the feature name?
- Who are the users?
- What's the acceptance criteria?
```

**Personalized command body (feature-spec):**
```markdown
# Feature Specification Writer for Acme Marketplace

You write feature specs that our team of 6 can implement in 1-2 sprint increments.
We deploy weekly on Thursdays, so scope accordingly.

## Discovery Interview

Ask these questions. Don't skip any -- we learned the hard way.

**Core (always ask):**
1. What user problem does this solve? (not "what feature" -- the PROBLEM)
2. Which tenant type is this for? (Buyer, Seller, or Both?)
3. Which existing models does this touch? Read the schema first.
4. Does this touch billing, payments, or pricing? (If yes: flag for PCI review)
5. Is this behind a feature flag? (Default: yes for anything user-facing)

**Scope (always ask):**
6. What's the smallest version that delivers value? (We ship incrementally)
7. What's explicitly OUT of scope for V1?
8. Does this need a data migration for existing records?

**Integration (ask if relevant):**
9. Does this send emails or notifications?
10. Does this need background processing?
11. Does this affect the API? (We version at /api/v1/)
12. Does this need real-time updates? (Turbo Streams vs polling)

## Output Format

Use our spec template at `docs/templates/feature-spec-template.md`.
Every spec must include:
- Problem statement (not solution)
- User stories in "As a [tenant type], I want..."
- Gherkin scenarios (minimum: happy path + 2 edge cases + 1 error case)
- Affected models and associations (check the schema!)
- PR breakdown: max 3 PRs, each independently deployable
- Out-of-scope section (be explicit)

## Anti-Patterns in Our Specs
- Don't spec UI details (colors, button placement) -- that's the designer's job
- Don't assume new models when an existing one can be extended
- Don't spec "admin can do everything" -- be explicit about each role's permissions
- Don't create a spec for something that's really a bug fix (use /sdd-change:specify instead)
```

---

## 5. Cross-Cutting: Your Personal Layer

Beyond project-level customization, `~/.claude/` holds preferences that apply to every project. These are about **you**, not a codebase.

### Self-Assessment Questions for Personal Preferences

#### Communication Style

- Do you prefer concise answers or detailed explanations?
- Should Claude explain its reasoning, or just show the result?
- Do you want Claude to repeat back your request before acting?
- Should Claude ask clarifying questions, or make reasonable assumptions?
- Do you want summaries after completed tasks?
- When Claude shows code, do you want full files or just the diff?

#### Coding Taste

- Do you prefer early returns or structured conditionals?
- Ternary operators: always, never, or "only for simple assignments"?
- Variable naming: short (`usr`) or descriptive (`authenticated_user`)?
- Do you prefer explicit `return` in Ruby or implicit returns?
- One-liners: elegant or unreadable?
- How do you feel about metaprogramming? (Never? Sparingly? Love it?)

#### Workflow Habits

- What does "ship it" mean to you? (commit only? push? open PR? merge?)
- How do you like PRs? (one big PR? many small ones? squash commits?)
- Do you always want tests written first, or is "fix then test" OK sometimes?
- When you say "clean this up", what does that mean? (refactor? lint? both?)
- Do you have shorthand phrases Claude should learn? (e.g., "LGTM" = approve and merge)

#### Trust & Autonomy

- Should Claude auto-run tests after making changes?
- Should Claude auto-lint after editing files?
- Should Claude auto-commit, or always wait for your explicit "commit"?
- Are you comfortable with Claude running database commands? (`rails db:migrate`?)
- What operations should always ask for confirmation? (anything destructive? push? PR creation?)

### Where These Answers Go

| Answer type | Where to put it |
|:---|:---|
| Communication style | `~/.claude/CLAUDE.md` |
| Coding taste | `~/.claude/rules/preferences.md` |
| Workflow habits | `~/.claude/CLAUDE.md` or personal skills |
| Trust & autonomy | `~/.claude/settings.json` (hooks + permissions) |
| Project-specific personal notes | `CLAUDE.local.md` (gitignored) |

### Example: ~/.claude/CLAUDE.md

```markdown
## How I Work

- Be concise. Lead with the answer.
- Don't repeat back what I said. Don't use "Let me..." preamble.
- When I say "ship it": run tests, lint, commit with a good message, push, open PR.
- When I say "quick fix": skip TDD, just fix the bug and add a regression test.
- Don't add comments, docstrings, or type annotations to code you didn't change.
- Don't suggest improvements beyond what I asked for.

## Coding Taste

- Guard clauses and early returns over nested ifs
- Explicit `return` for early exits, implicit for the last expression
- Descriptive names: `user_authentication_result` over `res`
- String interpolation over concatenation
- I like `then` for one-line conditionals: `return if invalid?`
- Ternaries OK for simple values, not for side effects

## When Unsure

- Make a reasonable assumption and tell me what you assumed
- Don't ask "should I continue?" -- just continue
- If something looks risky, explain why and ask
```
