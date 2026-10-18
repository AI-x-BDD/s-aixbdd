/**
 * CH2 動態敘事的唯一狀態來源：每一幕在影片絕對秒數 t 的顯示清單（幾何、不透明度、顏色）、
 * 鏡頭與強調中的語意 id。TSX 只負責把這份清單畫出來；逐影格 QA 也讀同一個函式，
 * 不另外維護一套理想值。可直接用 Node 24 執行（型別剝除），不依賴 React。
 */
import {Easing, interpolate, interpolateColors} from 'remotion';
import {evolvePath, getBoundingBox, getLength, getPointAtLength, interpolatePath} from '@remotion/paths';

export const SCENES = ['00', '01', '02', '03', '07', '04', '05', '06', '08'] as const;
export type SceneId = (typeof SCENES)[number];
export type Segment = {start: number; end: number; text: string; chars: [number, number][]; cues: {start: number; end: number; lines: string[]}[]};
export type Camera = {cx: number; cy: number; s: number};
export type Box = {x: number; y: number; w: number; h: number};
export type Item = {
	id: string;
	kind: 'rect' | 'path' | 'text';
	cam: boolean; // true：在鏡頭內；false：固定標題列
	opacity: number;
	x: number; y: number; w: number; h: number; // rect 幾何；text 為基線起點與估算框；path 為外框
	d?: string;
	fill?: string;
	stroke?: string;
	sw?: number;
	dash?: string;
	draw?: number; // path 描出進度 0–1
	text?: string;
	size?: number;
	weight?: number;
	anchor?: 'start' | 'middle' | 'end';
	spacing?: number;
	clip?: Box & {on: number}; // 焦點色塊範圍：其內改用深色字
};
export type SceneState = {scene: SceneId; t: number; camera: Camera; items: Item[]; active: string[]};

// 正式 B「深色系統路由」色彩角色；動態只改動作，不換配色。
export const C = {bg: '#201D31', surface: '#373249', ink: '#F4F0FF', muted: '#C4BDD5', focus: '#D8EF8A', onFocus: '#201D31', line: '#847B97'};
export const FPS = 25;
const LEAD = 0.12; // 動作在片語起點前 0.12 秒開始
const HL = 0.2; // 強調色切換時間：中點落在片語起點前，強調判定與畫面一致
const EASE = Easing.bezier(0.33, 0, 0.2, 1);
const FULL: Camera = {cx: 800, cy: 450, s: 1};

let SEG: Record<SceneId, Segment> | null = null;
/** 載入 public/segments.json 的內容；Remotion 與 QA 腳本各自讀檔後呼叫。 */
export const setSegments = (data: Record<string, Segment>) => {
	SEG = data as Record<SceneId, Segment>;
};
export const segment = (id: SceneId) => {
	if (!SEG) throw new Error('尚未載入 segments.json');
	return SEG[id];
};

/** 旁白片語開始的影片絕對秒數（與 video.text_time 相同：第一個有時間的字）。 */
export const at = (id: SceneId, phrase: string, nth = 0) => {
	const {text, chars} = segment(id);
	let index = -1;
	for (let i = 0; i <= nth; i++) {
		index = text.indexOf(phrase, index + 1);
		if (index < 0) throw new Error(`${id} 旁白找不到「${phrase}」`);
	}
	const hit = chars.find(([offset]) => offset >= index);
	if (!hit) throw new Error(`${id}「${phrase}」沒有字元時間`);
	return hit[1];
};

export const ramp = (t: number, t0: number, d: number, a = 0, b = 1) =>
	interpolate(t, [t0, t0 + d], [a, b], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE});
/** 關鍵影格：每個時間點開始以 d 秒緩動到新值，其餘時間靜止。 */
export const track = (t: number, keys: [number, number][], d = 0.45) => {
	let value = keys[0][1];
	for (const [time, next] of keys.slice(1)) value += (next - value) * ramp(t, time, d);
	return value;
};
/**
 * 片語區間的強調值：a 片語前 0.12 秒開始亮；下一片語前 0.04 秒才開始退，
 * 交棒時前後兩項會短暫同時亮（不超過 0.2 秒），確保整段解說期間強調不提前消失。
 */
const OUT = 0.04;
const lit = (t: number, a: number, b = Infinity) => ramp(t, a - LEAD, HL) * (b === Infinity ? 1 : 1 - ramp(t, b - OUT, HL));
const mixc = (v: number, a: string, b: string) => interpolateColors(Math.max(0, Math.min(1, v)), [0, 1], [a, b]);
export const rectPath = (x: number, y: number, w: number, h: number, fold = 0) =>
	`M ${x} ${y} L ${x + w - fold} ${y} L ${x + w} ${y + fold} L ${x + w} ${y + h} L ${x} ${y + h} Z`;
export const pointOn = (d: string, progress: number) => {
	const p = getPointAtLength(d, getLength(d) * progress);
	if (!p) throw new Error(`路徑無法取點：${d}`);
	return p;
};
export {evolvePath};

/** 估算文字框（CJK 全形一字一級，其他約 0.6 級），只供 QA 定位，不影響繪製。 */
const textWidth = (s: string, size: number) => [...s].reduce((w, c) => w + (/[⺀-￯]/.test(c) ? size : size * 0.6), 0);

class Builder {
	items: Item[] = [];
	active = new Set<string>();
	alpha = 1;
	cam = false;
	group(alpha: number, fn: () => void) {
		const before = this.alpha;
		this.alpha *= alpha;
		fn();
		this.alpha = before;
	}
	rect(id: string, x: number, y: number, w: number, h: number, s: Partial<Item> = {}) {
		this.items.push({kind: 'rect', id, x, y, w, h, ...s, cam: this.cam, opacity: (s.opacity ?? 1) * this.alpha});
	}
	path(id: string, d: string, s: Partial<Item> = {}) {
		const b = getBoundingBox(d);
		this.items.push({kind: 'path', id, d, x: b.x1, y: b.y1, w: b.width, h: b.height, ...s, cam: this.cam, opacity: (s.opacity ?? 1) * this.alpha});
	}
	text(id: string, x: number, y: number, text: string, size: number, s: Partial<Item> = {}) {
		const w = textWidth(text, size);
		const left = s.anchor === 'middle' ? x - w / 2 : s.anchor === 'end' ? x - w : x;
		this.items.push({kind: 'text', id, text, size, weight: 600, fill: C.ink, ...s, x, y, w, h: size * 1.05, cam: this.cam, opacity: (s.opacity ?? 1) * this.alpha, ...{bx: left}} as Item);
	}
	on(id: string, value: number | boolean) {
		if (value === true || (typeof value === 'number' && value > 0.5)) this.active.add(id);
	}
}

const header = (b: Builder, eyebrow: string, title: string) => {
	b.cam = false;
	b.text('eyebrow', 90, 85, eyebrow, 24, {fill: C.muted, spacing: 3});
	b.text('title', 90, 168, title, 58);
	b.path('title-rule', 'M90 205 L1510 205', {stroke: C.line, sw: 2});
	b.cam = true;
};

