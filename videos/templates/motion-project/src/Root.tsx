import React from 'react';
import {AbsoluteFill, Composition, useCurrentFrame, useVideoConfig} from 'remotion';
import props from '../public/render-props.json';
import stateData from '../public/state.json';

type StateItem = {
	id: string;
	text?: string;
	x?: number;
	y?: number;
	w?: number;
	h?: number;
	opacity?: number;
	fill?: string;
};

type FrameState = {frame: number; t?: number; active?: string[]; visible?: StateItem[]; items?: StateItem[]};

const frames = (stateData as {frames: FrameState[]}).frames ?? [];

const currentState = (frame: number): FrameState => {
	let value = frames[0] ?? {frame: 0, visible: []};
	for (const candidate of frames) {
		if (candidate.frame > frame) break;
		value = candidate;
	}
	return value;
};

const Scene: React.FC = () => {
	const frame = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const state = currentState(frame);
	const visible = state.visible ?? state.items ?? [];
	const active = new Set(state.active ?? []);
	return (
		<AbsoluteFill style={{background: props.background ?? '#000000', color: props.foreground ?? '#ffffff', fontFamily: 'Arial, sans-serif'}}>
			{visible.map((item) => (
				<div key={item.id} style={{position: 'absolute', left: item.x ?? width * 0.1, top: item.y ?? height * 0.35, width: item.w ?? width * 0.8, height: item.h ?? height * 0.2, opacity: item.opacity ?? 1, background: item.fill ?? 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: Math.max(16, Math.round(height * 0.07)), color: props.foreground ?? '#ffffff'}}>
					<div style={{fontWeight: active.has(item.id) ? 700 : 400, border: active.has(item.id) ? `3px solid ${props.focus ?? 'currentColor'}` : '0', padding: active.has(item.id) ? 8 : 0}}>{item.text ?? item.id}</div>
				</div>
			))}
		</AbsoluteFill>
	);
};

export const RemotionRoot: React.FC = () => (
	<Composition id={props.composition ?? 'Main'} component={Scene} durationInFrames={props.frameCount} fps={props.fps} width={props.width} height={props.height} />
);
