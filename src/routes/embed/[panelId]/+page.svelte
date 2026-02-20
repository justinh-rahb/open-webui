<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	type ChatMessage = {
		role: 'system' | 'user' | 'assistant';
		content: string;
	};

	type EmbedPanel = {
		id: string;
		model_id: string;
		title: string;
		welcome_message?: string | null;
		starter_prompts?: string[];
		auth_mode: string;
		allow_anonymous: boolean;
		allowed_origins: string[];
		ui: Record<string, unknown>;
	};

	let panel: EmbedPanel | null = null;
	let token = '';
	let input = '';
	let loading = false;
	let error = '';
	let messages: ChatMessage[] = [];

	const getApiBaseUrl = () => {
		if (typeof window === 'undefined') return '';
		const apiBaseFromParent = window.sessionStorage.getItem('owui:embed:api-base-url');
		return apiBaseFromParent || window.location.origin;
	};

	const getAuthHeaders = () =>
		token
			? {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				}
			: {
					'Content-Type': 'application/json'
				};

	const loadPanel = async () => {
		const res = await fetch(`${getApiBaseUrl()}/api/v1/embed/panels/${$page.params.panelId}`, {
			headers: token ? { Authorization: `Bearer ${token}` } : undefined
		});

		if (!res.ok) {
			throw new Error('Failed to load embed panel.');
		}

		panel = await res.json();
		if (messages.length === 0 && panel?.welcome_message) {
			messages = [{ role: 'assistant', content: panel.welcome_message }];
		}
	};

	const sendMessage = async () => {
		const content = input.trim();
		if (!content || !panel || !token) return;

		error = '';
		loading = true;

		const requestMessages = [...messages, { role: 'user', content }];
		messages = requestMessages;
		input = '';

		try {
			const res = await fetch(`${getApiBaseUrl()}/api/v1/chat/completions`, {
				method: 'POST',
				headers: getAuthHeaders(),
				body: JSON.stringify({
					model: panel.model_id,
					stream: false,
					messages: requestMessages
				})
			});

			if (!res.ok) {
				throw new Error('Failed to generate completion.');
			}

			const data = await res.json();
			const reply = data?.choices?.[0]?.message?.content ?? '';
			if (reply) {
				messages = [...requestMessages, { role: 'assistant', content: reply }];
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Unable to send message.';
		} finally {
			loading = false;
		}
	};

	onMount(async () => {
		const searchParams = new URLSearchParams(window.location.search);
		const tokenFromUrl = searchParams.get('token');
		if (tokenFromUrl) {
			token = tokenFromUrl;
		}

		const messageHandler = async (event: MessageEvent) => {
			const data = event.data ?? {};
			if (data?.type !== 'openwebui:embed:auth') return;

			const nextToken = data?.token;
			const nextApiBaseUrl = data?.apiBaseUrl;
			if (nextApiBaseUrl && typeof nextApiBaseUrl === 'string') {
				window.sessionStorage.setItem('owui:embed:api-base-url', nextApiBaseUrl);
			}

			if (!nextToken || typeof nextToken !== 'string') {
				error = 'Missing embed auth token.';
				return;
			}

			token = nextToken;
			try {
				await loadPanel();
			} catch (e) {
				error = e instanceof Error ? e.message : 'Failed to load panel.';
			}
		};

		window.addEventListener('message', messageHandler);

		try {
			if (token) {
				await loadPanel();
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load panel.';
		}

		return () => {
			window.removeEventListener('message', messageHandler);
		};
	});
</script>

<svelte:head>
	<title>{panel?.title ?? 'Open WebUI Embed'}</title>
</svelte:head>

<div
	class="h-screen w-full bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex flex-col"
>
	<div class="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
		<div class="text-sm font-semibold">{panel?.title ?? 'Chat'}</div>
	</div>

	<div class="flex-1 overflow-y-auto p-4 space-y-3">
		{#if error}
			<div class="text-xs text-red-500">{error}</div>
		{/if}
		{#if !token}
			<div class="text-xs text-gray-500">Waiting for authentication...</div>
		{/if}
		{#each messages as message}
			<div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
				<div
					class="max-w-[85%] px-3 py-2 text-sm rounded-2xl {message.role === 'user'
						? 'bg-black text-white dark:bg-white dark:text-black'
						: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100'}"
				>
					{message.content}
				</div>
			</div>
		{/each}
	</div>

	<form
		class="p-3 border-t border-gray-100 dark:border-gray-800 flex gap-2"
		on:submit|preventDefault={sendMessage}
	>
		<input
			class="flex-1 px-3 py-2 text-sm rounded-xl bg-gray-100 dark:bg-gray-800 outline-hidden"
			type="text"
			bind:value={input}
			placeholder="Type a message..."
			disabled={!token || loading}
		/>
		<button
			type="submit"
			class="px-3 py-2 text-sm rounded-xl bg-black text-white dark:bg-white dark:text-black disabled:opacity-50"
			disabled={!token || loading}
		>
			Send
		</button>
	</form>
</div>
