import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {evolvePath} from '@remotion/paths';
import {AudioEnabled, Camera, FONT, SEG, Stage} from './lib';
import {SCENES, sceneState, type Item, type SceneId} from './motion-state.ts';

// 動態敘事的繪製層：逐項畫出 motion-state 的顯示清單，不自行計算任何幾何或時間。

const Shape: React.FC<{it: Item; uid: string}> = ({it, uid}) => {
	const common = {opacity: it.opacity, fill: it.fill ?? 'none', stroke: it.stroke, strokeWidth: it.sw, strokeDasharray: it.dash};
	if (it.kind === 'rect') return <rect x={it.x} y={it.y} width={Math.max(0, it.w)} height={Math.max(0, it.h)} {...common} />;
	if (it.kind === 'text') {
		return (
			<text x={it.x} y={it.y} fontFamily={FONT} fontSize={it.size} fontWeight={it.weight} fill={it.fill} opacity={it.opacity} textAnchor={it.anchor} letterSpacing={it.spacing}>
				{it.text}
			</text>
		);
	}
	if (it.draw === undefined || it.draw >= 1) return <path d={it.d} {...common} />;
	// 依進度描出：實線直接用 dash 偏移；虛線以實線描出的遮罩露出，保留虛線樣式。
	const evolved = evolvePath(it.draw, it.d as string);
	if (!it.dash) return <path d={it.d} {...common} strokeDasharray={evolved.strokeDasharray} strokeDashoffset={evolved.strokeDashoffset} />;
	return (
		<>
			<mask id={uid} maskUnits="userSpaceOnUse" x={0} y={0} width={1600} height={900}>
				<path d={it.d} fill="none" stroke="#fff" strokeWidth={(it.sw ?? 2) + 6} strokeDasharray={evolved.strokeDasharray} strokeDashoffset={evolved.strokeDashoffset} />
			</mask>
			<path d={it.d} {...common} mask={`url(#${uid})`} />
		</>
	);
};

export const SceneView: React.FC<{id: SceneId}> = ({id}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const st = sceneState(id, SEG[id].start + frame / fps);
	const fixed = st.items.filter((it) => !it.cam);
	const moving = st.items.filter((it) => it.cam);
	return (
		<Stage id={id}>
			<Camera id={`s${id}`} {...st.camera}>
				{moving.map((it, i) => <Shape key={`${it.id}-${i}`} it={it} uid={`m${id}-${i}`} />)}
			</Camera>
			{fixed.map((it, i) => <Shape key={`${it.id}-${i}`} it={it} uid={`f${id}-${i}`} />)}
		</Stage>
	);
};

/** 全片：九幕依各自起訖排成 Sequence；只出畫面，原音由建置流程最後封裝。 */
export const FullMotion: React.FC = () => {
	const {fps} = useVideoConfig();
	return (
		<AudioEnabled.Provider value={false}>
			<AbsoluteFill>
				{SCENES.map((id) => (
					<Sequence key={id} name={`scene${id}`} from={Math.round(SEG[id].start * fps)} durationInFrames={Math.round((SEG[id].end - SEG[id].start) * fps)}>
						<SceneView id={id} />
					</Sequence>
				))}
			</AbsoluteFill>
		</AudioEnabled.Provider>
	);
};
