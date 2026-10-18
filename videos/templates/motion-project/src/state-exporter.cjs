// Optional contract for a film-specific state exporter.
// The film may replace this file or point profile.state_exporter at another
// command.  It must write {"frames":[...]} and must not infer expected focus.
const fs = require('node:fs');
const path = require('node:path');

const output = process.argv[2];
if (!output) throw new Error('state-exporter requires an output path');
const source = path.resolve(__dirname, '..', 'public', 'state.json');
const target = path.resolve(output);
if (!fs.existsSync(source)) {
  throw new Error('public/state.json is missing; author a film-specific exporter or state file');
}
if (source !== target) fs.copyFileSync(source, target);
