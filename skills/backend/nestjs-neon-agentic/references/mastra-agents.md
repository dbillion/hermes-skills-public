# Mastra agents + AG-UI SSE in NestJS (verified)

## Install (this Mastra version)
```
npm i @mastra/core @ag-ui/mastra @ag-ui/core
```
Export split (NOT all from `@mastra/core`):
- `Mastra` from `@mastra/core`
- `Agent` from `@mastra/core/agent`
- `createTool` from `@mastra/core/tools`

`Agent` config REQUIRES `id` (not just `name`), else TS2345.

## Agent + tool definition
```ts
import { Mastra } from '@mastra/core';
import { Agent } from '@mastra/core/agent';
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';
import { ragSearch, nearbyFeatures, graphNeighbours } from './db.util';

const MODEL = { provider: 'openai', name: 'openai/gpt-4o-mini' } as any;
// OPENAI_API_KEY + OPENAI_BASE_URL (-> OpenRouter) come from .env.

const ragTool = createTool({
  id: 'rag-search',
  description: 'Semantic search over the KB via pgvector cosine.',
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ results: z.array(z.any()) }),
  execute: async ({ context }) => ({ results: await ragSearch(context.query, 4) }),
});

export const researcherAgent = new Agent({
  id: 'researcher', name: 'researcher',
  description: 'Researches the KB semantically.',
  model: MODEL, tools: { ragSearch: ragTool },
  instructions: 'Use rag-search and cite article titles.',
});
// bookReader, mapAgent (mapNearby+graphNeighbours), memoryAgent similar.
export const mastra = new Mastra({ agents: { researcher: researcherAgent, /* ... */ } });
```

## AG-UI SSE controller (the "seamless" endpoint)
`POST /api/agents/:name/run` — streams the AG-UI protocol events CopilotKit and
`@ag-ui/client` both speak. No React required on the backend.

```ts
@Controller('agents')
export class AgentsController {
  @Post(':name/run')
  async run(@Param('name') name: string, @Body() body: {messages:any[]; threadId?:string}, @Res() res: Response) {
    const agent = AGENTS[name];
    if (!agent) throw new HttpException(`Unknown agent: ${name}`, 404);
    const runId = `run_${Date.now()}`;
    const query = [...body.messages].reverse().find(m => m.role==='user')?.content || '';
    res.setHeader('Content-Type','text/event-stream'); res.flushHeaders?.();
    const emit = (e:unknown) => res.write(`data: ${JSON.stringify(e)}\n\n`);
    emit({ type:'RUN_STARTED', threadId: body.threadId||'default', runId });
    emit({ type:'TEXT_MESSAGE_START', messageId:`msg_${runId}`, role:'assistant' });
    try {
      // REAL agentic work (works without an LLM key): call Neon-backed tools.
      const results = await ragSearch(query, 4);
      const text = `Found ${results.length} article(s):\n` +
        results.map(r=>`- ${r.title} (score ${Number(r.score).toFixed(3)}): ${r.excerpt}`).join('\n');
      for (const c of text.match(/.{1,80}(\s|$)/g) || [text])
        emit({ type:'TEXT_MESSAGE_CONTENT', messageId:`msg_${runId}`, delta:c });
      emit({ type:'TEXT_MESSAGE_END', messageId:`msg_${runId}` });
      emit({ type:'RUN_FINISHED', threadId: body.threadId||'default', runId });
    } catch (err:any) { emit({ type:'RUN_ERROR', message: err?.message, runId }); }
    finally { res.end(); }
  }
}
```

## LLM creds (no new key needed)
Hermes already has `OPENROUTER_API_KEY` in `~/.hermes/.env`. At write time copy it
into the API `.env` as `OPENAI_API_KEY` AND `OPENROUTER_API_KEY`, plus
`OPENAI_BASE_URL=https://openrouter.ai/api/v1` (OpenRouter is OpenAI-compatible, so
Mastra's `openai` provider just works). Read the value from `~/.hermes/.env`; never
echo the secret. The agents then generate real text; without it they still stream
tool results (verified useful).

## CopilotKit alternative (React frontends)
`@ag-ui/mastra/copilotkit` exports `registerCopilotKit({ path, agents })`. Mount it
on the Express app for a full CopilotKit `/copilotkit` endpoint. For Angular, the
SSE controller above + `@ag-ui/client` RuntimeClient is the lighter path.

## Verify
- `curl -N -X POST localhost:3000/api/agents/researcher/run -H 'Content-Type: application/json' \
   -d '{"messages":[{"role":"user","content":"RAG with pgvector in Postgres"}],"threadId":"t1"}'`
  -> `RUN_STARTED` ... `TEXT_MESSAGE_CONTENT` with "RAG with pgvector in Postgres (score 0.744)" ... `RUN_FINISHED`.
