"use strict";

const http = require("node:http");
const https = require("node:https");
const fs = require("node:fs");
const path = require("node:path");
const url = require("node:url");

const frontendPath = path.join(__dirname, "..", "frontend", "index.html");
const recordsPath = path.join(__dirname, "..", "frontend", "data", "road-waterlogging-records.json");
const riskApiBaseUrl = process.env.GARUDAROUTE_RISK_API_BASE_URL || "http://127.0.0.1:8000";

function forwardRiskRequest(request, response, roadId) {
  const parsed = new URL(request.url, `http://${request.headers.host}`);
  const asOf = parsed.searchParams.get("as_of");
  const targetPath = roadId ? `/api/roads/${roadId}/risk` : `/api/roads/risk`;
  const targetUrl = new URL(targetPath, riskApiBaseUrl);
  if (asOf) {
    targetUrl.searchParams.set("as_of", asOf);
  }

  const protocol = targetUrl.protocol === "https:" ? https : http;
  const upstream = protocol.get(targetUrl.toString(), {headers: {"Accept": "application/json"}}, (upstreamRes) => {
    let data = "";
    upstreamRes.on("data", chunk => data += chunk);
    upstreamRes.on("end", () => {
      const statusCode = upstreamRes.statusCode;
      if (statusCode >= 500) {
        response.writeHead(statusCode, {"Content-Type": "application/json; charset=utf-8"});
        response.end(JSON.stringify({error: upstreamRes.statusMessage || "Risk API upstream error"}));
      } else {
        response.writeHead(statusCode, {"Content-Type": "application/json; charset=utf-8"});
        response.end(data);
      }
    });
  });
  upstream.on("error", (error) => {
    response.writeHead(502, {"Content-Type": "application/json; charset=utf-8"});
    response.end(JSON.stringify({error: "Could not reach the Risk API service.", detail: error.message}));
  });
}

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

    if (request.method === "GET" && request.url === "/config.js") {
      response.writeHead(200, {"Content-Type": "application/javascript; charset=utf-8"});
      response.end(`window.GARUDA_CONFIG = ${JSON.stringify({googleMapsApiKey: googleMapsKey})};`);
      return;
    }

    if (request.method === "GET" && request.url === "/records.js") {
      try {
        const records = JSON.parse(fs.readFileSync(recordsPath, "utf8"));
        response.writeHead(200, {"Content-Type": "application/javascript; charset=utf-8"});
        response.end(`window.GARUDA_DATA = ${JSON.stringify(records)};`);
      } catch {
        response.writeHead(500, {"Content-Type": "application/javascript; charset=utf-8"});
        response.end("window.GARUDA_DATA = null;");
      }
      return;
    }

    if (request.method === "GET" && (request.url === "/" || request.url === "/index.html")) {
      response.writeHead(200, {"Content-Type": "text/html; charset=utf-8"});
      fs.createReadStream(frontendPath).pipe(response);
      return;
    }

    // Risk API proxy routes
    if (request.method === "GET" && request.url.startsWith("/api/risk/roads")) {
      const pathname = new URL(request.url, `http://${request.headers.host}`).pathname;
      const roadIdMatch = pathname.match(/\/api\/risk\/roads\/([^/]+)\/risk$/);
      if (roadIdMatch) {
        const roadId = roadIdMatch[1];
        forwardRiskRequest(request, response, roadId);
      } else if (pathname === "/api/risk/roads" || pathname === "/api/risk/roads/") {
        forwardRiskRequest(request, response, null);
      } else {
        response.writeHead(404, {"Content-Type": "application/json; charset=utf-8"});
        response.end(JSON.stringify({error: "Not found"}));
      }
      return;
    }

    const endpoint = {
      "/api/imd/warnings": "districtwarning",
      "/api/imd/rainfall": "districtrainfall"
    }[request.url];
    if (request.method !== "GET" || !endpoint) {
      response.writeHead(404, {"Content-Type": "application/json; charset=utf-8"});
      response.end(JSON.stringify({error: "Not found"}));
      return;
    }
    if (!apiKey) {
      response.writeHead(503, {"Content-Type": "application/json; charset=utf-8"});
      response.end(JSON.stringify({error: "IMD credentials are not configured on the backend."}));
      return;
    }
    if (authMode !== "header" && authMode !== "query") {
      response.writeHead(500, {"Content-Type": "application/json; charset=utf-8"});
      response.end(JSON.stringify({error: "IMD_API_KEY_MODE must be header or query."}));
      return;
    }
    if (authMode === "header" && !/^[A-Za-z0-9-]+$/.test(authHeader)) {
      response.writeHead(500, {"Content-Type": "application/json; charset=utf-8"});
      response.end(JSON.stringify({error: "Invalid IMD_API_KEY_HEADER configuration."}));
      return;
    }

    try {
      const upUrl = new URL(`https://api.imd.gov.in/api/v1/${endpoint}`);
      const headers = {"Accept": "application/json"};
      if (authMode === "header") headers[authHeader] = authPrefix ? `${authPrefix} ${apiKey}` : apiKey;
      else upUrl.searchParams.set(queryParameter, apiKey);
      const upstream = await fetchImpl(upUrl, {headers, signal: AbortSignal.timeout(12000)});
      if (!upstream.ok) {
        const status = upstream.status === 401 || upstream.status === 403 ? upstream.status : 502;
        response.writeHead(status, {"Content-Type": "application/json; charset=utf-8"});
        response.end(JSON.stringify({error: status === 401 || status === 403 ? "IMD rejected the configured credentials." : `IMD upstream returned HTTP ${upstream.status}.`}));
        return;
      }
      const data = await upstream.json();
      response.writeHead(200, {"Content-Type": "application/json; charset=utf-8"});
      response.end(JSON.stringify(data));
    } catch (error) {
      const timedOut = error.name === "TimeoutError";
      response.writeHead(timedOut ? 504 : 502, {"Content-Type": "application/json; charset=utf-8"});
      response.end(JSON.stringify({error: timedOut ? "IMD request timed out." : "Could not reach the IMD service."}));
    }
  });
}

if (require.main === module) {
  const port = Number(process.env.PORT || 3000);
  const host = process.env.HOST || "127.0.0.1";
  createServer().listen(port, host, () => console.log(`Garuda Route listening on http://${host}:${port}`));
}

module.exports = { createServer, riskApiBaseUrl };
