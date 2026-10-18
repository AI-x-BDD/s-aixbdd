import React from 'react';
import {AbsoluteFill, Composition, useCurrentFrame} from 'remotion';
import props from '../public/render-props.json';
import stateData from '../public/state.json';

type StateItem = {id: string; text?: string; x?: number; y?: number; w?: number; h?: number; opacity?: number};
type FrameState = {frame: number; t?: number; scene?: string; active?: string[]; visible?: StateItem[]; items?: StateItem[]};
const frames = (stateData as {frames: FrameState[]}).frames ?? [];
const currentState = (frame: number): FrameState => {
	let value = frames[0] ?? {frame: 0, visible: []};
	for (const candidate of frames) { if (candidate.frame > frame) break; value = candidate; }
	return value;
};

const INK = '#20252A';
const PAPER = '#FFFDF8';
const MUTED = '#9A958B';
const ACCENT = '#E36B3F';
const TEAL = '#3C7770';

const Rail: React.FC<{activeStep: number}> = ({activeStep}) => <>
	<div style={{position: 'absolute', left: 50, right: 50, top: 42, height: 1, background: '#D7CFC1'}} />
	<div style={{position: 'absolute', left: 54, top: 53, color: ACCENT, fontSize: 15, letterSpacing: 3, fontWeight: 800}}>退款路徑 / REFUND PATH</div>
	<div style={{position: 'absolute', left: 50, top: 84, width: 1180, display: 'flex', justifyContent: 'space-between', color: INK, fontSize: 17, letterSpacing: 1}}>
		{['找原訂單', '交給審核人', '回接付款紀錄'].map((label, index) => <div key={label} style={{display: 'flex', alignItems: 'center', gap: 10, opacity: index === activeStep ? 1 : 0.45}}>
			<div style={{width: 24, height: 24, borderRadius: '50%', border: `2px solid ${index === activeStep ? ACCENT : INK}`, background: index === activeStep ? ACCENT : 'transparent', color: index === activeStep ? PAPER : INK, display: 'grid', placeItems: 'center', fontSize: 13, fontWeight: 800}}>{index + 1}</div><span>{label}</span>
		</div>)}
	</div>
	<svg width="1180" height="28" viewBox="0 0 1180 28" style={{position: 'absolute', left: 50, top: 122}}><path d="M12 14 H1168" stroke="#C6BBAA" strokeWidth="2" strokeDasharray="7 9" fill="none" /><circle cx="12" cy="14" r="5" fill={activeStep >= 0 ? ACCENT : '#C6BBAA'} /><circle cx="590" cy="14" r="5" fill={activeStep >= 1 ? ACCENT : '#C6BBAA'} /><circle cx="1168" cy="14" r="5" fill={activeStep >= 2 ? ACCENT : '#C6BBAA'} /></svg>
</>;

const FocusFrame: React.FC<{active: boolean; children: React.ReactNode; style?: React.CSSProperties}> = ({active, children, style}) => <div style={{position: 'absolute', border: active ? `3px solid ${ACCENT}` : '1px solid #C9C1B3', boxShadow: active ? `0 0 0 7px ${ACCENT}22` : 'none', ...style}}>{children}</div>;

