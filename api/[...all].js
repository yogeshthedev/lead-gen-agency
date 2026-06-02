const app = require('./server');

// Vercel requires a function handler for catch-all routes
module.exports = (req, res) => {
  return app(req, res);
};
