# Embed Workstream Handoff

Date: 2026-02-20

## Branch Stack

1. `codex/pr-a-embed-backend`
   - Commit: `11c836bb4`
   - Adds backend embed primitives:
     - `GET /api/v1/embed/panels/{panel_id}`
     - `POST /api/v1/auths/embed/token`
     - `POST /api/v1/auths/embed/token/exchange`
     - Scoped embed token enforcement in `/api/v1/chat/completions`
     - Embed config flags in `env.py` + `PersistentConfig`

2. `codex/pr-b-model-embed-settings`
   - Commit: `b1d51efd0`
   - Adds model editor UI for `model.meta.embed` config + generated snippet copy.

3. `codex/pr-c-embed-runtime`
   - Commit: `677646687`
   - Adds runtime:
     - `static/embed/open-webui-chatbot.js`
     - `src/routes/embed/[panelId]/+page.svelte`
     - Public-route auth bypass in `src/routes/+layout.svelte` for `/embed/*` and `/s/*`
     - Cypress smoke spec for embed route
     - `docs/embeddable-panels.md`

4. `codex/artifacts-embed` (this branch)
   - Handoff/artifacts-only branch for fast session restart.

## Stack Usage

To apply in series on `dev`:

1. Merge `codex/pr-a-embed-backend`
2. Merge `codex/pr-b-model-embed-settings`
3. Merge `codex/pr-c-embed-runtime`

## Key Runtime Config

- `ENABLE_EMBED=True`
- `ENABLE_EMBED_TOKEN_EXCHANGE=True`
- `EMBED_JWT_SECRET=...`
- Optional:
  - `EMBED_JWT_ISSUER`
  - `EMBED_JWT_AUDIENCE`
  - `EMBED_JWT_EMAIL_CLAIM` (default `email`)
  - `EMBED_TOKEN_EXPIRES_IN` (default `1h`)

## Verification Notes

- Python syntax checks completed with `python3 -m py_compile` for changed backend files.
- Could not run full lint/tests in this environment due missing local tooling/deps:
  - `eslint`, `svelte-kit`, `pylint`
  - Python package imports for pytest (e.g., `redis`, `open_webui` in local venv context)

## Known Follow-ups

- Add frontend API wrappers for embed endpoints (`src/lib/apis/auths/index.ts` / dedicated embed API module).
- Expand cypress coverage from route smoke test to full token exchange + message flow.
- Decide whether `/s/*` should remain public-route exempt long-term or use dedicated public layout handling.
