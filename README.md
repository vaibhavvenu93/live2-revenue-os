# Live2.ai — European Revenue OS (Full Local Platform)

A **runnable, local-first GTM operating system** with 14 connected pages, seven backend-driven agent stages, 87 seeded target accounts, country strategies, partner motions, buyer/signal records, human-approved email drafts, AE tasks, opportunities, experiments, product knowledge and CSV export. **Python standard library only** — no npm or pip dependencies.

## Run on Windows (PowerShell)

1. Extract the ZIP into `C:\Users\<you>\Documents\Live2Full`.
2. In VS Code, open the folder containing `server.py`.
3. In the terminal, run `py server.py`.
4. Open `http://localhost:8765` in Chrome.
5. Keep the terminal open. Save changes to `web/app.js`, `web/styles.css` or `web/index.html`, then refresh the browser with Ctrl+Shift+R.

If port 8765 is occupied, stop the old V2/V3 server with **Ctrl+C** before starting this version. Alternatively run `$env:PORT="8766"; py server.py` and open port 8766.

On macOS/Linux: `python3 server.py`.

## Demonstration journey (no keys required)

1. **European markets** → inspect UK, Netherlands, Germany strategies and competition.
2. **Account intelligence** → select a target, inspect evidence URL, update owner/status and save.
3. **Agent control room** → choose an account → **Run full workflow** → inspect seven recorded agent steps.
4. **Buying signals** → record a public event with a source URL → mark reviewed only after inspection.
5. **Buyer intelligence** → add a real, source-backed contact (do not invent emails).
6. **Outreach studio** → generate draft → edit → approve. **Approval does not send email.**
7. **AE task manager** → create and progress tasks.
8. **Revenue pipeline** → create a $40k opportunity → move through stages → see Won ARR on dashboard.
9. **Agency partnerships**, **Channels & activation**, **Growth experiments**, **Knowledge bank**, **GTM tech stack** → explore and update.
10. CSV export from account, signals, buyer, tasks and pipeline pages.

## Optional real research and agent synthesis

Set credentials in the **terminal that starts the server**:

```powershell
$env:TAVILY_API_KEY="your_key_here"
$env:OPENAI_API_KEY="your_key_here"
py server.py
```

Never place keys in browser JS or commit them to Git. When Tavily is configured, **Run with live research** retrieves public web search results. When OpenAI is also configured, the backend requests structured JSON synthesis constrained to those results. Search snippets and extracted triggers are **unverified** until reviewed. Live research requires network access and provider quotas. The model defaults to `gpt-4o-mini` and can be changed with `OPENAI_MODEL`.

Offline **Run full workflow** still performs a backend execution and saves a structured seven-agent trace, but its reasoning is deterministic, based on stored hypotheses, and not an autonomous LLM run.

## Implementation

- `server.py`: Python HTTP server + REST JSON API, SQLite persistence, research provider and optional LLM adapter, agent orchestration.
- `web/index.html`: application shell.
- `web/styles.css`: responsive styling.
- `web/app.js`: interactive pages, forms, API calls, navigation, approvals, pipeline.
- `data/accounts.json`: seeded research hypotheses, country/segment/use-case/evidence URLs.
- `data/revenue.db`: created on first run; local data persistence.

## Honest scope and security

**Working:** local account edits, signal and contact creation, run history, optional Tavily research, optional OpenAI source-based analysis, draft review, task creation/status, deals, experiment updates, knowledge approval, CSV exports and revenue metrics.

**Not connected:** Apollo, Hunter, HubSpot, Smartlead, mailboxes, inbox reply ingestion, scheduled crawling, verified email discovery, user login, multi-tenant access, production queue workers, cloud hosting, or live deal synchronization. No email is sent; no contact details are fabricated. `integrations` is a capability/status registry, not fake connected apps. Country prioritization and ACVs are hypotheses. The local server binds to `127.0.0.1` and is **not production hardened**.

For a production deployment, add authentication/RBAC, encryption/secrets manager, audit logging, a real task queue, request rate limits, tests, CRM OAuth integration, lawful-basis/opt-out workflow, source verification and robust AI evaluations.