// ── 00 技能越改越難維護？：問題大字刻意停留；右側主檔隨「越改」不斷被塞入新段落而變長。 ──
const s00 = (b: Builder, t: number): Camera => {
	b.cam = false; // 開場沒有標題列，也不使用鏡頭；不套標題線下方裁切。
	b.text('question-1', 90, 280, '技能越改', 112, {weight: 700});
	b.text('question-2', 90, 430, '越難維護？', 112, {weight: 700});
	b.path('question-rule', 'M95 500 L670 500', {stroke: C.ink, sw: 4});
	const lines = ['流程', '規則', '範例', '例外', '輸出格式'];
	const arrive = [0.0, 0.18, 0.4, 0.64, 0.86].map((s) => ramp(t, s, 0.3));
	const grown = arrive.reduce((a, v) => a + v, 0);
	b.rect('skill-md', 1000, 155, 450, 120 + grown * 91, {fill: C.bg, stroke: C.line, sw: 1});
	b.text('skill-md-title', 1025, 205, 'SKILL.md', 29);
	b.path('skill-md-rule', 'M1025 235 L1425 235', {stroke: C.line, sw: 2});
	lines.forEach((label, i) => {
		b.group(arrive[i], () => {
			const dy = (1 - arrive[i]) * -26;
			b.text(`skill-md-${i}`, 1025, 278 + i * 65 + dy, label, 28, {weight: 400});
			if (i < lines.length - 1) b.path(`skill-md-rule-${i}`, `M1025 ${300 + i * 65 + dy} L1425 ${300 + i * 65 + dy}`, {stroke: C.line, sw: 2});
		});
	});
	return FULL;
};

// ── 01 委派：需求交給 Skill Engineering，再往下交給基礎技能並產出；最後預告。 ──
const s01 = (b: Builder, t: number): Camera => {
	header(b, 'SKILL ENGINEERING', '把修改工作交給對的技能');
	const T = {eng: at('01', 'Skill Engineering'), work: at('01', '建立和優化'), give: at('01', '分派給對應的基礎技能'), base: at('01', '基礎技能'), next: at('01', '接下來')};
	const eng = lit(t, T.eng, T.next);
	const parts = lit(t, T.give, T.next);
	const out = lit(t, T.next);
	b.on('eng', eng);
	b.on('parts', parts);
	b.on('out', out);
	b.text('input-label', 100, 350, '輸入', 30, {weight: 400, fill: C.muted});
	b.text('input', 100, 420, '建立／優化需求', 48);
	b.path('input-link', 'M530 395 V345 H640', {stroke: C.line, sw: 3});
	b.rect('eng', 640, 285, 760, 120, {fill: mixc(eng, C.surface, C.focus)});
	b.text('eng-label', 665, 357, 'Skill Engineering：安排工作', 34, {fill: eng > 0.5 ? C.onFocus : C.ink});
	const down1 = ramp(t, T.give - LEAD, 0.5);
	b.path('eng-parts-link', 'M1020 410 V450', {stroke: C.line, sw: 3, draw: down1});
	b.rect('parts', 640, 455, 760, 120, {fill: mixc(parts, C.surface, C.focus)});
	b.text('parts-label', 665, 527, 'Form ＋ Deriver：分工完成', 34, {fill: parts > 0.5 ? C.onFocus : C.ink});
	const down2 = ramp(t, T.base + 0.3, 0.45);
	b.path('parts-out-link', 'M1020 580 V610', {stroke: C.line, sw: 3, draw: down2});
	b.group(ramp(t, T.base + 0.5, 0.35), () => {
		const dy = (1 - ramp(t, T.base + 0.5, 0.35)) * 20;
		b.text('output', 640, 650 + dy, '產出新的／改寫後的 Skill', 36);
	});
	b.path('out-rule', 'M640 705 L1400 705', {stroke: C.line, sw: 2, draw: ramp(t, T.next - LEAD, 0.5)});
	b.group(ramp(t, T.next - LEAD, HL), () => b.text('out', 640, 780, '接下來：分工方式 × 三支案例', 38, {fill: mixc(out, C.ink, C.focus)}));
	// 需求晶片：只走輸入文字右側的連線與兩框之間的空隙，停在框外交棒，不進入任何文字框。
	const leg1 = ramp(t, T.work - LEAD, 1.0);
	const leg2 = ramp(t, T.give - LEAD, 0.9);
	const r1 = 'M 530 452 L 530 345 L 558 345';
	const r2 = 'M 558 345 L 558 430 L 1020 430';
	const p = leg2 > 0 ? pointOn(r2, leg2) : pointOn(r1, leg1);
	// 交給 Engineering 後停在框左側等待；分派時沿兩框之間的空隙交到基礎技能，再退場。
	const chip = ramp(t, T.work - LEAD, 0.2) * (1 - ramp(t, T.give + 0.8, 0.2));
	b.group(chip, () => {
		b.rect('request', p.x - 80, p.y - 22, 160, 44, {fill: C.focus});
		b.text('request-label', p.x - 58, p.y + 9, '修改需求', 24, {fill: C.onFocus});
	});
	return FULL;
};

