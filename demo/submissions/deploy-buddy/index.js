// Deploy Buddy: decides whether a rollback is needed (called by the Switch agent).
const { shouldRollback } = require('./lib/policy'); // lib/policy.js was never committed
module.exports = { shouldRollback };
