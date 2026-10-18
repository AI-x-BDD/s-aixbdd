import React from 'react';
import {AbsoluteFill, Easing, interpolate, interpolateColors, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {getLength, getPointAtLength} from '@remotion/paths';
import segments from '../public/segments.json';
import {setSegments, type SceneId, type Segment} from './motion-state.ts';

// 正式 B「深色系統路由」色彩角色；動態候選只改動態語言，不換配色。
export const C = {
	bg: '#201D31',
	surface: '#373249',
	ink: '#F4F0FF',
	muted: '#C4BDD5',
	focus: '#D8EF8A',
	onFocus: '#201D31',
	line: '#847B97',
};
export const FONT = 'PingFang TC';
export type {SceneId};
export type Variant = 'focus' | 'motion';
export const SEG = segments as unknown as Record<SceneId, Segment>;
setSegments(SEG);

/** 全片合成只要畫面，原音由建置流程最後封裝；單段樣片才帶聲音。 */
export const AudioEnabled = React.createContext(true);
export const segmentFrames = (id: SceneId, fps = 25) => Math.round((SEG[id].end - SEG[id].start) * fps);

const EASE = Easing.bezier(0.33, 0, 0.2, 1);

/** 旁白片語開始的影片絕對秒數；nth 指第幾次出現，shift 指片語內第幾個字。 */
export const at = (id: SceneId, phrase: string, nth = 0, shift = 0) => {
	const {text, chars} = SEG[id];
	let index = -1;
	for (let i = 0; i <= nth; i++) {
		index = text.indexOf(phrase, index + 1);
		if (index < 0) throw new Error(`旁白找不到「${phrase}」`);
	}
	const hit = chars.find(([offset]) => offset >= index + shift);
	if (!hit) throw new Error(`「${phrase}」沒有字元時間`);
	return hit[1];
};

/** 目前畫格對應的影片絕對秒數，所有動畫都以旁白詞時間為錨。 */
export const useTime = (id: SceneId) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return SEG[id].start + frame / fps;
};

export const ramp = (t: number, t0: number, d: number, a = 0, b = 1) =>
	interpolate(t, [t0, t0 + d], [a, b], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE});

/** 關鍵影格：在每個時間點開始，以 d 秒緩動到新值，其餘時間靜止。 */
export const track = (t: number, keys: [number, number][], d = 0.45) => {
	let value = keys[0][1];
	for (const [time, next] of keys.slice(1)) {
		value = value + (next - value) * ramp(t, time, d);
	}
	return value;
};

/** 路徑上某進度的座標；@remotion/paths 對空路徑回傳 null，此處路徑固定不為空。 */
export const pointOn = (d: string, progress: number) => {
	const p = getPointAtLength(d, getLength(d) * progress);
	if (!p) throw new Error(`路徑無法取點：${d}`);
	return p;
};

export const mix = (t: number, t0: number, d: number, a: string, b: string) =>
	interpolateColors(ramp(t, t0, d), [0, 1], [a, b]);

export const Text: React.FC<{x: number; y: number; size: number; weight?: number; fill?: string; opacity?: number; anchor?: 'start' | 'middle' | 'end'; spacing?: number; children: React.ReactNode}> = ({x, y, size, weight = 600, fill = C.ink, opacity = 1, anchor = 'start', spacing, children}) => (
	<text x={x} y={y} fontFamily={FONT} fontSize={size} fontWeight={weight} fill={fill} opacity={opacity} textAnchor={anchor} letterSpacing={spacing}>
		{children}
	</text>
);

export const Header: React.FC<{eyebrow: string; title: string}> = ({eyebrow, title}) => (
	<>
		<Text x={90} y={85} size={24} fill={C.muted} spacing={3}>{eyebrow}</Text>
		<Text x={90} y={168} size={58}>{title}</Text>
		<path d="M90 205 L1510 205" stroke={C.line} strokeWidth={2} />
	</>
);

/**
 * 二維鏡頭：以設計座標 (cx, cy) 為畫面中心、縮放 s。標題列固定在鏡頭外，
 * 鏡頭內容裁在標題線下方，推近時不會出現半截標題或內容壓到標題。
 */
export const Camera: React.FC<{id: string; cx: number; cy: number; s: number; children: React.ReactNode}> = ({id, cx, cy, s, children}) => (
	<>
		<clipPath id={`${id}-camera`}>
			<rect x={0} y={215} width={1600} height={685} />
		</clipPath>
		<g clipPath={`url(#${id}-camera)`}>
			<g transform={`translate(800 450) scale(${s}) translate(${-cx} ${-cy})`}>{children}</g>
		</g>
	</>
);

/**
 * 焦點色塊上的文字：底層一律淺色字，再疊一份裁在色塊範圍內的深色字。
 * 色塊移動途中，壓在色塊上的部分是深字、其餘仍是淺字，任何時刻都可讀。
 */
export const FocusText: React.FC<{id: string; focus: {x: number; y: number; w: number; h: number; on: number}; render: (color: string) => React.ReactNode}> = ({id, focus, render}) => (
	<>
		<g>{render(C.ink)}</g>
		<clipPath id={id}>
			<rect x={focus.x} y={focus.y} width={focus.w} height={focus.h} />
		</clipPath>
		<g clipPath={`url(#${id})`} opacity={focus.on}>
			{render(C.onFocus)}
		</g>
	</>
);

/**
 * 與正式 B 燒錄版相同的畫面配置：1600×900 圖解等比縮進 1422×800 內容框，
 * 底部 100px 字幕帶以同字級、同斷行顯示 SRT；聲音直接取正式旁白的同一段。
 */
export const Stage: React.FC<{id: SceneId; children: React.ReactNode}> = ({id, children}) => {
	const {fps} = useVideoConfig();
	const withAudio = React.useContext(AudioEnabled);
	const t = useTime(id);
	const cue = SEG[id].cues.find((c) => t >= c.start && t < c.end);
	const lines = cue?.lines ?? [];
	const baselines = lines.length === 1 ? [65] : [40, 84];
	return (
		<AbsoluteFill style={{backgroundColor: C.bg}}>
			<svg style={{position: 'absolute', left: 89, top: 0}} width={1422} height={800} viewBox="0 0 1600 900">
				<rect width={1600} height={900} fill={C.bg} />
				{children}
			</svg>
			<svg style={{position: 'absolute', left: 0, top: 800}} width={1600} height={100} viewBox="0 0 1600 100">
				{lines.map((line, i) => (
					<Text key={i} x={800} y={baselines[i]} size={36} weight={500} anchor="middle">{line}</Text>
				))}
			</svg>
			{withAudio && <Audio src={staticFile('正式旁白.m4a')} trimBefore={Math.round(SEG[id].start * fps)} />}
		</AbsoluteFill>
	);
};