// ── 02 兩組技能：群組卡片形變為標題列、部位逐項落位；推近看細節、回全景看抽取。 ──
const LABELS = ['用途說明', '執行流程', '規則', '樣板', '腳本'];
const DETAILS = ['何時使用這支 Skill？', '實際執行哪些步驟？', '判斷依據與正反例', '輸出骨架與完成範例', '輸入、輸出與執行方式'];
const TILE = {y: 330, w: 260, h: 112, x: (i: number) => 90 + i * 290};
const s02 = (b: Builder, t: number): Camera => {
	header(b, 'FORM × 5  /  DERIVER × 3', '兩種分工，處理不同問題');
	const T = {
		overview: at('02', '先看兩種分工'), form: at('02', '一組是格式把關'),
		enumerate: LABELS.map((w) => at('02', w)),
		detail: ['用途說明讓', 'SOP 寫清楚', '規則附', '樣板提供', '腳本則'].map((p) => at('02', p)),
		derive: at('02', '另一組是部位抽取'),
		extract: [at('02', '規則、樣板或'), at('02', '樣板或腳本'), at('02', '腳本從流程')],
	};
	const windowCenter = (i: number) => (i <= 2 ? 655 : 945); // 推近時前四項／後四項各成完整視窗
	const cam: Camera = {
		// 第一次推近等列舉的最後一項（腳本）講完才開始，避免當下主焦點被推出畫面。
		cx: track(t, [[0, 800], [T.detail[0] - OUT, windowCenter(0)], ...T.detail.slice(1).map((s, i): [number, number] => [s - 0.3, windowCenter(i + 1)]), [T.derive - LEAD, 800]], 0.6),
		cy: track(t, [[0, 450], [T.detail[0] - OUT, 420], [T.derive - LEAD, 450]], 0.6),
		s: track(t, [[0, 1], [T.detail[0] - OUT, 1.3], [T.derive - LEAD, 1]], 0.6),
	};
	const view = {left: cam.cx - 800 / cam.s, right: cam.cx + 800 / cam.s};
	// 待命的 Deriver 卡：推近時淡出；回全景時等鏡頭大致回位才淡入，避免大塊殘影。
	const pushed = ramp(t, T.detail[0] - OUT, 0.4) * (1 - ramp(t, T.derive - LEAD + 0.15, 0.2));
	const overview = lit(t, T.overview, T.form);
	const formsHead = lit(t, T.form, T.derive);
	const deriveLit = lit(t, T.derive);
	b.on('overview', overview);
	b.on('forms-head', formsHead);
	b.on('derive', deriveLit);

	const toForm = ramp(t, T.form - LEAD, 0.6);
	const toDerive = ramp(t, T.derive - LEAD, 0.35);
	b.group(ramp(t, T.overview - LEAD, HL), () => {
		b.path('overview', interpolatePath(toForm, rectPath(90, 300, 620, 260), rectPath(90, 250, 1420, 60)), {fill: C.surface, stroke: C.focus, sw: 3 * overview});
		b.group(1 - ramp(t, T.form - LEAD, 0.2), () => {
			b.text('form-group-title', 130, 410, '格式把關', 48);
			b.text('form-group-count', 130, 500, '× 5', 64, {fill: C.focus});
		});
		// 群組標題先在 0.2 秒內退場，再接著淡入標題列文字，兩者不重疊。
		b.group(ramp(t, T.form - LEAD + 0.2, 0.12), () =>
			b.text('forms-head', Math.max(115, view.left + 25), 293, 'FORM：把關各部位格式', 34, {fill: mixc(formsHead, C.ink, C.focus)}));
		// 推近時待命的 Deriver 卡會出鏡，先淡出；回全景再回來並形變為 Deriver 標題列。
		b.group(1 - pushed, () => {
			const parked = interpolatePath(toForm, rectPath(890, 300, 620, 260), rectPath(1110, 640, 400, 110));
			b.path('derive', interpolatePath(toDerive, parked, rectPath(90, 470, 1420, 56)), {fill: C.surface, stroke: C.focus, sw: 3 * overview, opacity: 1 - toForm * 0.55 + toDerive * 0.55});
			b.group(1 - ramp(t, T.derive - LEAD, 0.2), () =>
				b.text('derive-group-title', track(t, [[0, 930], [T.form - LEAD, 1140]], 0.6), track(t, [[0, 410], [T.form - LEAD, 705]], 0.6), '部位抽取 × 3', track(t, [[0, 48], [T.form - LEAD, 32]], 0.6), {fill: C.muted}));
		});
		b.group(ramp(t, T.derive - LEAD + 0.35, 0.25), () => b.text('derive-head', 115, 510, 'DERIVER：從流程分出部位', 34, {fill: mixc(deriveLit, C.ink, C.focus)}));
	});
	b.group(ramp(t, T.form - LEAD, 0.3) * (1 - toDerive * 0.6), () =>
		LABELS.forEach((_, i) => b.rect(`slot-${i}`, TILE.x(i) + 1.5, TILE.y + 1.5, TILE.w - 3, TILE.h - 3, {fill: 'none', stroke: C.line, sw: 3, dash: '10 8'})));
	// 部位：唸到時從標題列落入空位並亮起；詳解時依序再亮一次。
	LABELS.forEach((label, i) => {
		const value = lit(t, T.enumerate[i], T.enumerate[i + 1] ?? T.detail[0]) + lit(t, T.detail[i], T.detail[i + 1] ?? T.derive);
		b.on(`p${i}`, value);
		const arrive = ramp(t, T.enumerate[i] - LEAD, 0.45);
		b.group(Math.min(arrive / 0.5, 1) * (1 - toDerive * 0.35), () => {
			const y = TILE.y + (1 - arrive) * -70;
			b.rect(`p${i}`, TILE.x(i), y, TILE.w, TILE.h, {fill: mixc(value, C.surface, C.focus)});
			b.text(`p${i}-label`, TILE.x(i) + 25, y + 68, label, 34, {fill: value > 0.5 ? C.onFocus : C.ink});
		});
	});
	const focusIndex = track(t, [[0, 0], ...T.detail.map((s, i): [number, number] => [s - LEAD, i])], 0.35);
	const tileCenter = TILE.x(0) + focusIndex * 290 + 130;
	const panelX = Math.min(view.right - 580, Math.max(view.left + 20, tileCenter - 280));
	b.group(ramp(t, T.detail[0] - LEAD, 0.25) * (1 - ramp(t, T.derive - LEAD, 0.25)), () => {
		b.rect('detail-panel', panelX, 470, 560, 104, {fill: 'none', stroke: C.focus, sw: 3});
		b.path('detail-pointer', `M ${tileCenter} 446 L ${tileCenter} 470`, {stroke: C.focus, sw: 3});
		DETAILS.forEach((d, i) => b.group(Math.max(0, 1 - Math.abs(focusIndex - i) * 2), () => b.text(`detail-${i}`, panelX + 28, 535, d, 36)));
	});
	// 部位抽取：流程片段沿曲線飛出、形變為獨立檔案，原位置留下虛線空位。
	const doc = ramp(t, T.derive + 0.3, 0.4);
	const STRIPS = ['規則', '樣板', '腳本'];
	const FILES = [['rules/', '規則抽取'], ['templates/', '樣板抽取'], ['scripts/', '腳本抽取']];
	b.group(doc, () => {
		b.path('flow-doc', rectPath(90, 548, 430, 222, 32), {fill: 'none', stroke: C.line, sw: 2});
		b.text('flow-doc-title', 118, 590, '流程步驟', 26, {fill: C.muted});
		STRIPS.forEach((label, i) => b.rect(`flow-slot-${i}`, 118, 608 + i * 52, 370, 40, {fill: 'none', stroke: C.line, sw: 2, dash: '8 6', opacity: ramp(t, T.extract[i] - LEAD + 0.1, 0.3)}));
		STRIPS.forEach((label, i) => {
			const from = {x: 118, y: 608 + i * 52, w: 370, h: 40};
			const to = {x: 610 + i * 310, y: 560, w: 270, h: 180};
			const start = T.extract[i] - LEAD;
			const move = ramp(t, start, 0.55);
			const value = lit(t, T.extract[i], T.extract[i + 1] ?? Infinity);
			b.on(`d${i}`, value);
			const route = `M ${from.x + from.w / 2} ${from.y + from.h / 2} C ${from.x + 520} ${from.y + 20}, ${to.x + to.w / 2} ${to.y - 60}, ${to.x + to.w / 2} ${to.y + to.h / 2}`;
			const p = pointOn(route, move);
			const w = from.w + (to.w - from.w) * move;
			const h = from.h + (to.h - from.h) * move;
			const landed = ramp(t, start + 0.55, 0.2);
			b.path(`d${i}`, interpolatePath(move, rectPath(p.x - from.w / 2, p.y - from.h / 2, from.w, from.h, 0), rectPath(p.x - w / 2, p.y - h / 2, w, h, 30)), {fill: mixc(value, C.surface, C.focus), stroke: C.focus, sw: landed * (1 - value) * 2});
			// 名稱跟著物件走：流程片段上的字先退，抽取名稱隨即出現在飛行中的片段上，到位後才補路徑。
			b.text(`d${i}-strip`, from.x + 20, from.y + 29, label, 26, {fill: C.muted, opacity: 1 - ramp(t, start, 0.1)});
			b.text(`d${i}-label`, p.x - w / 2 + 20 + 4 * move, p.y + 10 + 30 * landed, FILES[i][1], 26 + 4 * move, {fill: value > 0.5 ? C.onFocus : C.ink, opacity: ramp(t, start + 0.1, 0.1)});
			b.text(`d${i}-path`, to.x + 24, to.y + 70, FILES[i][0], 30, {fill: value > 0.5 ? C.onFocus : C.ink, opacity: landed});
		});
	});
	// 頁尾在推近前先退場、之後不再出現，回全景時不會留下被切的殘句。
	b.text('footer', 90, 805, '五個格式責任，三種抽取工作；兩組不是同一套分類。', 32, {weight: 400, fill: C.muted, opacity: 1 - ramp(t, T.detail[0] - OUT - 0.15, 0.15)});
	return cam;
};

