// 純函式狀態取自實際繪製共用的 TS 模組；不啟動瀏覽器、不產生理想焦點。
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
for (const ext of ['.ts', '.tsx']) {
  require.extensions[ext] = (mod, filename) => {
    const result = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {compilerOptions: {
      module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true, resolveJsonModule: true,
    }});
    mod._compile(result.outputText, filename);
  };
}
const {getMotionState, setSegments} = require('../src/motion-state.ts');
const segments = require('../public/segments.json');
setSegments(segments);
const frames = [];
for (let f = 0; f < 2825; f++) {
  const t = f / 25;
  const scene = Object.entries(segments).find(([, s]) => t >= s.start && t < s.end);
  if (!scene) throw new Error(`沒有場景：${f}`);
  frames.push({frame: f, t, scene: scene[0], ...getMotionState(scene[0], t)});
}
fs.writeFileSync(process.argv[2], JSON.stringify(frames));
