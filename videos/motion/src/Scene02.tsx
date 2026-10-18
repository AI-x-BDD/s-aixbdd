import React from 'react';
import {at, C, FocusText, Header, mix, ramp, Stage, Text, track, useTime, type Variant} from './lib';

// scene02：五個 Form 部位與三種 Deriver 抽取。時間全部取自旁白字元對齊。
const LABELS = ['用途說明', '執行流程', '規則', '樣板', '腳本'];
const DETAILS = ['何時使用這支 Skill？', '實際執行哪些步驟？', '判斷依據與正反例', '輸出骨架與完成範例', '輸入、輸出與執行方式'];
const TILE = {y: 330, w: 260, h: 112, x: (i: number) => 90 + i * 290};
const DERIVE = {y: 610, w: 400, h: 86, x: [90, 585, 1080]};
const LEAD = 0.12; // 動作在片語起點前 0.12 秒開始；到位時間另依各動作長度而定
const SWAP = 0.14; // 同位置換字：先淡出、再淡入，任何時刻只有一份文字

const times = () => {
	const enumerate = LABELS.map((w) => at('02', w));
	const detail = ['用途說明讓', 'SOP 寫清楚', '規則附', '樣板提供', '腳本則'].map((p) => at('02', p));
	const extract = [at('02', '規則、樣板或'), at('02', '樣板或腳本'), at('02', '腳本從流程')];
	return {overview: at('02', '先看兩種分工'), form: at('02', '一組是格式把關'), enumerate, detail, derive: at('02', '另一組是部位抽取'), extract};
};

/** 依序出現的文字：在 start 淡入；若有下一段，在 next 前完整淡出，與下一段不重疊。 */
const shown = (t: number, start: number, next?: number) =>
	ramp(t, start + SWAP, SWAP) * (next === undefined ? 1 : 1 - ramp(t, next, SWAP));

const Slots: React.FC<{opacity: number}> = ({opacity}) => (
	<g opacity={opacity}>
		{LABELS.map((_, i) => (
			<rect key={i} x={TILE.x(i) + 1.5} y={TILE.y + 1.5} width={TILE.w - 3} height={TILE.h - 3} fill="none" stroke={C.line} strokeWidth={3} strokeDasharray="10 8" />
		))}
	</g>
);

// ── M1 連續焦點：版面固定；一個焦點色塊沿解說連續滑動，部位逐詞揭露，無鏡頭、無形變。 ──
const Focus: React.FC = () => {
	const t = useTime('02');
	const T = times();
	const fx = track(t, [[0, TILE.x(0)], ...T.enumerate.map((s, i): [number, number] => [s - LEAD, TILE.x(i)]), ...T.detail.map((s, i): [number, number] => [s - LEAD, TILE.x(i)]), ...T.extract.map((s, i): [number, number] => [s - LEAD, DERIVE.x[i]])]);
	const down = (a: number, b: number) => track(t, [[0, a], [T.extract[0] - LEAD, b]]);
	const focus = {
		x: fx, y: down(TILE.y, DERIVE.y), w: down(TILE.w, DERIVE.w), h: down(TILE.h, DERIVE.h),
		on: ramp(t, T.enumerate[0] - LEAD, 0.2) * (1 - ramp(t, T.derive - LEAD, 0.25)) + ramp(t, T.extract[0] - LEAD, 0.2),
	};
	const derive = ramp(t, T.derive - LEAD, 0.3);
	const nexts = [...T.detail.slice(1), T.derive].map((s) => s - LEAD);
	return (
		<Stage id="02">
			<Header eyebrow="FORM × 5  /  DERIVER × 3" title="兩種分工，處理不同問題" />
			<g opacity={shown(t, T.overview - LEAD, T.form - LEAD)}>
				<Text x={90} y={545} size={52}>格式把關 × 5　／　部位抽取 × 3</Text>
			</g>
			<g opacity={ramp(t, T.form - LEAD, 0.25)}>
				<Text x={90} y={290} size={36} fill={mix(t, T.derive - LEAD, 0.3, C.focus, C.ink)}>FORM：把關各部位格式</Text>
			</g>
			<Slots opacity={ramp(t, T.form - LEAD, 0.25)} />
			{LABELS.map((_, i) => (
				<rect key={i} x={TILE.x(i)} y={TILE.y} width={TILE.w} height={TILE.h} fill={C.surface} opacity={ramp(t, T.enumerate[i] - LEAD, 0.25)} />
			))}
			<g opacity={derive}>
				<Text x={90} y={540} size={48} fill={C.focus}>DERIVER：從流程分出部位</Text>
				{DERIVE.x.map((x) => <rect key={x} x={x} y={DERIVE.y} width={DERIVE.w} height={DERIVE.h} fill={C.surface} />)}
			</g>
			<rect x={focus.x} y={focus.y} width={focus.w} height={focus.h} fill={C.focus} opacity={focus.on} />
			<FocusText id="s02-focus-text" focus={focus} render={(color) => (
				<>
					{LABELS.map((label, i) => (
						<Text key={label} x={TILE.x(i) + 25} y={TILE.y + 68} size={34} fill={color} opacity={ramp(t, T.enumerate[i] - LEAD, 0.25)}>{label}</Text>
					))}
					{['規則抽取', '樣板抽取', '腳本抽取'].map((label, i) => (
						<Text key={label} x={DERIVE.x[i] + 25} y={DERIVE.y + 55} size={34} fill={color} opacity={derive}>{label}</Text>
					))}
				</>
			)} />
			{DETAILS.map((d, i) => (
				<g key={d} opacity={shown(t, T.detail[i] - LEAD, nexts[i])}>
					<Text x={100} y={545} size={56} fill={C.focus}>{LABELS[i]}：{d}</Text>
				</g>
			))}
			<Text x={90} y={805} size={32} weight={400} fill={C.muted}>五個格式責任，三種抽取工作；兩組不是同一套分類。</Text>
		</Stage>
	);
};

// M1 連續焦點（代表片段比較用）；M2 動態敘事改由 motion-state.ts＋Motion.tsx 繪製，與全片同一程式。
export const Scene02: React.FC<{variant: Variant}> = () => <Focus />;
