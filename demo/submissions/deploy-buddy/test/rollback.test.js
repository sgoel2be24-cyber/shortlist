const { shouldRollback } = require('../index');
if (!shouldRollback({ errorRate: 0.2 })) throw new Error('expected rollback');
console.log('ok');
