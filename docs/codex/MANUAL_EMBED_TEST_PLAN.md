# Manual Embed Test Plan

Date: 2026-02-20
Branch: `codex/artifacts-embed`

## 1. Prerequisites

- Open WebUI running from this branch.
- Feature flags set:
  - `ENABLE_EMBED=true`
  - `ENABLE_EMBED_TOKEN_EXCHANGE=true`
  - `EMBED_JWT_SECRET=<shared-secret>`
- A model with **Embeddable Panel** enabled in Workspace -> Models.
- Panel ID from model config (example: `panel-support`).

## 2. Verify Panel API

```bash
curl -sS \
  "http://localhost:8080/api/v1/embed/panels/panel-support" | jq
```

Expected:
- `id` matches panel id
- `model_id` present
- `auth_mode`, `allow_anonymous`, `allowed_origins` present

## 3. Generate External JWT (HS256)

Use same secret as `EMBED_JWT_SECRET`.

```bash
python3 - <<'PY'
import jwt, time
secret = "replace-with-embed-jwt-secret"
payload = {
  "email": "admin@localhost",
  "iat": int(time.time()),
  "exp": int(time.time()) + 3600,
}
print(jwt.encode(payload, secret, algorithm="HS256"))
PY
```

Copy output token as `EXTERNAL_JWT`.

## 4. Exchange External JWT for Open WebUI Scoped Token

```bash
curl -sS -X POST \
  "http://localhost:8080/api/v1/auths/embed/token/exchange" \
  -H "Content-Type: application/json" \
  -d '{
    "panel_id": "panel-support",
    "token": "'"$EXTERNAL_JWT"'"
  }' | jq
```

Expected:
- `token` present in response
- decoded token contains `embed_scope.panel_id` and `embed_scope.model_id`

## 5. Call Chat Completions with Scoped Token

```bash
OWUI_TOKEN="<token from previous step>"

curl -sS -X POST \
  "http://localhost:8080/api/v1/chat/completions" \
  -H "Authorization: Bearer $OWUI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "replace-with-panel-model-id",
    "stream": false,
    "messages": [
      {"role":"user","content":"Reply in one short sentence."}
    ]
  }' | jq
```

Expected:
- `choices[0].message.content` returned.

## 6. Negative Checks

### 6.1 Model Override Rejected

```bash
curl -sS -X POST \
  "http://localhost:8080/api/v1/chat/completions" \
  -H "Authorization: Bearer $OWUI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "some-other-model",
    "stream": false,
    "messages": [{"role":"user","content":"test"}]
  }' | jq
```

Expected:
- 403 with model override rejection.

### 6.2 Direct Model Rejected

```bash
curl -sS -X POST \
  "http://localhost:8080/api/v1/chat/completions" \
  -H "Authorization: Bearer $OWUI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "replace-with-panel-model-id",
    "model_item": {"direct": true},
    "stream": false,
    "messages": [{"role":"user","content":"test"}]
  }' | jq
```

Expected:
- 403 with direct model restriction.

## 7. Runtime Route Manual Check

Open:

- `http://localhost:8080/embed/panel-support`

Expected:
- Page loads without forced auth redirect.
- Shows “Waiting for authentication...” before token handshake.

## 8. Widget Script Manual Check

Create a local HTML page with:

```html
<script src="http://localhost:8080/static/embed/open-webui-chatbot.js"></script>
<script>
  OpenWebUIChatbot.init({
    panelId: "panel-support",
    apiBaseUrl: "http://localhost:8080",
    externalToken: "<EXTERNAL_JWT>"
  });
</script>
```

Expected:
- Floating chat button appears.
- Clicking opens iframe chat.
- Sending message returns response.
