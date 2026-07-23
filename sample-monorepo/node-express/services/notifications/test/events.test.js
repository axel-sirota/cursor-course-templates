'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

// Point the service at a throwaway log BEFORE loading the app, so tests
// never touch a real notifications.log.
const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'notifications-test-'));
process.env.NOTIFICATIONS_LOG = path.join(tmpDir, 'notifications.log');

const { app } = require('../src/index');

let server;
let baseUrl;

test.before(
  () =>
    new Promise((resolve) => {
      server = app.listen(0, '127.0.0.1', () => {
        baseUrl = `http://127.0.0.1:${server.address().port}`;
        resolve();
      });
    })
);

test.after(() => new Promise((resolve) => server.close(resolve)));

function readLog() {
  try {
    return fs.readFileSync(process.env.NOTIFICATIONS_LOG, 'utf8');
  } catch (err) {
    if (err.code === 'ENOENT') {
      return '';
    }
    throw err;
  }
}

test('POST /events then GET /events round-trips a valid event', async () => {
  const fixturePath = path.join(__dirname, '..', 'fixtures', 'notification_event.json');
  const event = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));

  const post = await fetch(`${baseUrl}/events`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(event),
  });
  assert.equal(post.status, 201);

  const get = await fetch(`${baseUrl}/events`);
  assert.equal(get.status, 200);
  const entries = await get.json();
  assert.equal(entries.length, 1);
  assert.deepEqual(entries[0], event);

  const logLines = readLog()
    .split('\n')
    .filter((line) => line !== '');
  assert.equal(logLines.length, 1);
  assert.deepEqual(JSON.parse(logLines[0]), event);
});

test('POST /events rejects a malformed event with 400 and logs nothing', async () => {
  const before = readLog();

  const res = await fetch(`${baseUrl}/events`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ event_type: 'refund.exploded', payment_id: 'pay_1001' }),
  });
  assert.equal(res.status, 400);

  const body = await res.json();
  assert.ok(Array.isArray(body.errors));
  assert.ok(body.errors.length >= 1);

  const after = readLog();
  assert.equal(after, before);
});
