'use strict';

const express = require('express');
const { router } = require('./events');

const app = express();
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'notifications' });
});

app.use(router);

const port = Number(process.env.NOTIFICATIONS_PORT || 8002);

if (require.main === module) {
  app.listen(port, () => {
    console.log(`notifications listening on :${port}`);
  });
}

module.exports = { app, port };