const Item: React.FC<{item: StateItem; active: Set<string>; scene: string; t: number}> = ({item, active, scene, t}) => {
	const isActive = active.has(item.id);
	const retiringOpacity = scene === 'review-handoff' && (item.id === 'application-card' || item.id === 'reviewer') && t >= 12.38 ? Math.max(0, 1 - (t - 12.38) / 0.34) : 1;
	const stampOpacity = scene === 'review-handoff' && item.id === 'approval-stamp' && t > 12.72 ? Math.max(0, 1 - (t - 12.72) / 0.3) : 1;
	const ticketOpacity = scene === 'review-handoff' && item.id === 'refund-ticket' && t < 12.72 ? 0 : 1;
	const transitionOpacity = retiringOpacity * stampOpacity * ticketOpacity;
	const base: React.CSSProperties = {position: 'absolute', left: item.x ?? 0, top: item.y ?? 0, width: item.w ?? 100, height: item.h ?? 60, opacity: (item.opacity ?? 1) * transitionOpacity, color: INK, fontFamily: 'PingFang TC, Arial, sans-serif'};
	if (item.id === 'order-card' || item.id === 'application-card') return <FocusFrame active={isActive} style={{...base, background: PAPER, borderRadius: 3, padding: 18, overflow: 'hidden'}}><div style={{fontSize: 14, letterSpacing: 2, color: MUTED, fontWeight: 700}}>DOCUMENT / 退款流程</div><div style={{fontSize: 32, fontWeight: 800, marginTop: 13, letterSpacing: 2}}>{item.text}</div><div style={{position: 'absolute', left: 18, right: 18, bottom: 18, display: 'flex', gap: 7}}><i style={{height: 6, flex: 1, background: '#DED7CB'}} /><i style={{height: 6, flex: 0.5, background: '#DED7CB'}} /><i style={{height: 6, flex: 0.8, background: '#DED7CB'}} /></div></FocusFrame>;
	if (item.id === 'product-check' || item.id === 'reason-check') return <FocusFrame active={isActive} style={{...base, background: isActive ? '#FFF0E8' : '#EFE9DF', borderRadius: 5, padding: 16, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><span style={{fontSize: 26, fontWeight: 800}}>{item.text}</span></FocusFrame>;
	if (item.id === 'submit-button') return <FocusFrame active={isActive} style={{...base, background: isActive ? ACCENT : '#F2DDD4', borderColor: isActive ? ACCENT : '#D7B5A6', color: isActive ? PAPER : INK, borderRadius: 4, padding: 16, display: 'grid', placeItems: 'center'}}><span style={{fontSize: 24, fontWeight: 800}}>{item.text}</span></FocusFrame>;
	if (item.id === 'reviewer') return <FocusFrame active={isActive} style={{...base, background: '#E6EFEC', borderColor: isActive ? TEAL : '#AFC4BE', borderRadius: 90, display: 'grid', placeItems: 'center', padding: 18}}><div style={{textAlign: 'center'}}><div style={{fontSize: 46, lineHeight: 1, color: TEAL}}>◎</div><div style={{fontSize: 23, fontWeight: 800, marginTop: 6}}>{item.text}</div></div></FocusFrame>;
	if (item.id === 'approval-stamp') return <FocusFrame active={isActive} style={{...base, border: `3px dashed ${isActive ? ACCENT : '#B6A99A'}`, borderRadius: 6, display: 'grid', placeItems: 'center', background: '#FFF7EF'}}><span style={{fontSize: 24, color: ACCENT, fontWeight: 900, letterSpacing: 3}}>{item.text}</span></FocusFrame>;
	if (item.id === 'refund-ticket') { const morph = scene === 'review-handoff' ? Math.min(1, Math.max(0, (t - 12.72) / 1.08)) : 1; return <FocusFrame active={isActive} style={{...base, background: '#FFF0D9', borderColor: isActive ? ACCENT : '#D8B98E', borderRadius: 6 + morph * 18, padding: 15, display: 'flex', alignItems: 'center', gap: 14}}><div style={{fontSize: 31, color: ACCENT}}>▣</div><div><div style={{fontSize: 13, color: MUTED, letterSpacing: 2}}>STATUS / {morph > 0.6 ? 'REFUND' : 'ORDER'}</div><div style={{fontSize: 25, fontWeight: 900}}>{item.text}</div></div></FocusFrame>; }
	if (item.id === 'payment-ledger') return <FocusFrame active={isActive} style={{...base, background: PAPER, borderRadius: 3, padding: 15, border: `1px solid ${isActive ? ACCENT : '#C9C1B3'}`, boxShadow: isActive ? `inset 0 0 0 2px ${ACCENT}, 0 0 0 7px ${ACCENT}22` : 'none'}}><div style={{fontSize: 24, fontWeight: 900, marginBottom: 10}}>{item.text}</div><div style={{height: 2, background: '#D7CFC1', marginBottom: 10}} /><div style={{display: 'grid', gridTemplateColumns: '1.1fr 1fr 1fr', gap: 7, color: MUTED, fontSize: 17}}><span>款項</span><span>方式</span><span>狀態</span><b style={{height: 16, background: '#DED7CB'}} /><b style={{height: 16, background: '#DED7CB'}} /><b style={{height: 16, background: '#D8E7E1'}} /></div></FocusFrame>;
	if (item.id === 'payment-link') { const progress = Math.min(1, Math.max(0, (t - 17.34) / 0.4)); const color = isActive ? ACCENT : '#A9A093'; return <div style={{...base, zIndex: 4}}><svg width={70} height={19} viewBox="0 0 70 19" style={{display:'block',overflow:'visible'}}><line x1={0} y1={8} x2={70 * progress} y2={8} stroke={color} strokeWidth={isActive ? 3 : 1.5}/><circle cx={0} cy={8} r={3} fill={color}/>{progress === 1 && <circle cx={70} cy={8} r={3} fill={color}/>}</svg><div style={{fontSize:16,textAlign:'center',color,fontWeight:isActive ? 800 : 500}}>回接</div></div>; }
	if (item.id === 'trace-line') return <FocusFrame active={isActive} style={{...base, border: 0, boxShadow: 'none', background: 'transparent', display: 'flex', alignItems: 'center', gap: 12}}><div style={{height: 8, flex: 1, background: `linear-gradient(90deg, ${ACCENT} 0 68%, #D7CFC1 68%)`, borderRadius: 9}} /><span style={{fontSize: 18, fontWeight: 800, whiteSpace: 'nowrap'}}>{item.text}</span></FocusFrame>;
	return <FocusFrame active={isActive} style={{...base, background: '#EEE9DF', borderRadius: 4, padding: 12, display: 'grid', placeItems: 'center'}}><span style={{fontSize: 22, fontWeight: 800}}>{item.text}</span></FocusFrame>;
};

const Scene: React.FC = () => {
	const frame = useCurrentFrame();
	const state = currentState(frame);
	const active = new Set(state.active ?? []);
	const visible = state.visible ?? state.items ?? [];
	const t = state.t ?? frame / 30;
	const activeStep = state.scene === 'order-apply' ? 0 : state.scene === 'review-handoff' ? 1 : 2;
	return <AbsoluteFill style={{background: props.background ?? '#F5F0E7', color: INK, fontFamily: 'PingFang TC, Arial, sans-serif', overflow: 'hidden'}}><Rail activeStep={activeStep} /><div style={{position: 'absolute', left: 53, top: 154, color: '#C8BBA9', fontSize: 76, fontWeight: 900, lineHeight: 1, letterSpacing: -5}}>{String(activeStep + 1).padStart(2, '0')}</div><div style={{position: 'absolute', left: 54, top: 237, color: MUTED, fontSize: 14, letterSpacing: 2, writingMode: 'vertical-rl'}}>ORDER → REVIEW → TRACK</div><div style={{position: 'absolute', left: 50, right: 50, top: 548, height: 1, background: '#D7CFC1'}} />{visible.map((item) => <Item key={item.id} item={item} active={active} scene={state.scene ?? ''} t={t} />)}</AbsoluteFill>;
};

export const RemotionRoot: React.FC = () => <Composition id={props.composition ?? 'Main'} component={Scene} durationInFrames={props.frameCount} fps={props.fps} width={props.width} height={props.height} />;
