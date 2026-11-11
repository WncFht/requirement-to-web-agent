// Run assertions inside the check runner; emit evidence only for executed cases.
const { appendFileSync } = require('node:fs');

async function scenario(id, run, setup) {
  const path = process.env.ARC_CHECK_RESULTS;
  if (!path) throw new Error('Run scenarios through scripts/run_check.py --case ID -- ...');
  const emit = (status, error) => appendFileSync(path, JSON.stringify({ case: id, status, ...(error ? { error } : {}) }) + '\n');
  emit('started');
  let phase = 'setup';
  try {
    if (setup) await setup();
    phase = 'assertions';
    await run();
  } catch (error) {
    const status = phase === 'setup' ? 'blocked' : 'failed';
    emit(status, String(error?.stack || error));
    console.error(`${status.toUpperCase()} ${id}`, error);
    process.exitCode = 1;
    return;
  }
  emit('passed');
  console.log(`PASS ${id}`);
}

module.exports = { scenario };
