"use strict";

const assert = require("node:assert/strict");
const {after, test} = require("node:test");
const {createServer} = require("../backend/server");

const servers = [];

async function serve(options) {
  const server = createServer(options);
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  servers.push(server);
  return `http://127.0.0.1:${server.address().port}`;
}

after(async () => {
  await Promise.all(servers.map(server => new Promise(resolve => server.close(resolve))));
});

test("forwards the configured auth header only to the fixed IMD endpoint", async () => {
  let received;
  const base = await serve({
    apiKey:"test-secret",
    authHeader:"x-api-key",
    authPrefix:"",
    fetchImpl:async (url, options) => {
      received = {url:new URL(url), headers:options.headers};
      return new Response(JSON.stringify([{District:"KANPUR", Day_1:"2"}]), {status:200});
    }
  });

  const response = await fetch(`${base}/api/imd/warnings`);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), [{District:"KANPUR", Day_1:"2"}]);
  assert.equal(received.url.origin, "https://api.imd.gov.in");
  assert.equal(received.url.pathname, "/api/v1/districtwarning");
  assert.equal(received.headers["x-api-key"], "test-secret");
});

test("supports query-string authentication without exposing it to the client", async () => {
  let upstreamUrl;
  const base = await serve({
    apiKey:"test-secret",
    authMode:"query",
    queryParameter:"access_key",
    fetchImpl:async url => {
      upstreamUrl = new URL(url);
      return new Response("[]", {status:200});
    }
  });

  const response = await fetch(`${base}/api/imd/rainfall`);
  assert.equal(response.status, 200);
  assert.equal(upstreamUrl.pathname, "/api/v1/districtrainfall");
  assert.equal(upstreamUrl.searchParams.get("access_key"), "test-secret");
  assert.equal(await response.text(), "[]");
});

test("returns a setup error when no credential is configured", async () => {
  const base = await serve({apiKey:"", fetchImpl:() => assert.fail("must not call IMD without a key")});
  const response = await fetch(`${base}/api/imd/warnings`);
  assert.equal(response.status, 503);
  assert.match((await response.json()).error, /not configured/i);
});

test("serves the bundled workbook records used by the dashboard", async () => {
  const base = await serve({apiKey:"test"});
  const response = await fetch(`${base}/records.js`);
  assert.equal(response.status, 200);
  const script = await response.text();
  const match = script.match(/^window\.GARUDA_DATA = (.*);$/s);
  assert.ok(match);
  const data = JSON.parse(match[1]);
  assert.equal(data.source, "road_waterlogging_historical_records.xlsx");
  assert.equal(data.locations.length, 7);
  assert.equal(data.locations.reduce((count, location) => count + location.events.length, 0), 10);
  assert.equal(data.locations.find(location => location.id === "GGN-03").refMin, 120);
});