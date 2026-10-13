# Mastra + AG-UI + CopilotKit — seamless agent UX (condensed from Context7 /mastra-ai/mastra)

## The problem
Wiring multiple agents (researcher, book-reader, map, memory/RAG) into a frontend chat usually means
hand-rolling websockets, streaming, tool UIs, and human-in-the-loop — brittle and slow.

## The verified pattern (one protocol, three pieces)
1. **Mastra** (agent runtime, server-side, Node/TS): define agents with tools + memory.
   ```ts
   import { Agent } from '@mastra/core';
   export const researcher = new Agent({
     name: 'Researcher',
     instructions: '...',
     tools: { /* web search, ... */ },
     memory: /* memory config */
   });
   ```
2. **`@ag-ui/mastra/copilotkit`** adapter: exposes Mastra agents as an AG-UI (Agent-User Interaction)
   HTTP/SSE endpoint. This is the seam that makes any frontend "just work".
   ```ts
   import { CopilotRuntime, copilotRuntimeNodeHttpEndpoint } from '@mastra/copilotkit';
   // mount at /api/copilotkit
   ```
   AG-UI is a transport-agnostic protocol: the agent emits typed events (text, tool call, tool result,
   state, generative UI) the client renders.
3. **Frontend**:
   - React: `@copilotkit/react-core` (`<CopilotKit runtimeUrl="/api/copilotkit" agent="researcher">`)
     + `@copilotkit/react-ui` (`<CopilotChat>`). Gives streaming chat, generative UI (A2UI), HITL, for free.
   - **Angular (this repo)**: CopilotKit's polished components are React-only. Consume the SAME AG-UI
     endpoint with `@ag-ui/client` `RuntimeClient` over HTTP/SSE and render events in a custom Angular
     chat component. You get streaming + generative UI without mounting React.

## Why it's "seamless and good"
- One endpoint (`/api/copilotkit`) serves all agents; frontend picks the `agent` name.
- Streaming, tool-call visibility, and human-in-the-loop are protocol features, not custom code.
- Mastra memory + pgvector (Neon) = agents that retain context; graph (Neon) = relational memory.
- Swap/model-agnostic: change the model in Mastra, frontend unchanged.

## Wiring to the Neon backend in this repo
- Researcher / BookReader: call the NestJS service layer (or external tools).
- MapAgent: queries PostGIS via the map/graph services (ST_AsGeoJSON etc.).
- MemoryAgent (RAG): pgvector cosine `<=>` over `articles.embedding`; history persisted in `agent_history`.
- Expose all via the CopilotKit/AG-UI endpoint; Angular consumes via `@ag-ui/client`.

## Concrete Mastra install (this session, NestJS 11 + @mastra/core)
- `npm i @mastra/core @ag-ui/mastra @ag-ui/core` — installs clean, `nest build` stays green.
- IMPORT PATHS in this Mastra version (do NOT import `Agent`/`createTool` from `@mastra/core` root):
  - `Mastra` -> `import { Mastra } from '@mastra/core'`
  - `Agent`  -> `import { Agent } from '@mastra/core/agent'`
  - `createTool` -> `import { createTool } from '@mastra/core/tools'`
- `Agent` config REQUIRES an `id` field (not just `name`) or TS errors `Property 'id' is missing`.
- Model field form for OpenRouter: `{ provider: 'openai', name: 'openai/gpt-4o-mini' }` (bare
  `gpt-4o-mini` is wrong; OpenRouter model ids are prefixed).
- Reuse Hermes' provider key for real LLM calls (don't ask the user for a new key):
  - Keys live in `~/.hermes/.env` (NOT config.yaml). Present: `OPENROUTER_API_KEY`, `GOOGLE_API_KEY`,
    `NVIDIA_API_KEY`, `HF_TOKEN`, `EXA_API_KEY`, `FIRECRAWL_API_KEY`, `TAVILY_API_KEY`.
  - OpenRouter is OpenAI-compatible. Pull into the API `.env` WITHOUT echoing secrets:
    `K=$(grep -E '^OPENROUTER_API_KEY=' ~/.hermes/.env | head -1 | cut -d= -f2-); printf 'OPENROUTER_API_KEY=%s\nOPENAI_API_KEY=%s\nOPENAI_BASE_URL=https://openrouter.ai/api/v1\n' "$K" "$K" >> path/to/.env`
  - API `.env` MUST be gitignored. App MUST `import 'dotenv/config'` before building config or
    `process.env` reads return undefined. Verify by making a real model call, not by asserting the var.

## Custom AG-UI SSE controller (verifiable, framework-agnostic alternative)
Instead of the CopilotKit React handler (`copilotRuntimeNodeHttpEndpoint` expects an Express adapter
that needs extra wiring inside NestJS), a NestJS `@Controller('agents')` can stream AG-UI events over
plain SSE — same protocol CopilotKit speaks, so Angular's `@ag-ui/client` `RuntimeClient` consumes it
unchanged. Verified working this session:
```ts
@Post(':name/run')
async run(@Param('name') name, @Body() body, @Res() res: Response) {
  res.setHeader('Content-Type', 'text/event-stream'); res.flushHeaders?.();
  const emit = (e:unknown) => res.write(`data: ${JSON.stringify(e)}\n\n`);
  emit({ type:'RUN_STARTED', threadId: body.threadId||'default', runId });
  emit({ type:'TEXT_MESSAGE_START', messageId:`msg_${runId}`, role:'assistant' });
  // ... REAL agentic work (ragSearch / nearbyFeatures / graphNeighbours) ...
  // stream text in deltas:
  emit({ type:'TEXT_MESSAGE_CONTENT', messageId:`msg_${runId}`, delta: chunk });
  emit({ type:'TEXT_MESSAGE_END', messageId:`msg_${runId}` });
  emit({ type:'RUN_FINISHED', threadId: body.threadId||'default', runId });
  res.end();
}
```
Curl test: `curl -sN -X POST localhost:3000/api/agents/researcher/run -H 'Content-Type: application/json'
-d '{"messages":[{"role":"user","content":"..."}],"threadId":"t1"}'` -> prints RUN_STARTED,
TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT..., TEXT_MESSAGE_END, RUN_FINISHED. This proves the endpoint
end-to-end WITHOUT needing an LLM key (tool results stream regardless).

## OPEN PITFALL (unresolved at skill-write time — investigate, do not assume fixed)
- `articles.embedding <=> $1::vector` returned 0 rows even though all 6 seed rows have valid
  1536-dim `vector` values (confirmed via `vector_dims(embedding)=1536` and non-null count). A
  self-vs-self distance query (`a.embedding <=> b.embedding WHERE b.title='X'`) also returned `[]`,
  which is impossible if the `<=>` operator is live — suggesting the pgvector operator class or the
  `vector` extension is not actually functional in the query path (extension listed in `pg_extension`
  but operator may not resolve, or the column is stored as `text`/wrong type despite `vector(1536)`
  DDL). BEFORE trusting RAG: re-run `SELECT '[1,2,3]'::vector <=> '[1,2,3]'::vector` via the MCP — if
  that errors or returns empty, the extension/operator is broken and RAG must not be claimed working.
  Also confirm the column type is `vector` (not `text`) via `information_schema`.