// ── 03 先找原因：四步依旁白由上而下展開；確認閘門在「都確認後」亮起、「才開始動手」打開，整理 SOP 才通過。 ──
const s03 = (b: Builder, t: number): Camera => {
	header(b, 'OPTIMIZATION / 先確認，再施工', '先找原因，再決定怎麼改');
	const T = {s: [at('03', '收到優化需求'), at('03', '再找出差異'), at('03', '根因和修改計畫'), at('03', '接著整理')], confirm: at('03', '確認後'), go: at('03', '才開始動手'), parts: at('03', '判斷每一步')};
	const rows = [['01   預期', '哪裡不滿意？'], ['02   根因', '差異怎麼來？'], ['03   修改計畫', '確認後才動手'], ['04   整理 SOP', '逐步判斷部位']];
	const Y = [280, 390, 500, 640];
	rows.forEach(([label, detail], i) => {
		const shown = ramp(t, T.s[i] - LEAD, HL);
		const slide = ramp(t, T.s[i] - LEAD, 0.45);
		const current = lit(t, T.s[i], T.s[i + 1] ?? Infinity);
		b.on(`v${i}`, shown);
		b.on(`s${i}`, current);
		// 第四步從閘門上方穿過開口落位；其餘由下往上滑入。
		const dy = i === 3 ? (1 - slide) * -90 : (1 - slide) * 30;
		b.group(shown, () => {
			b.rect(`v${i}`, 450, Y[i] + dy, 1000, 95, {fill: C.surface, stroke: C.focus, sw: 3 * current});
			b.text(`s${i}`, 490, Y[i] + 62 + dy, label, 40, {fill: mixc(current, C.ink, C.focus)});
			b.text(`s${i}-detail`, 900, Y[i] + 62 + dy, detail, 31, {weight: 400, fill: C.muted});
		});
	});
	// 進度線：從第一步一路延伸到目前這一步。
	const reach = track(t, [[0, Y[0] + 47], ...T.s.slice(1).map((s, i): [number, number] => [s - LEAD, Y[i + 1] + 47])], 0.45);
	b.group(ramp(t, T.s[0] - LEAD, HL), () => {
		b.path('progress', `M 420 ${Y[0] + 47} L 420 ${reach}`, {stroke: C.focus, sw: 4});
		b.rect('progress-dot', 412, reach - 8, 16, 16, {fill: C.focus});
	});
	// 確認閘門：說到修改計畫時出現；「都確認後」轉為焦點色；「才開始動手」向兩側打開。
	const gateIn = ramp(t, T.s[2] + 0.4, 0.3);
	const confirmed = ramp(t, T.confirm - LEAD, HL);
	const open = ramp(t, T.go - LEAD, 0.6);
	b.group(gateIn, () => {
		b.rect('gate-left', 450, 614, 500 * (1 - open), 8, {fill: mixc(confirmed, C.line, C.focus)});
		b.rect('gate-right', 950 + 500 * open, 614, 500 * (1 - open), 8, {fill: mixc(confirmed, C.line, C.focus)});
	});
	// 第四步：說到「判斷每一步需要哪些部位」時，列出可能抽出的部位，銜接下一幕的抽取。
	['規則', '樣板', '腳本'].forEach((label, i) => {
		const v = ramp(t, T.parts - LEAD + i * 0.12, 0.3);
		b.group(v, () => {
			b.rect(`part-${i}`, 1120 + i * 108, Y[3] + 27 + (1 - v) * 12, 96, 42, {fill: 'none', stroke: C.focus, sw: 2});
			b.text(`part-${i}-label`, 1144 + i * 108, Y[3] + 57 + (1 - v) * 12, label, 24, {fill: C.focus});
		});
	});
	b.text('footer', 90, 810, '根因與修改計畫確認，是開始施工的前提。', 32, {weight: 400, fill: C.muted});
	return FULL;
};

