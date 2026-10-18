import React from 'react';
import {Composition} from 'remotion';
import {FullMotion, SceneView} from './Motion';
import {Scene02} from './Scene02';
import {Scene07} from './Scene07';
import {segmentFrames} from './lib';

// 全片動態敘事（只出畫面，2825 影格＝113 秒）；代表片段比較保留 M1 連續焦點，M2 與全片共用同一份 motion-state。
export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="Full-Motion" component={FullMotion} durationInFrames={2825} fps={25} width={1600} height={900} />
		<Composition id="S02-focus" component={Scene02} durationInFrames={segmentFrames('02')} fps={25} width={1600} height={900} defaultProps={{variant: 'focus' as const}} />
		<Composition id="S02-motion" component={SceneView} durationInFrames={segmentFrames('02')} fps={25} width={1600} height={900} defaultProps={{id: '02' as const}} />
		<Composition id="S07-focus" component={Scene07} durationInFrames={segmentFrames('07')} fps={25} width={1600} height={900} defaultProps={{variant: 'focus' as const}} />
		<Composition id="S07-motion" component={SceneView} durationInFrames={segmentFrames('07')} fps={25} width={1600} height={900} defaultProps={{id: '07' as const}} />
	</>
);
