"use strict";

const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const frontendPath = path.join(__dirname, "..", "frontend", "index.html");
const recordsPath = path.join(__dirname, "..", "frontend", "data", "road-waterlogging-records.json");

function createServer({
  apiKey = process.env.IMD_API_KEY || "",
  authHeader = process.env.IMD_API_KEY_HEADER || "Authorization",
  authPrefix = process.env.IMD_API_KEY_PREFIX ?? "Bearer",
  authMode = process.env.IMD_API_KEY_MODE || "header",
  queryParameter = process.env.IMD_API_KEY_QUERY_PARAMETER || "key",
  googleMapsKey = process.env.GOOGLE_MAPS_BROWSER_KEY || "",
  fetchImpl = globalThis.fetch
} = {}) {
  return http.createServer(async (request, response) => {
    response.setHeader("X-Content-Type-Options", "nosniff");
    response.setHeader("Cache-Control", "no-store");

    if(request.method === "GET" && request.url === "/config.js") {
      response.writeHead(200, {"Content-Type":"application/javascript; charset=utf-8"});
      response.end(`window.GARUDA_CONFIG = ${JSON.stringify({googleMapsApiKey:googleMapsKey})};`);
      return;
    }

    if(request.method === "GET" && request.url === "/records.js") {
      try {
        const records = JSON.parse(fs.readFileSync(recordsPath, "utf8"));
        response.writeHead(200, {"Content-Type":"application/javascript; charset=utf-8"});
        response.end(`window.GARUDA_DATA = ${JSON.stringify(records)};`);
      } catch {
        response.writeHead(500, {"Content-Type":"application/javascript; charset=utf-8"});
        response.end("window.GARUDA_DATA = null;");
      }
      return;
    }

    if(request.method === "GET" && (request.url === "/" || request.url === "/index.html")) {
      response.writeHead(200, {"Content-Type":"text/html; charset=utf-8"});
      fs.createReadStream(frontendPath).pipe(response);
      return;
    }

    const endpoint = {
      "/api/imd/warnings":"districtwarning",
      "/api/imd/rainfall":"districtrainfall"
    }[request.url];
    if(request.method !== "GET" || !endpoint) {
      response.writeHead(404, {"Content-Type":"application/json; charset=utf-8"});
      response.end(JSON.stringify({error:"Not found"}));
      return;
    }
    if(!apiKey) {
      response.writeHead(503, {"Content-Type":"application/json; charset=utf-8"});
      response.end(JSON.stringify({error:"IMD credentials are not configured on the backend."}));
      return;
    }
    if(authMode !== "header" && authMode !== "query") {
      response.writeHead(500, {"Content-Type":"application/json; charset=utf-8"});
      response.end(JSON.stringify({error:"IMD_API_KEY_MODE must be header or query."}));
      return;
    }
    if(authMode === "header" && !/^[A-Za-z0-9-]+$/.test(authHeader)) {
      response.writeHead(500, {"Content-Type":"application/json; charset=utf-8"});
      response.end(JSON.stringify({error:"Invalid IMD_API_KEY_HEADER configuration."}));
      return;
    }

    try {
      const url = new URL(`https://api.imd.gov.in/api/v1/${endpoint}`);
      const headers = {Accept:"application/json"};
      if(authMode === "header") headers[authHeader] = authPrefix ? `${authPrefix} ${apiKey}` : apiKey;
      else url.searchParams.set(queryParameter, apiKey);
      const upstream = await fetchImpl(url, {headers, signal:AbortSignal.timeout(12000)});
      if(!upstream.ok) {
        const status = upstream.status === 401 || upstream.status === 403 ? upstream.status : 502;
        response.writeHead(status, {"Content-Type":"application/json; charset=utf-8"});
        response.end(JSON.stringify({error:status === 401 || status === 403
          ? "IMD rejected the configured credentials."
          : `IMD upstream returned HTTP ${upstream.status}.`}));
        return;
      }
      const data = await upstream.json();
      response.writeHead(200, {"Content-Type":"application/json; charset=utf-8"});
      response.end(JSON.stringify(data));
    } catch(error) {
      const timedOut = error.name === "TimeoutError";
      response.writeHead(timedOut ? 504 : 502, {"Content-Type":"application/json; charset=utf-8"});
      response.end(JSON.stringify({error:timedOut ? "IMD request timed out." : "Could not reach the IMD service."}));
    }
  });
}

if(require.main === module) {
  const port = Number(process.env.PORT || 3000);
  const host = process.env.HOST || "127.0.0.1";
  createServer().listen(port, host, () => console.log(`Garuda Route listening on http://${host}:${port}`));
}

module.exports = {createServer};