// ── 07 抽出規則並接回：規則需求沿路徑交棒、形變為規則檔，回接 SOP；既有檔案繞過抽取。 ──
const s07 = (b: Builder, t: number): Camera => {
	header(b, 'EXTRACTION / 產出檔案只是其中一步', '拆出規則，也要接回讀取時機');
	const T = {step: at('07', '例如'), need: at('07', '判斷規則'), give: at('07', '就交給規則抽取技能'), write: at('07', '它請格式技能'), file: at('07', '寫好規則檔'), back: at('07', '再更新流程'), read: at('07', '交代何時讀'), branches: at('07', '需要固定輸出'), existing: at('07', '既有檔案只改內容'), direct: at('07', '直接交給格式技能')};
	const cam: Camera = {
		// 開場推近 SOP 的那一步，交棒時回全景；之後保持全景，讓 SOP 與既有檔案的繞行同時可見。
		cx: track(t, [[0, 551], [T.give - 0.3, 800]], 0.8),
		cy: track(t, [[0, 400], [T.give - 0.3, 450]], 0.8),
		s: track(t, [[0, 1.45], [T.give - 0.3, 1]], 0.8),
	};
	// 強調：步驟 3 全程以框線標出；derive 在交棒與寫規則期間；form 從被呼叫起；回接、分支、既有檔案各自從片語起。
	const stepBand = lit(t, T.step, T.give + 0.5);
	const stepRing = lit(t, T.step);
	const deriveFill = lit(t, T.give, T.write);
	const deriveRing = lit(t, T.give, T.back);
	const formShown = ramp(t, T.write - LEAD, 0.35);
	const formFill = Math.min(1, lit(t, T.write, T.back) + lit(t, T.direct));
	const formRing = lit(t, T.write);
	const lanes = lit(t, T.branches, T.existing);
	const existing = lit(t, T.existing);
	b.on('step', stepRing);
	b.on('extract', deriveRing);
	b.on('write', formRing);
	b.on('branches', lanes);
	b.on('existing', existing);
	b.path('sop-doc', rectPath(90, 240, 420, 340, 36), {fill: C.surface});
	b.text('sop-title', 120, 292, 'SOP', 34);
	b.text('sop-step-1', 120, 350, '步驟 1　讀取需求', 28, {weight: 400, fill: C.muted});
	b.text('sop-step-2', 120, 400, '步驟 2　判斷部位', 28, {weight: 400, fill: C.muted});
	b.rect('step-band', 106, 420, 388, 46, {fill: C.focus, opacity: stepBand});
	b.rect('step', 107.5, 421.5, 385, 43, {fill: 'none', stroke: C.focus, sw: 3, opacity: stepRing});
	b.text('step-label', 120, 452, '步驟 3　需要更多判斷規則', 28, {fill: stepBand > 0.5 ? C.onFocus : C.ink});
	const read = ramp(t, T.read - LEAD, 0.4);
	b.text('sop-read', 120 + (1 - read) * 40, 530, '讀取：何時讀、怎麼用', 28, {fill: C.focus, opacity: read});
	b.path('sop-derive-link', 'M510 285 L620 285', {stroke: C.line, sw: 2});
	b.rect('extract', 620, 240, 340, 90, {fill: mixc(deriveFill, C.surface, C.focus), stroke: C.focus, sw: 3 * deriveRing});
	b.text('extract-label', 645, 283, 'derive-rule', 32, {fill: deriveFill > 0.5 ? C.onFocus : C.ink});
	b.text('extract-sub', 645, 315, '規則抽取', 22, {weight: 400, fill: deriveFill > 0.5 ? C.onFocus : C.muted});
	b.group(formShown, () => {
		b.path('derive-form-link', 'M960 285 L1090 285', {stroke: C.line, sw: 2});
		b.rect('write', 1090, 240, 420, 90, {fill: mixc(formFill, C.surface, C.focus), stroke: C.focus, sw: 3 * formRing});
		b.text('write-label', 1115, 283, 'form-rule', 32, {fill: formFill > 0.5 ? C.onFocus : C.ink});
		b.text('write-sub', 1115, 315, '寫好規則檔', 22, {weight: 400, fill: formFill > 0.5 ? C.onFocus : C.muted});
	});
	const laneIn = ramp(t, T.branches - LEAD, 0.6);
	['固定輸出 → derive-template', '自動處理 → derive-script'].forEach((label, i) => b.group(laneIn, () => {
		const y = 370 + i * 76 + (1 - laneIn) * -(80 + i * 76);
		b.rect(i === 0 ? 'branches' : `branches-${i}`, 620, y, 340, 56, {fill: 'none', stroke: mixc(lanes, C.line, C.focus), sw: 2, dash: '8 6'});
		b.text(`branches-${i}-label`, 640, y + 36, label, 22, {weight: 400, fill: mixc(lanes, C.muted, C.focus)});
	}));
	const back = ramp(t, T.back - LEAD, 1.0);
	b.on('back', back > 0);
	b.path('back', 'M 1300 570 V 640 H 300 V 584', {stroke: C.focus, sw: 7, draw: back, opacity: back > 0 ? 1 : 0});
	b.path('back-arrow', 'M 288 604 L 300 584 L 312 604', {stroke: C.focus, sw: 5, opacity: ramp(back, 0.92, 0.08)});
	b.group(ramp(t, T.back + 0.3, 0.3), () => {
		b.rect('back-label-box', 560, 612, 480, 56, {fill: C.surface});
		b.text('back-label', 585, 651, 'form-sop：接回讀取時機', 28, {fill: C.focus});
	});
	// 規則需求晶片：停在節點正下方交棒，形變成規則檔；名稱跟著形變，落地後補類型與路徑。
	const leg1 = ramp(t, T.give - LEAD, 1.1);
	const leg2 = ramp(t, T.write - LEAD, 1.0);
	const morph = ramp(t, T.file - LEAD, 0.7);
	const r1 = 'M 580 443 C 640 443, 640 362, 790 362'; // 從 SOP 文件右緣外出發，不壓住步驟 3 的文字
	const r2 = 'M 790 362 L 1300 362 L 1300 480';
	const p = leg2 > 0 ? pointOn(r2, leg2) : pointOn(r1, leg1);
	const settled = ramp(t, T.back - LEAD, 0.4);
	b.group(ramp(t, T.need - LEAD, 0.3), () => {
		b.path('rule-file', interpolatePath(morph, rectPath(p.x - 85, p.y - 24, 170, 48), rectPath(1150, 390, 300, 180, 30)), {fill: mixc(settled, C.focus, C.surface), stroke: C.focus, sw: 3});
		// 「判斷規則」名稱全程跟著物件：形變時從晶片內移到規則檔標題位置並放大，不先退場；落地後才補類型與路徑。
		b.text('rule-need-label', p.x - 62 + (1180 - (p.x - 62)) * morph, p.y + 9 + (460 - (p.y + 9)) * morph, '判斷規則', 24 + 8 * morph, {fill: mixc(settled, C.onFocus, C.ink)});
		b.group(ramp(t, T.file - LEAD + 0.7, 0.2), () => {
			b.text('rule-file-label', 1180, 505, '規則檔', 24, {weight: 400, fill: mixc(settled, C.onFocus, C.muted)});
			b.text('rule-file-path', 1180, 540, 'rules/判斷規則.md', 20, {weight: 400, fill: mixc(settled, C.onFocus, C.muted)});
		});
	});
	const enter = ramp(t, T.existing - LEAD, 0.6);
	b.group(enter, () => {
		b.rect('existing', 1240 + (1 - enter) * 360, 700, 200, 52, {fill: C.surface, stroke: C.focus, sw: 3});
		b.text('existing-label', 1262 + (1 - enter) * 360, 736, '既有檔案', 26);
		b.text('existing-sub', 1240 + (1 - enter) * 360, 790, '只改內容', 24, {weight: 400, fill: C.muted});
	});
	const direct = ramp(t, T.direct - LEAD, 0.8);
	b.path('existing-direct', 'M 1440 726 H 1490 V 330', {stroke: C.focus, sw: 5, draw: direct, opacity: direct > 0 ? 1 : 0});
	b.path('existing-arrow', 'M 1478 350 L 1490 330 L 1502 350', {stroke: C.focus, sw: 5, opacity: ramp(direct, 0.92, 0.08)});
	return cam;
};

