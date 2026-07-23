'use strict';

const fs = require('node:fs');
const path = require('node:path');
const express = require('express');

// Field rules mirror contracts/notification.schema.json. The schema is the
// source of truth; if the two ever disagree, the schema wins.
const REQUIRED_FIELDS = ['event_type', 'payment_id', 'refund_id', 'recipient'];
const EVENT_TYPES = ['refund.approved', 'refund.rejected'];

function logPath() {
  return process.env.NOTIFICATIONS_LOG || path.join(process.cwd(), 'notifications.log');
}

// Returns a list of violation messages; empty means the event passes.
function validateEvent(event) {
  if (typeof event !== 'object' || event === null || Array.isArray(event)) {
    return ['document is not an object'];
  }

  const errors = [];
  for (const field of REQUIRED_FIELDS) {
    if (!(field in event)) {
      errors.push(`field "${field}" is required but missing`);
    } else if (typeof event[field] !== 'string') {
      errors.push(
        `field "${field}" value ${JSON.stringify(event[field])} is not of type string`
      );
    }
  }

  if (typeof event.event_type === 'string' && !EVENT_TYPES.includes(event.event_type)) {
    errors.push(
      `field "event_type" value "${event.event_type}" not in enum [${EVENT_TYPES.join(', ')}]`
    );
  }

  return errors;
}

const router = express.Router();

router.post('/events', (req, res) => {
  const errors = validateEvent(req.body);
  if (errors.length > 0) {
    return res.status(400).json({ errors });
  }

  const entry = {
    event_type: req.body.event_type,
    payment_id: req.body.payment_id,
    refund_id: req.body.refund_id,
    recipient: req.body.recipient,
  };
  fs.appendFileSync(logPath(), `${JSON.stringify(entry)}\n`);
  return res.status(201).json(entry);
});

router.get('/events', (req, res) => {
  let raw;
  try {
    raw = fs.readFileSync(logPath(), 'utf8');
  } catch (err) {
    if (err.code === 'ENOENT') {
      return res.json([]);
    }
    throw err;
  }

  const entries = raw
    .split('\n')
    .filter((line) => line.trim() !== '')
    .map((line) => JSON.parse(line));
  return res.json(entries);
});

module.exports = { router, validateEvent, logPath };
