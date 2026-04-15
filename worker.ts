export default {
	async fetch(request: Request, env: { ASSETS: Fetcher }): Promise<Response> {
		const response = await env.ASSETS.fetch(request);
		if (new URL(request.url).pathname.endsWith('.cast')) {
			const headers = new Headers(response.headers);
			headers.set('Access-Control-Allow-Origin', '*');
			return new Response(response.body, { status: response.status, headers });
		}
		return response;
	},
};