// ── 04 慣例式提交：推近主檔看混在一起的三類內容；拆成時回全景，分類與訊息格式飛出成規則檔，
//    範例拆成正反例分到各規則，主檔縮成只帶流程，最後依需要接上歷史處理。 ──
const s04 = (b: Builder, t: number): Camera => {
	header(b, 'CASE 01 / 主檔帶流程，規則按需讀取', '慣例式提交：依決策分開規則');
	const T = {before: at('04', '這次三支技能'), case: at('04', '慣例式提交'), cls: at('04', '分類、訊息格式和範例'), msg: at('04', '訊息格式和範例'), ex: at('04', '範例混在主檔'), split: at('04', '現在拆成'), three: at('04', '三份規則'), flow: at('04', '流程在需要時'), need: at('04', '需要時讀取')};
	const cam: Camera = {
		cx: track(t, [[0, 800], [T.case - 0.2, 520], [T.split - LEAD, 800]], 0.7),
		// 推近 1.3 倍時主檔上緣落在標題線下方（y≈222）、下緣在 y≈820。
		cy: track(t, [[0, 450], [T.case - 0.2, 455], [T.split - LEAD, 450]], 0.7),
		s: track(t, [[0, 1], [T.case - 0.2, 1.3], [T.split - LEAD, 1]], 0.7),
	};
	const before = lit(t, T.before, T.split);
	const items = [lit(t, T.cls, T.msg), lit(t, T.msg, T.ex), lit(t, T.ex, T.split)];
	const after = lit(t, T.split);
	b.on('before', before);
	['before-class', 'before-message', 'before-example'].forEach((id, i) => b.on(id, items[i]));
	b.on('after', after);
	// 主檔：拆分後縮短，標題由「原本混寫」換成「SOP 主檔」。
	const shrink = ramp(t, T.three - LEAD, 0.6);
	b.rect('before', 90, 280, 310, 460 - shrink * 210, {fill: C.surface, stroke: C.focus, sw: 3 * before});
	b.text('before-title', 120, 345, '原本混寫', 40, {opacity: 1 - ramp(t, T.three - LEAD, 0.14)});
	b.group(ramp(t, T.three - LEAD + 0.14, 0.14), () => {
		b.text('sop-title', 120, 345, 'SOP 主檔', 40);
		b.text('sop-sub', 120, 410, '只帶流程', 30, {weight: 400, fill: C.muted});
	});
	b.group(ramp(t, T.split - LEAD, 0.3), () => b.text('after', 500, 335, '現在：在對的決策點讀取', 45, {fill: mixc(after, C.ink, C.focus)}));
	const CARD = (i: number) => ({x: 500 + i * 340, y: 470, w: 280, h: 200});
	const names = ['變更分類', '提交訊息', '歷史處理'];
	// 分類、訊息格式：從主檔飛出並形變成規則檔。
	['分類', '訊息格式'].forEach((label, i) => {
		const from = {x: 112, y: 400 + i * 75, w: 260, h: 50};
		const to = CARD(i);
		const move = ramp(t, T.split - LEAD + i * 0.25, 0.55);
		const p = pointOn(`M ${from.x + from.w / 2} ${from.y + from.h / 2} C ${from.x + 420} ${from.y}, ${to.x + to.w / 2} ${to.y - 80}, ${to.x + to.w / 2} ${to.y + to.h / 2}`, move);
		const w = from.w + (to.w - from.w) * move;
		const h = from.h + (to.h - from.h) * move;
		const moving = move > 0 && move < 1 ? 1 : 0;
		b.path(`rule-${i}`, interpolatePath(move, rectPath(p.x - from.w / 2, p.y - from.h / 2, from.w, from.h), rectPath(p.x - w / 2, p.y - h / 2, w, h, 28)), {fill: mixc(moving || items[i], C.surface, C.focus), stroke: C.focus, sw: 2 * after, opacity: move > 0 ? 1 : 0});
		const start = T.split - LEAD + i * 0.25;
		b.text(['before-class', 'before-message'][i], 120, 435 + i * 75, label, 40, {weight: 400, fill: mixc(items[i], C.ink, C.focus), opacity: 1 - ramp(t, start, 0.1)});
		// 規則名稱隨飛行中的檔案移動（焦點色上用深色字），到位後才補副標。
		const landed = ramp(t, start + 0.55, 0.2);
		b.text(`rule-${i}-name`, p.x - w / 2 + 20 + 4 * move, p.y + 10 - 48 * move, names[i], 28 + 8 * move, {fill: move > 0 && move < 1 ? C.onFocus : C.ink, opacity: ramp(t, start + 0.1, 0.1)});
		b.text(`rule-${i}-sub`, to.x + 24, to.y + 108, '獨立規則檔', 26, {weight: 400, fill: C.muted, opacity: landed});
	});
	// 歷史處理：說到「三份規則」時出現；只在需要時讀取，以虛線表示。
	const third = ramp(t, T.three - LEAD, 0.4);
	b.group(third, () => {
		const c = CARD(2);
		b.path('rule-2', rectPath(c.x, c.y, c.w, c.h, 28), {fill: 'none', stroke: mixc(after, C.line, C.focus), sw: 2, dash: '10 8'});
		b.text('rule-2-name', c.x + 24, c.y + 62, names[2], 36);
		b.text('rule-2-sub', c.x + 24, c.y + 108, '需要時讀取', 26, {weight: 400, fill: C.muted});
	});
	// 範例：拆成三份正反例，分別附到三份規則。
	b.text('before-example', 120, 585, '範例', 40, {weight: 400, fill: mixc(items[2], C.ink, C.focus), opacity: 1 - ramp(t, T.split - LEAD + 0.5, 0.12)});
	[0, 1, 2].forEach((i) => {
		// 間隔 0.35 秒依序出發：後一張經過時前一張已升進自己的規則檔，三張的字不會疊在一起。
		const move = ramp(t, T.split - LEAD + 0.5 + i * 0.35, 0.8);
		const to = CARD(i);
		// 先下到卡片下方的通道（y=760）橫走，到自己的規則檔正下方才垂直上升，不經過其他卡片的落點。
		const p = pointOn(`M 160 575 L 160 760 L ${to.x + 84} 760 L ${to.x + 84} ${to.y + 158}`, move);
		b.group(move > 0 ? 1 : 0, () => {
			b.rect(`example-${i}`, p.x - 60, p.y - 18, 120, 36, {fill: C.focus});
			b.text(`example-${i}-label`, p.x - 46, p.y + 9, '正反例', 24, {fill: C.onFocus});
		});
	});
	// 流程在需要時讀取：從主檔接到三份規則，歷史處理那條為虛線，說到「需要時」才接上。
	const bus = ramp(t, T.flow - LEAD, 0.7);
	// 讀取線走標題下方的空隙（y=410），再分到各規則檔頂端，不穿過標題文字。
	b.path('read-bus', 'M 400 410 H 640 V 470 M 640 410 H 980 V 470', {stroke: C.focus, sw: 3, draw: bus, opacity: bus > 0 ? 1 : 0});
	const need = ramp(t, T.need - LEAD, 0.6);
	b.path('read-history', 'M 980 410 H 1320 V 470', {stroke: C.focus, sw: 3, dash: '10 8', draw: need, opacity: need > 0 ? 1 : 0});
	return cam;
};

