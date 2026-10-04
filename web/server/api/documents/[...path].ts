// Proxies /api/documents/** to the FastAPI service, adding the access code server-side.
// Bodies are streamed through, never logged or stored.
export default defineEventHandler(event => proxyToApi(event))
