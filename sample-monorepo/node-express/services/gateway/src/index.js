// Gateway service: public HTTP entry point for the refund monorepo.
// Validates incoming requests and forwards them to internal services.
// It makes no refund decisions of its own — payments owns those.
const express = require("express");

const refundsRouter = require("./refunds");

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "gateway" });
});

app.use(refundsRouter);

// Exported so tests can start the app on an ephemeral port.
module.exports = app;

if (require.main === module) {
  const port = Number(process.env.GATEWAY_PORT || 8000);
  app.listen(port, () => {
    console.log(`gateway listening on port ${port}`);
  });
}