// ── 05 主幹式開發：混在一起的判準拆成共通與兩份任務規則；任務先讀共通判準，再分成規劃與審查各自載入。 ──
const s05 = (b: Builder, t: number): Camera => {
	header(b, 'CASE 02 / 共通判準 ＋ 任務規則', '主幹式開發：共通先讀，再依任務分流');
	const T = {start: at('05', '主幹式開發'), common: at('05', '共通判準'), plan: at('05', '變更規劃和'), flow: at('05', '工作流程評估'), read: at('05', '先讀共通判準'), route: at('05', '再依規劃'), review: at('05', '審查任務'), load: at('05', '載入相關規則')};
	const commonFill = lit(t, T.start, T.plan) + lit(t, T.read, T.route);
	const commonRing = lit(t, T.start);
	const split = lit(t, T.plan, T.read);
	const routed = lit(t, T.route);
	b.on('common', Math.max(commonFill, commonRing));
	b.on('task', Math.max(split, routed));
	b.rect('common', 420, 250, 760, 110, {fill: mixc(Math.min(1, commonFill), C.surface, C.focus), stroke: C.focus, sw: 3 * commonRing});
	const dark = commonFill > 0.5;
	b.text('common-mixed', 445, 318, '主檔：判準＋規劃＋評估', 34, {fill: dark ? C.onFocus : C.ink, opacity: 1 - ramp(t, T.common - LEAD, 0.14)});
	b.group(ramp(t, T.common - LEAD + 0.14, 0.14), () => b.text('common-label', 445, 318, '每次先讀：共通 TBD 判準', 34, {fill: dark ? C.onFocus : C.ink}));
	// 兩份任務規則：從共通區塊拆出，形變並落到下方。
	const cards = [{label: '變更規劃', x: 420, at: T.plan}, {label: '工作流程評估', x: 820, at: T.flow}];
	const load = lit(t, T.load);
	cards.forEach((c, i) => {
		const move = ramp(t, c.at - LEAD, 0.55);
		const x = 420 + i * 380 + (c.x - 420 - i * 380) * move;
		const y = 250 + 220 * move;
		const fill = Math.min(1, lit(t, c.at, T.read) + load);
		b.path(i === 0 ? 'task' : 'task-flow', interpolatePath(move, rectPath(420 + i * 380, 250, 360, 110), rectPath(x, y, 360, 110, 24)), {fill: mixc(fill, C.surface, C.focus), stroke: C.focus, sw: 2 * routed, opacity: move > 0 ? 1 : 0});
		// 名稱隨拆出的規則一起移動；離開共通區塊後才淡入，避免和區塊內文字重疊。
		b.text(`rule-${i}-label`, x + 24, y + 68, c.label, 34, {fill: fill > 0.5 ? C.onFocus : C.ink, opacity: ramp(t, c.at - LEAD + 0.25, 0.1)});
	});
	// 任務晶片：先從左側進來讀共通判準，再分成規劃與審查。
	const enter = ramp(t, T.read - LEAD, 0.9);
	const split2 = ramp(t, T.route - LEAD, 0.8);
	const p = pointOn('M 200 760 L 300 760 L 300 305 L 330 305', enter);
	b.group(ramp(t, T.read - LEAD, 0.2) * (1 - (split2 > 0 ? 1 : 0)), () => {
		b.rect('task-chip', p.x - 80, p.y - 24, 160, 48, {fill: C.focus});
		b.text('task-chip-label', p.x - 30, p.y + 9, '任務', 26, {fill: C.onFocus});
	});
	const tasks = [{label: '規劃任務', to: 600, route: 'M 330 305 L 300 305 L 300 646 L 600 646'}, {label: '審查任務', to: 1000, route: 'M 330 305 L 300 305 L 300 646 L 1000 646'}];
	tasks.forEach((task, i) => {
		const q = pointOn(task.route, split2);
		b.group(split2 > 0 ? 1 : 0, () => {
			b.rect(`task-${i}`, q.x - 90, q.y - 24, 180, 48, {fill: C.focus});
			b.text(`task-${i}-label`, q.x - 52, q.y + 9, task.label, 26, {fill: C.onFocus});
		});
	});
	// 載入：規劃只接變更規劃；審查接變更規劃與工作流程評估兩份。
	const links = ramp(t, T.review - LEAD, 0.6);
	b.path('load-plan', 'M 600 622 V 580', {stroke: C.focus, sw: 4, draw: ramp(t, T.route + 0.5, 0.4), opacity: split2 >= 1 ? 1 : 0});
	b.path('load-review', 'M 1000 622 V 580 M 960 622 L 760 580', {stroke: C.focus, sw: 4, draw: links, opacity: links > 0 ? 1 : 0});
	return FULL;
};

// ── 06 雙鑽石：三類判斷逐一從主檔抽出成直立規則檔；推近主檔看流程步驟，回全景時由步驟接回各規則。 ──
const s06 = (b: Builder, t: number): Camera => {
	header(b, 'CASE 03 / 分開的是規則責任', '雙鑽石：流程與三類判斷各有位置');
	const T = {sop: at('06', '雙鑽石'), rule: [at('06', '模型判準'), at('06', '任務分流'), at('06', '需求分析')], flow: at('06', '主檔負責帶流程'), judge: at('06', '各類判斷'), mixed: at('06', '避免全部混寫')};
	const cam: Camera = {
		// 推近等第三份規則（需求分析）講完才開始，避免當下主焦點被推出畫面。
		cx: track(t, [[0, 800], [T.flow - OUT, 270], [T.judge - LEAD, 800]], 0.7),
		cy: track(t, [[0, 450], [T.flow - OUT, 425], [T.judge - LEAD, 450]], 0.7),
		s: track(t, [[0, 1], [T.flow - OUT, 1.3], [T.judge - LEAD, 1]], 0.7),
	};
	const sop = lit(t, T.sop, T.rule[0]) + lit(t, T.flow, T.judge);
	const judge = lit(t, T.judge);
	b.on('sop', sop);
	b.on('rules', judge);
	b.rect('sop', 90, 250, 420, 470, {fill: C.surface, stroke: C.focus, sw: 3 * Math.min(1, sop)});
	b.text('sop-title', 120, 330, 'SOP', 72, {fill: mixc(Math.min(1, sop), C.ink, C.focus)});
	b.text('sop-sub', 120, 380, '主檔帶流程', 30, {weight: 400});
	const names = ['模型判準', '任務分流', '需求分析'];
	names.forEach((name, i) => {
		const value = Math.min(1, lit(t, T.rule[i], T.rule[i + 1] ?? T.flow) + judge);
		b.on(`rule${i}`, value);
		const from = {x: 115, y: 420 + i * 60, w: 370, h: 46};
		const to = {x: 600 + i * 300, y: 280, w: 270, h: 410};
		const move = ramp(t, T.rule[i] - LEAD, 0.55);
		const p = pointOn(`M ${from.x + from.w / 2} ${from.y + from.h / 2} C ${from.x + 500} ${from.y}, ${to.x + to.w / 2} ${to.y + 40}, ${to.x + to.w / 2} ${to.y + to.h / 2}`, move);
		const w = from.w + (to.w - from.w) * move;
		const h = from.h + (to.h - from.h) * move;
		b.path(`rule${i}`, interpolatePath(move, rectPath(p.x - from.w / 2, p.y - from.h / 2, from.w, from.h), rectPath(p.x - w / 2, p.y - h / 2, w, h, 30)), {fill: mixc(move > 0 && move < 1 ? 1 : 0, C.surface, C.focus), stroke: C.focus, sw: 3 * value});
		const start = T.rule[i] - LEAD;
		const flying = move > 0 && move < 1;
		b.text(`rule${i}-mixed`, from.x + 18, from.y + 32, name, 28, {weight: 400, fill: C.muted, opacity: 1 - ramp(t, start, 0.1)});
		// 名稱隨飛行中的規則檔移動（焦點色上用深色字），到位後停在原標題位置，再補分隔線與副標。
		b.text(`rule${i}-label`, p.x - w / 2 + 20 + 5 * move, p.y + 12 - 32 * move, name, 28 + 11 * move, {fill: flying ? C.onFocus : mixc(value, C.ink, C.focus), opacity: ramp(t, start + 0.1, 0.1)});
		b.group(ramp(t, start + 0.55, 0.2), () => {
			b.path(`rule${i}-rule`, `M ${to.x + 25} 360 L ${to.x + 245} 360`, {stroke: C.line, sw: 2});
			b.text(`rule${i}-sub`, to.x + 25, 625, '獨立規則', 29, {weight: 400, fill: C.muted});
		});
	});
	// 主檔帶流程：三個步驟在推近時出現，一個標記沿步驟往下走。
	const steps = ramp(t, T.flow - LEAD, 0.4);
	b.group(steps, () => {
		['步驟 1', '步驟 2', '步驟 3'].forEach((s, i) => b.text(`flow-${i}`, 150, 470 + i * 70, s, 30, {weight: 400}));
		const y = 460 + 140 * ramp(t, T.flow + 0.3, 1.2);
		b.rect('flow-marker', 116, y - 12, 20, 20, {fill: C.focus});
	});
	// 各類判斷回到各自的規則檔：步驟接到三份規則。
	const links = ramp(t, T.judge - LEAD + 0.3, 0.9);
	// 由步驟往上走到規則檔上方的各自通道，再從上方進入各自的規則檔，不穿過其他規則檔。
	b.path('rules', 'M 330 460 C 540 460, 540 264, 600 264 L 735 264 L 735 280 M 330 530 C 556 530, 556 252, 640 252 L 1035 252 L 1035 280 M 330 600 C 572 600, 572 240, 680 240 L 1335 240 L 1335 280', {stroke: C.focus, sw: 3, dash: '10 8', draw: links, opacity: links > 0 ? 1 : 0});
	// 頁尾在推近前先退場，回全景後再出現，不會被鏡頭切成半截。
	const footer = (1 - ramp(t, T.flow - OUT - 0.15, 0.15)) + ramp(t, T.judge - LEAD + 0.7, 0.3);
	b.text('footer', 90, 825, '這是檔案責任的分離；不是把雙鑽石模型改成固定階段。', 29, {weight: 400, fill: C.muted, opacity: Math.min(1, footer)});
	return cam;
};

