(function () {
	if (window.OpenWebUIChatbot) return;

	function resolveApiBaseUrl(apiBaseUrl) {
		if (apiBaseUrl) return apiBaseUrl.replace(/\/$/, '');
		return window.location.origin.replace(/\/$/, '');
	}

	async function getEmbedToken(config, apiBaseUrl) {
		if (config.openWebUIToken) {
			return config.openWebUIToken;
		}

		if (!config.externalToken) {
			throw new Error('Missing externalToken or openWebUIToken.');
		}

		var exchangePath = config.exchangePath || '/api/v1/auths/embed/token/exchange';
		var response = await fetch(resolveApiBaseUrl(apiBaseUrl) + exchangePath, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				panel_id: config.panelId,
				token: config.externalToken
			})
		});

		if (!response.ok) {
			throw new Error('Failed to exchange embed token.');
		}

		var json = await response.json();
		if (!json || !json.token) {
			throw new Error('Token exchange did not return an Open WebUI token.');
		}

		return json.token;
	}

	function createWidgetElements(config, apiBaseUrl) {
		var container = document.createElement('div');
		container.style.position = 'fixed';
		container.style.right = '20px';
		container.style.bottom = '20px';
		container.style.zIndex = '2147483000';
		container.style.display = 'flex';
		container.style.flexDirection = 'column';
		container.style.alignItems = 'flex-end';
		container.style.gap = '12px';

		var iframe = document.createElement('iframe');
		iframe.src = resolveApiBaseUrl(apiBaseUrl) + '/embed/' + encodeURIComponent(config.panelId);
		iframe.title = config.title || 'Open WebUI Chat';
		iframe.style.width = (config.width || 380) + 'px';
		iframe.style.height = (config.height || 620) + 'px';
		iframe.style.border = '0';
		iframe.style.borderRadius = '16px';
		iframe.style.boxShadow = '0 16px 48px rgba(0,0,0,0.25)';
		iframe.style.background = '#fff';
		iframe.style.display = 'none';
		iframe.setAttribute('allow', 'clipboard-read; clipboard-write');

		var button = document.createElement('button');
		button.type = 'button';
		button.textContent = config.buttonText || 'Chat';
		button.style.border = '0';
		button.style.borderRadius = '999px';
		button.style.padding = '12px 16px';
		button.style.background = '#111827';
		button.style.color = '#fff';
		button.style.fontFamily = 'ui-sans-serif, system-ui, sans-serif';
		button.style.fontSize = '14px';
		button.style.cursor = 'pointer';
		button.style.boxShadow = '0 6px 20px rgba(0,0,0,0.18)';

		var opened = false;
		button.addEventListener('click', function () {
			opened = !opened;
			iframe.style.display = opened ? 'block' : 'none';
		});

		container.appendChild(iframe);
		container.appendChild(button);
		document.body.appendChild(container);

		return { container: container, iframe: iframe };
	}

	window.OpenWebUIChatbot = {
		init: async function (config) {
			if (!config || !config.panelId) {
				throw new Error('OpenWebUIChatbot.init requires panelId.');
			}

			var apiBaseUrl = resolveApiBaseUrl(config.apiBaseUrl);
			var elements = createWidgetElements(config, apiBaseUrl);
			var token = await getEmbedToken(config, apiBaseUrl);

			var iframe = elements.iframe;
			iframe.addEventListener('load', function () {
				iframe.contentWindow.postMessage(
					{
						type: 'openwebui:embed:auth',
						token: token,
						panelId: config.panelId,
						apiBaseUrl: apiBaseUrl
					},
					apiBaseUrl
				);
			});
		}
	};
})();
