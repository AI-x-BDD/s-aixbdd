import React from 'react';
import {evolvePath} from '@remotion/paths';
import {at, C, FocusText, Header, ramp, Stage, Text, track, useTime, type Variant} from './lib';

// scene07：規則需求從 SOP 出發，經 derive-rule、form-rule 成為規則檔，再由 form-sop 接回讀取時機。
const LEAD = 0.12;
const times = () => ({
	step: at('07', '例如'),
	need: at('07', '判斷規則'),
	give: at('07', '就交給規則抽取技能'),
	write: at('07', '它請格式技能'),
	file: at('07', '寫好規則檔'),
	back: at('07', '再更新流程'),
	read: at('07', '交代何時讀'),
	branches: at('07', '需要固定輸出'),
	existing: at('07', '既有檔案只改內容'),
	direct: at('07', '直接交給格式技能'),
});

/** 依進度描出路徑；箭頭在描完後出現，方向即流程方向。 */
const Drawn: React.FC<{d: string; progress: number; width?: number; arrow?: string}> = ({d, progress, width = 7, arrow}) => {
	const evolved = evolvePath(progress, d);
	return (
		<>
			<path d={d} fill="none" stroke={C.focus} strokeWidth={width} strokeDasharray={evolved.strokeDasharray} strokeDashoffset={evolved.strokeDashoffset} opacity={progress > 0 ? 1 : 0} />
			{arrow && <path d={arrow} fill="none" stroke={C.focus} strokeWidth={5} opacity={ramp(progress, 0.92, 0.08)} />}
		</>
	);
};

// ── M1 連續焦點：沿用正式 B 版面；焦點色塊依旁白從 SOP 滑到抽取、寫規則，回接線依方向描回 SOP。 ──
const BOX = {step: {x: 90, w: 410}, extract: {x: 590, w: 390}, write: {x: 1070, w: 440}};
const Focus: React.FC = () => {
	const t = useTime('07');
	const T = times();
	const keys = (pick: (b: {x: number; w: number}) => number): [number, number][] =>
		[[0, pick(BOX.step)], [T.give - LEAD, pick(BOX.extract)], [T.write - LEAD, pick(BOX.write)], [T.back + 0.95, pick(BOX.step)]];
	const focus = {x: track(t, keys((b) => b.x)), y: 290, w: track(t, keys((b) => b.w)), h: 115, on: ramp(t, T.step - 0.2, 0.2)};
	const writeOn = ramp(t, T.write - LEAD, 0.25);
	const back = ramp(t, T.back - LEAD, 1.0);
	return (
		<Stage id="07">
			<Header eyebrow="EXTRACTION / 產出檔案只是其中一步" title="拆出規則，也要接回讀取時機" />
			<rect x={90} y={290} width={410} height={115} fill={C.surface} />
			<path d="M500 350 L590 350" stroke={C.line} strokeWidth={2} />
			<rect x={590} y={290} width={390} height={115} fill={C.surface} />
			<g opacity={writeOn}>
				<path d="M980 350 L1070 350" stroke={C.line} strokeWidth={2} />
				<rect x={1070} y={290} width={440} height={115} fill={C.surface} />
			</g>
			<rect x={focus.x} y={focus.y} width={focus.w} height={focus.h} fill={C.focus} opacity={focus.on} />
			<FocusText id="s07-focus-text" focus={focus} render={(color) => (
				<>
					<Text x={115} y={359.5} size={34} fill={color}>SOP：需要更多規則</Text>
					<Text x={615} y={359.5} size={34} fill={color}>derive-rule</Text>
					<Text x={1095} y={359.5} size={34} fill={color} opacity={writeOn}>form-rule 寫規則</Text>
				</>
			)} />
			<Drawn d="M1290 405 V625 H295 V405" progress={back} arrow="M283 425 L295 405 L307 425" />
			<g opacity={ramp(t, T.read - LEAD, 0.3)}>
				<rect x={590} y={535} width={580} height={120} fill={C.surface} />
				<Text x={625} y={610} size={38} fill={C.focus}>form-sop：接回讀取時機</Text>
			</g>
			<g opacity={ramp(t, T.branches - LEAD, 0.3)}>
				<Text x={90} y={795} size={30} weight={400} fill={C.muted}>需要固定輸出 → 抽取樣板　／　需要自動處理 → 抽取腳本</Text>
			</g>
			<g opacity={ramp(t, T.existing - LEAD, 0.3)}>
				<Text x={90} y={850} size={30} fill={C.focus}>既有檔案只改內容 → 直接交給 Form</Text>
			</g>
		</Stage>
	);
};

// M1 連續焦點（代表片段比較用）；M2 動態敘事改由 motion-state.ts＋Motion.tsx 繪製，與全片同一程式。
export const Scene07: React.FC<{variant: Variant}> = () => <Focus />;
