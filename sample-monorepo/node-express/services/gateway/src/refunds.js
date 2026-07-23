// POST /refunds — validate the body against the RefundRequest contract
// (contracts/refund.schema.json), then forward it to the payments service.
// Validation is written out by hand on purpose: the checks must mirror the
// schema exactly, and the labs practice keeping the two in sync.
const express = require("express");

const router = express.Router();

// Mirrors RefundRequest in contracts/refund.schema.json:
// required payment_id (string), amount (number, minimum 0), reason (string).
function validateRefundRequest(body) {
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return ["body must be a JSON object"];
  }

  const errors = [];

  if (!("payment_id" in body)) {
    errors.push('field "payment_id" is required but missing');
  } else if (typeof body.payment_id !== "string") {
    errors.push('field "payment_id" must be a string');
  }

  if (!("amount" in body)) {
    errors.push('field "amount" is required but missing');
  } else if (typeof body.amount !== "number" || Number.isNaN(body.amount)) {
    errors.push('field "amount" must be a number');
  } else if (body.amount < 0) {
    errors.push('field "amount" is below minimum 0');
  }

  if (!("reason" in body)) {
    errors.push('field "reason" is required but missing');
  } else if (typeof body.reason !== "string") {
    errors.push('field "reason" must be a string');
  }

  return errors;
}

router.post("/refunds", async (req, res) => {
  const errors = validateRefundRequest(req.body);
  if (errors.length > 0) {
    // Reject before anything reaches payments (spec: HTTP 422).
    return res.status(422).json({ detail: errors });
  }

  // Read the env at request time so tests can point the gateway at a stub.
  const paymentsUrl = process.env.PAYMENTS_URL || "http://localhost:8001";

  let response;
  try {
    response = await fetch(`${paymentsUrl}/refunds`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
  } catch (err) {
    return res.status(502).json({
      detail: `payments service unreachable at ${paymentsUrl}: ${err.message}`,
    });
  }

  // Return the payments response verbatim: same status, same body.
  const body = await response.text();
  res.status(response.status);
  const contentType = response.headers.get("content-type");
  if (contentType) {
    res.set("Content-Type", contentType);
  }
  return res.send(body);
});

module.exports = router;
