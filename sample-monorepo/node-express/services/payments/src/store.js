"use strict";

// In-memory payment store. Fields follow contracts/payment.schema.json.
// Seeded with the same three payments as the python-fastapi variant:
// one completed (refundable), one pending, one already refunded.
const SEED_PAYMENTS = [
  {
    id: "pay-001",
    amount: 100,
    currency: "USD",
    status: "completed",
    customer_email: "ada@example.com",
  },
  {
    id: "pay-002",
    amount: 50,
    currency: "USD",
    status: "pending",
    customer_email: "grace@example.com",
  },
  {
    id: "pay-003",
    amount: 75,
    currency: "EUR",
    status: "refunded",
    customer_email: "alan@example.com",
  },
];

function createStore() {
  const payments = new Map(SEED_PAYMENTS.map((payment) => [payment.id, { ...payment }]));

  return {
    get(paymentId) {
      return payments.get(paymentId);
    },
    list() {
      return Array.from(payments.values());
    },
  };
}

module.exports = { createStore, SEED_PAYMENTS };
