"use strict";

const assert = require("node:assert/strict");
const http = require("node:http");
const { after, before, beforeEach, test } = require("node:test");

const { createApp } = require("../src/index");
const { createStore } = require("../src/store");

// Local stub standing in for the notifications service: records every event
// POSTed to /events so tests can assert on delivery without the real
// service running.
const receivedEvents = [];
const stubServer = http.createServer((req, res) => {
  let body = "";
  req.on("data", (chunk) => {
    body += chunk;
  });
  req.on("end", () => {
    if (req.method === "POST" && req.url === "/events") {
      receivedEvents.push(JSON.parse(body));
      res.writeHead(202, { "content-type": "application/json" });
      res.end(JSON.stringify({ accepted: true }));
    } else {
      res.writeHead(404);
      res.end();
    }
  });
});

let appServer;
let baseUrl;

before(async () => {
  await new Promise((resolve) => stubServer.listen(0, "127.0.0.1", resolve));
  const notificationsUrl = `http://127.0.0.1:${stubServer.address().port}`;
  const app = createApp({ store: createStore(), notificationsUrl });
  appServer = http.createServer(app);
  await new Promise((resolve) => appServer.listen(0, "127.0.0.1", resolve));
  baseUrl = `http://127.0.0.1:${appServer.address().port}`;
});

after(async () => {
  await new Promise((resolve) => appServer.close(resolve));
  await new Promise((resolve) => stubServer.close(resolve));
});

beforeEach(() => {
  receivedEvents.length = 0;
});

async function requestRefund(body) {
  const response = await fetch(`${baseUrl}/refunds`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  return { status: response.status, body: await response.json() };
}

test("approves a refund of 50 against the completed payment of 100", async () => {
  const { status, body } = await requestRefund({
    payment_id: "pay-001",
    amount: 50,
    reason: "damaged item",
  });

  assert.equal(status, 200);
  assert.equal(body.status, "approved");
  assert.equal(body.payment_id, "pay-001");
  assert.match(body.refund_id, /^ref-/);
  assert.ok(!Number.isNaN(Date.parse(body.processed_at)));

  assert.equal(receivedEvents.length, 1);
  assert.deepEqual(receivedEvents[0], {
    event_type: "refund.approved",
    payment_id: "pay-001",
    refund_id: body.refund_id,
    recipient: "ada@example.com",
  });
});

test("rejects a refund of 150 against the completed payment of 100", async () => {
  const { status, body } = await requestRefund({
    payment_id: "pay-001",
    amount: 150,
    reason: "changed my mind",
  });

  assert.equal(status, 200);
  assert.equal(body.status, "rejected");
  assert.equal(body.reason, "amount_exceeds_payment");
  assert.equal(receivedEvents.length, 0);
});

test("rejects a refund against a pending payment", async () => {
  const { status, body } = await requestRefund({
    payment_id: "pay-002",
    amount: 10,
    reason: "duplicate charge",
  });

  assert.equal(status, 200);
  assert.equal(body.status, "rejected");
  assert.equal(body.reason, "payment_not_completed");
  assert.equal(receivedEvents.length, 0);
});

test("rejects a refund against an unknown payment", async () => {
  const { status, body } = await requestRefund({
    payment_id: "pay-999",
    amount: 10,
    reason: "never received",
  });

  assert.equal(status, 200);
  assert.equal(body.status, "rejected");
  assert.equal(body.reason, "payment_not_found");
  assert.equal(receivedEvents.length, 0);
});
