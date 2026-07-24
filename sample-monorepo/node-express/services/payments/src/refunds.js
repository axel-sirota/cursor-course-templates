"use strict";

const crypto = require("node:crypto");
const express = require("express");

// Decision logic per specs/feature-refunds.md:
// approve iff the payment exists AND status === "completed" AND the requested
// amount is <= the payment amount; reject in every other case with a
// machine-readable reason.
function decide(payment, amount) {
  if (!payment) {
    return { status: "rejected", reason: "payment_not_found" };
  }
  if (payment.status !== "completed") {
    return { status: "rejected", reason: "payment_not_completed" };
  }
  if (amount > payment.amount) {
    return { status: "rejected", reason: "amount_exceeds_payment" };
  }
  return { status: "approved" };
}

// Fire-and-forget delivery: a notifications outage must never fail a refund,
// so every failure path here only logs.
async function postNotification(notificationsUrl, event) {
  try {
    const response = await fetch(`${notificationsUrl}/events`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(event),
    });
    if (!response.ok) {
      console.error(`notification rejected: HTTP ${response.status}`);
    }
  } catch (error) {
    console.error(`notification delivery failed: ${error.message}`);
  }
}

function createRefundsRouter({ store, notificationsUrl }) {
  const router = express.Router();

  router.post("/refunds", async (req, res) => {
    const { payment_id: paymentId, amount, reason } = req.body ?? {};
    if (
      typeof paymentId !== "string" ||
      typeof amount !== "number" ||
      Number.isNaN(amount) ||
      amount < 0 ||
      typeof reason !== "string"
    ) {
      res.status(422).json({ error: "body is not a valid RefundRequest" });
      return;
    }

    const payment = store.get(paymentId);
    const decision = decide(payment, amount);

    // Shape per contracts/refund.schema.json (RefundResult).
    const result = {
      refund_id: `ref-${crypto.randomUUID().slice(0, 8)}`,
      payment_id: paymentId,
      status: decision.status,
      processed_at: new Date().toISOString(),
    };
    if (decision.status === "rejected") {
      result.reason = decision.reason;
    }

    if (decision.status === "approved") {
      await postNotification(notificationsUrl, {
        event_type: "refund.approved",
        payment_id: paymentId,
        refund_id: result.refund_id,
        recipient: payment.customer_email,
      });
    }

    res.status(200).json(result);
  });

  return router;
}

module.exports = { createRefundsRouter, decide };