// ── 08 收束：三列分工全程可讀；一個標記沿左側脈絡依旁白往下走，三支案例共用同一條方法線。 ──
const s08 = (b: Builder, t: number): Camera => {
	b.cam = false;
	b.text('title', 90, 160, '各自的用途，同一套整理方法', 65);
	b.cam = true;
	const T = {keep: at('08', '三支技能保留'), share: at('08', '共用同一套'), flow: [at('08', '技能工程安排工作'), at('08', '基礎技能分工完成'), at('08', '流程負責')]};
	const rows = [['Engineering', '安排工作'], ['Form ＋ Deriver', '分工完成'], ['SOP', '在對的時機使用規則']];
	const Y = [290, 450, 610];
	rows.forEach(([left, right], i) => {
		const value = lit(t, T.flow[i], T.flow[i + 1] ?? Infinity);
		b.on(`v${i}`, true);
		b.on(`flow${i}`, value);
		b.text(`v${i}`, 90, Y[i], left, 52);
		b.path(`v${i}-link`, `M650 ${Y[i] - 15} L760 ${Y[i] - 15}`, {stroke: mixc(value, C.line, C.focus), sw: 2 + value * 2});
		b.text(`flow${i}`, 800, Y[i], right, 50, {fill: mixc(value, C.ink, C.focus)});
	});
	const marker = ramp(t, T.flow[0] - LEAD, 0.3);
	const y = track(t, [[0, Y[0] - 15], [T.flow[1] - LEAD, Y[1] - 15], [T.flow[2] - LEAD, Y[2] - 15]], 0.5);
	b.path('spine', `M 62 ${Y[0] - 15} L 62 ${Y[2] - 15}`, {stroke: C.line, sw: 2, opacity: ramp(t, T.share - LEAD, 0.4)});
	b.rect('spine-marker', 52, y - 10, 20, 20, {fill: C.focus, opacity: marker});
	const share = ramp(t, T.share - LEAD, 1.0);
	b.path('method-line', 'M90 735 L1510 735', {stroke: C.line, sw: 2});
	b.path('method-line-lit', 'M90 735 L1510 735', {stroke: C.focus, sw: 3, draw: share, opacity: share > 0 ? 1 - ramp(t, T.flow[0] - LEAD, 0.4) * 0.7 : 0});
	b.group(ramp(t, T.keep - LEAD, 0.4), () => b.text('cases', 90, 810, '慣例式提交　／　主幹式開發　／　雙鑽石', 36, {weight: 400, fill: C.muted}));
	return FULL;
};

const BUILD: Record<SceneId, (b: Builder, t: number) => Camera> = {'00': s00, '01': s01, '02': s02, '03': s03, '07': s07, '04': s04, '05': s05, '06': s06, '08': s08};

/** Remotion 繪製用：完整顯示清單。 */
export const sceneState = (id: SceneId, t: number): SceneState => {
	const b = new Builder();
	const camera = BUILD[id](b, t);
	return {scene: id, t, camera, items: b.items, active: [...b.active].sort()};
};

/** 鏡頭換算：world（場景設計座標）→ 套用鏡頭後的 1600×900 設計座標；固定標題列不受鏡頭影響。 */
const applyCamera = (box: Box, cam: Camera | null): Box => {
	const c = cam ?? FULL;
	return {x: 800 + (box.x - c.cx) * c.s, y: 450 + (box.y - c.cy) * c.s, w: box.w * c.s, h: box.h * c.s};
};
/** 設計座標 → 成片像素：內容框等比 1422/1600、左移 89；底部 100px 為字幕帶。 */
const toFrame = (box: Box): Box => {
	const k = 1422 / 1600;
	return {x: 89 + box.x * k, y: box.y * k, w: box.w * k, h: box.h * k};
};

/**
 * 逐影格 QA 用：與繪製相同的狀態。visible 只列不透明度大於 0.01、且在可見區內的物件；
 * x／y／w／h 為已套鏡頭的 1600×900 設計座標（鏡頭內物件裁在標題線 y=215 下方），
 * frame 為對應的成片像素框，world 為套鏡頭前的場景座標。text 的框為字寬估算。
 */
export const getMotionState = (id: SceneId, t: number) => {
	const st = sceneState(id, t);
	const r = (v: number) => Math.round(v * 10) / 10;
	const round = (b: Box) => ({x: r(b.x), y: r(b.y), w: r(b.w), h: r(b.h)});
	const visible = st.items.flatMap((it) => {
		if (it.opacity <= 0.01 || (it.kind === 'path' && it.draw === 0)) return [];
		const world = it.kind === 'text'
			? {x: (it as Item & {bx: number}).bx, y: it.y - (it.size ?? 0) * 0.88, w: it.w, h: it.h}
			: {x: it.x, y: it.y, w: it.w, h: it.h};
		const s = applyCamera(world, it.cam ? st.camera : null);
		const x1 = Math.max(s.x, 0), x2 = Math.min(s.x + s.w, 1600);
		const y1 = Math.max(s.y, it.cam ? 215 : 0), y2 = Math.min(s.y + s.h, 900);
		if (x2 <= x1 || y2 < y1) return [];
		const box = {x: x1, y: y1, w: x2 - x1, h: y2 - y1};
		// projected：套鏡頭後、裁切前的完整框；cropped：可見框比完整框小（被畫面邊或標題線裁到）。
		const cropped = x1 > s.x + 0.5 || x2 < s.x + s.w - 0.5 || y1 > s.y + 0.5 || y2 < s.y + s.h - 0.5;
		return [{id: it.id, kind: it.kind, ...round(box), opacity: Math.round(it.opacity * 1000) / 1000,
			projected: round(s), cropped, frame: round(toFrame(box)), world: round(world), camera: it.cam,
			...(it.text ? {text: it.text} : {}), ...(it.fill && it.fill !== 'none' ? {fill: it.fill} : {}), ...(it.stroke && (it.sw ?? 0) > 0 ? {stroke: it.stroke} : {})}];
	});
	return {scene: id, t: Math.round(t * 1000) / 1000, camera: st.camera, active: st.active, visible};
};

/** 依影片絕對秒數找所在場景（end 不含）。 */
export const sceneAt = (t: number): SceneId => {
	for (const id of SCENES) {
		const s = segment(id);
		if (t >= s.start && t < s.end) return id;
	}
	return SCENES[SCENES.length - 1];
};
