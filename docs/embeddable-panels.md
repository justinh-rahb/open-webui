# Embeddable Panels (Experimental)

Embeddable panels let you expose a model as a host-page chat widget.

## Configure a panel

1. Open **Workspace -> Models -> Edit**.
2. Enable **Embeddable Panel**.
3. Save the model.

The panel configuration is stored in `model.meta.embed`.

## Runtime endpoints

- `GET /api/v1/embed/panels/{panel_id}`
- `POST /api/v1/auths/embed/token`
- `POST /api/v1/auths/embed/token/exchange`

## Basic embed

```html
<script src="https://YOUR_OPEN_WEBUI/static/embed/open-webui-chatbot.js"></script>
<script>
	OpenWebUIChatbot.init({
		panelId: 'panel-support',
		apiBaseUrl: 'https://YOUR_OPEN_WEBUI',
		externalToken: 'JWT_FROM_HOST_APP'
	});
</script>
```

## Notes

- Embed-scoped tokens are forced to the panel model server-side.
- Cross-origin usage can be constrained with `allowed_origins` in panel config.
- Enable feature flags with:
  - `ENABLE_EMBED=True`
  - `ENABLE_EMBED_TOKEN_EXCHANGE=True`
