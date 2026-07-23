"use strict";

const express = require("express");

const { createRefundsRouter } = require("./refunds");
const { createStore } = require("./store");

function createApp({
  store = createStore(),
  notificationsUrl = process.env.NOTIFICATIONS_URL || "http://localhost:8002",
} = {}) {
  const app = express();
  app.use(express.json());

  app.get("/health", (req, res) => {
    res.json({ status: "ok", service: "payments" });
  });

  app.use(createRefundsRouter({ store, notificationsUrl }));

  return app;
}

if (require.main === module) {
  const port = Number(process.env.PAYMENTS_PORT || 8001);
  createApp().listen(port, () => {
    console.log(`payments listening on port ${port}`);
  });
}

module.exports = { createApp };
