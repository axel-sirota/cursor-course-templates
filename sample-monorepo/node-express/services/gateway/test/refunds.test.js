// Gateway tests: node:test only, no extra test dependencies.
// The app is started on an ephemeral port and exercised with fetch; the
// payments service is replaced by a local stub server whose URL is injected
// through PAYMENTS_URL.
const assert = require("node:assert/strict");
const http = require("node:http");
const { once } = require("node:events");
const { after, before, beforeEach, test } = require("node:test");

const app = require("../src/index");

const REFUND_RESULT = {
  refund_id: "ref_123",
  payment_id: "pay_001",
  status: "approved",
  processed_at: "2026-01-15T10:00:00Z",
};

let appServer;
let gatewayUrl;
let stubServer;
let stubCalls;

before(async () => {
  // Stub payments service: counts calls, always answers with REFUND_RESULT.
  stubServer = http.createServer((req, res) => {
    stubCalls += 1;
    req.resume();
    req.on("end", () => {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(REFUND_RESULT));
    });
  });
  stubServer.listen(0);
  await once(stubServer, "listening");
  process.env.PAYMENTS_URL = `http://localhost:${stubServer.address().port}`;

  appServer = app.listen(0);
  await once(appServer, "listening");
  gatewayUrl = `http://localhost:${appServer.address().port}`;
});

beforeEach(() => {
  stubCalls = 0;
});

after(() => {
  appServer.close();
  stubServer.close();
});

function postRefund(body) {
  return fetch(`${gatewayUrl}/refunds`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

test("GET /health reports ok", async () => {
  const response = await fetch(`${gatewayUrl}/health`);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: "ok", service: "gateway" });
});

test("valid refund request returns the payments response verbatim", async () => {
  const response = await postRefund({
    payment_id: "pay_001",
    amount: 50,
    reason: "duplicate charge",
  });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), REFUND_RESULT);
  assert.equal(stubCalls, 1);
});

test("missing required field returns 422 and payments is never called", async () => {
  const response = await postRefund({ payment_id: "pay_001", amount: 50 });
  assert.equal(response.status, 422);
  const body = await response.json();
  assert.ok(body.detail.some((message) => message.includes("reason")));
  assert.equal(stubCalls, 0);
});

test("wrong field type returns 422 and payments is never called", async () => {
  const response = await postRefund({
    payment_id: "pay_001",
    amount: "fifty",
    reason: "duplicate charge",
  });
  assert.equal(response.status, 422);
  assert.equal(stubCalls, 0);
});

test("negative amount returns 422 and payments is never called", async () => {
  const response = await postRefund({
    payment_id: "pay_001",
    amount: -1,
    reason: "duplicate charge",
  });
  assert.equal(response.status, 422);
  assert.equal(stubCalls, 0);
});

test("unreachable payments service returns 502 with a clear message", async () => {
  const previous = process.env.PAYMENTS_URL;
  // Port 9 (discard protocol) is a safe "nothing listens here" target.
  process.env.PAYMENTS_URL = "http://localhost:9";
  try {
    const response = await postRefund({
      payment_id: "pay_001",
      amount: 50,
      reason: "duplicate charge",
    });
    assert.equal(response.status, 502);
    const body = await response.json();
    assert.ok(body.detail.includes("payments service unreachable"));
  } finally {
    process.env.PAYMENTS_URL = previous;
  }
});
