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

const INK = '#24343D';
const MUTED = '#6D7C80';
const CREAM = '#FFF7E8';
const DESK = '#F3E8D7';
const MAT = '#D9C7A9';
const BLUE = '#2457D6';
const CORAL = '#E67958';

const DeskSurface: React.FC<{scene: string}> = ({scene}) => <>
	<div style={{position: 'absolute', inset: 0, background: DESK}} />
	<div style={{position: 'absolute', left: 74, top: 138, width: 1132, height: 410, borderRadius: 32, background: MAT, transform: 'rotate(-1deg)', boxShadow: '0 18px 0 rgba(36,52,61,0.08)'}} />
	<div style={{position: 'absolute', left: 92, top: 150, width: 1096, height: 386, borderRadius: 26, background: '#EADBC2', transform: 'rotate(-1deg)', opacity: 0.92}} />
	<div style={{position: 'absolute', left: 105, top: 162, width: 1070, height: 360, borderRadius: 24, border: '2px dashed rgba(109,124,128,0.22)', transform: 'rotate(-1deg)'}} />
	<div style={{position: 'absolute', right: 82, top: 182, width: 82, height: 82, borderRadius: '50%', border: '8px solid rgba(109,124,128,0.16)', opacity: scene === 'payment-track' ? 0.35 : 0.75}} />
	<div style={{position: 'absolute', right: 105, top: 206, width: 32, height: 32, borderRadius: '50%', background: 'rgba(109,124,128,0.12)'}} />
	<div style={{position: 'absolute', left: 92, bottom: 26, color: MUTED, fontSize: 13, letterSpacing: 3}}>TOP-DOWN WORKTABLE / HANDOFF, APPROVAL, TRACE</div>
</>;

const Header: React.FC<{scene: string}> = ({scene}) => <>
	<div style={{position: 'absolute', left: 52, top: 42, color: BLUE, fontSize: 15, letterSpacing: 4, fontWeight: 900}}>REFUND WORKTABLE</div>
	<div style={{position: 'absolute', right: 52, top: 42, color: MUTED, fontSize: 14, letterSpacing: 2}}>桌面紀錄 24—{scene === 'order-apply' ? '01' : scene === 'review-handoff' ? '02' : '03'}</div>
	<div style={{position: 'absolute', left: 52, top: 76, color: INK, fontSize: 32, fontWeight: 900, letterSpacing: 1}}>{scene === 'order-apply' ? '先把資料攤開，再按下申請' : scene === 'review-handoff' ? '把申請交到審核桌，留下決定' : '把退款單夾回付款紀錄'}</div>
</>;

const Focus: React.FC<{active: boolean; children: React.ReactNode; style?: React.CSSProperties}> = ({active, children, style}) => <div style={{position: 'absolute', border: active ? `3px solid ${BLUE}` : '1px solid rgba(36,52,61,0.26)', boxShadow: active ? `0 0 0 7px ${BLUE}22, 0 10px 0 rgba(36,52,61,0.12)` : '0 8px 0 rgba(36,52,61,0.10)', ...style}}>{children}</div>;

const Pin: React.FC<{color?: string}> = ({color = CORAL}) => <div style={{width: 15, height: 15, borderRadius: '50%', background: color, boxShadow: '0 2px 0 rgba(36,52,61,0.2)', flex: '0 0 auto'}} />;

const Hand: React.FC<{x: number; y: number; flip?: boolean; visible: boolean}> = ({x, y, flip = false, visible}) => <div style={{position: 'absolute', left: x, top: y, width: 88, height: 68, opacity: visible ? 0.95 : 0, transform: `scaleX(${flip ? -1 : 1}) rotate(-12deg)`, transformOrigin: 'center'}}><div style={{position: 'absolute', left: 17, top: 15, width: 51, height: 42, borderRadius: '45% 50% 42% 40%', background: '#F4B88E', border: '2px solid #C87958'}} /><div style={{position: 'absolute', left: 5, top: 9, width: 42, height: 17, borderRadius: 14, background: '#F4B88E', border: '2px solid #C87958', transform: 'rotate(-20deg)'}} /><div style={{position: 'absolute', left: 54, top: 22, width: 32, height: 16, borderRadius: 12, background: '#F4B88E', border: '2px solid #C87958', transform: 'rotate(35deg)'}} /></div>;

const Person: React.FC<{active: boolean; text?: string}> = ({active, text}) => <div style={{position: 'relative', width: '100%', height: '100%'}}><div style={{position: 'absolute', left: 72, top: 4, width: 70, height: 70, borderRadius: '50%', background: '#F4B88E', border: `3px solid ${active ? BLUE : '#C87958'}`}}><div style={{position: 'absolute', left: 17, top: 28, width: 8, height: 8, borderRadius: '50%', background: INK}} /><div style={{position: 'absolute', right: 17, top: 28, width: 8, height: 8, borderRadius: '50%', background: INK}} /><div style={{position: 'absolute', left: 24, top: 47, width: 23, height: 8, borderBottom: `3px solid ${INK}`, borderRadius: '50%'}} /></div><div style={{position: 'absolute', left: 22, top: 70, width: 170, height: 102, borderRadius: '55% 55% 12px 12px', background: active ? '#B7D8F0' : '#A9C6C2', border: `3px solid ${active ? BLUE : '#628E8E'}`}} /><div style={{position: 'absolute', left: -2, top: 91, width: 110, height: 30, borderRadius: 20, background: '#F4B88E', border: '3px solid #C87958', transform: 'rotate(-18deg)'}} /><div style={{position: 'absolute', left: 124, top: 97, width: 120, height: 30, borderRadius: 20, background: '#F4B88E', border: '3px solid #C87958', transform: 'rotate(18deg)'}} /><div style={{position: 'absolute', left: 46, bottom: 5, right: 46, textAlign: 'center', color: INK, fontSize: 20, fontWeight: 900}}>{text}</div></div>;

const RubberStamp: React.FC<{active: boolean; text?: string; t: number}> = ({active, text, t}) => <div style={{position: 'relative', width: '100%', height: '100%', transform: `rotate(-7deg) translateY(${active ? Math.sin(t * 18) * 2 : 0}px)`}}><div style={{position: 'absolute', left: 78, top: 0, width: 70, height: 30, borderRadius: 9, background: active ? BLUE : '#7D8B92', border: '3px solid #53666E'}} /><div style={{position: 'absolute', left: 60, top: 22, width: 108, height: 30, borderRadius: '9px 9px 5px 5px', background: active ? BLUE : '#9DABB0', border: '3px solid #53666E'}} /><div style={{position: 'absolute', left: 26, bottom: 5, width: 174, height: 34, borderRadius: 5, background: active ? '#E5EDFF' : '#D6DDDF', border: `4px solid ${active ? BLUE : '#53666E'}`, display: 'grid', placeItems: 'center', color: active ? BLUE : '#53666E', fontSize: 19, fontWeight: 900, letterSpacing: 2}}>{text}</div></div>;

const Item: React.FC<{item: StateItem; active: Set<string>; scene: string; t: number}> = ({item, active, scene, t}) => {
	const isActive = active.has(item.id);
	const retiringOpacity = scene === 'review-handoff' && (item.id === 'application-card' || item.id === 'reviewer') && t >= 12.38 ? Math.max(0, 1 - (t - 12.38) / 0.34) : 1;
	const stampOpacity = scene === 'review-handoff' && item.id === 'approval-stamp' && t > 12.72 ? Math.max(0, 1 - (t - 12.72) / 0.3) : 1;
	const ticketOpacity = scene === 'review-handoff' && item.id === 'refund-ticket' && t < 12.72 ? 0 : 1;
	const opacity = (item.opacity ?? 1) * retiringOpacity * stampOpacity * ticketOpacity;
	const base: React.CSSProperties = {position: 'absolute', left: item.x ?? 0, top: item.y ?? 0, width: item.w ?? 100, height: item.h ?? 60, opacity, color: INK, fontFamily: 'PingFang TC, Arial, sans-serif'};
	if (item.id === 'order-card' || item.id === 'application-card') {
		const isApp = item.id === 'application-card';
		return <Focus active={isActive} style={{...base, background: CREAM, borderRadius: 6, padding: 18, overflow: 'hidden', transform: `rotate(${isApp ? -3 : 2}deg)`}}><div style={{position: 'absolute', left: 0, top: 0, right: 0, height: 17, background: isApp ? BLUE : CORAL, opacity: 0.85}} /><div style={{position: 'absolute', left: 20, top: 17, right: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}><span style={{fontSize: 11, letterSpacing: 2, color: MUTED, fontWeight: 900}}>{isApp ? 'REVIEW TRAY / 02' : 'ORDER RECEIPT / 01'}</span><Pin color={isApp ? BLUE : CORAL} /></div><div style={{position: 'absolute', left: 18, top: 52, fontSize: 29, fontWeight: 900, letterSpacing: 2}}>{item.text}</div><div style={{position: 'absolute', left: 20, right: 20, bottom: 20, display: 'flex', gap: 8}}><i style={{height: 7, flex: 1, background: isApp ? '#BFD0F6' : '#E9C7B8'}} /><i style={{height: 7, flex: 0.55, background: '#D5DCDD'}} /><i style={{height: 7, flex: 0.35, background: '#D5DCDD'}} /></div><div style={{position: 'absolute', right: 11, top: 11, width: 32, height: 32, border: `2px solid ${isApp ? BLUE : CORAL}`, borderRadius: '50%', display: 'grid', placeItems: 'center', color: isApp ? BLUE : CORAL, fontSize: 17}}>{isApp ? '↗' : '✦'}</div></Focus>;
	}
	if (item.id === 'product-check' || item.id === 'reason-check') return <Focus active={isActive} style={{...base, background: isActive ? '#FFF0B5' : '#F5E7B7', border: `2px solid ${isActive ? '#C99520' : '#C8B273'}`, borderRadius: 4, padding: 13, display: 'flex', alignItems: 'center', justifyContent: 'space-between', transform: `rotate(${item.id === 'product-check' ? -4 : 4}deg)`}}><span style={{fontSize: 24, fontWeight: 900}}>{item.text}</span><Pin color={isActive ? CORAL : '#B89B47'} /></Focus>;
	if (item.id === 'submit-button') return <Focus active={isActive} style={{...base, border: 0, boxShadow: 'none', background: 'transparent', transform: 'rotate(-7deg)', padding: 0}}><RubberStamp active={isActive} text={item.text} t={t} /></Focus>;
	if (item.id === 'reviewer') return <Focus active={isActive} style={{...base, border: 0, boxShadow: 'none', background: 'transparent', padding: 0}}><Person active={isActive} text={item.text} /></Focus>;
	if (item.id === 'approval-stamp') return <Focus active={isActive} style={{...base, border: 0, boxShadow: 'none', background: 'transparent', padding: 0}}><RubberStamp active={isActive} text={item.text} t={t} /></Focus>;
	if (item.id === 'refund-ticket') return <Focus active={isActive} style={{...base, background: '#FFF0B5', border: `3px dashed ${isActive ? BLUE : '#C99520'}`, borderRadius: 5, padding: 15, display: 'flex', alignItems: 'center', gap: 15, transform: `rotate(${scene === 'payment-track' ? -2 : 2}deg)`, clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%, 0 82%, 3% 76%, 0 70%, 3% 64%, 0 58%, 3% 52%, 0 46%, 3% 40%, 0 34%, 3% 28%, 0 22%, 3% 16%)'}}><div style={{width: 34, height: 44, border: `2px solid ${BLUE}`, background: '#E0E9FF', display: 'grid', placeItems: 'center', color: BLUE, fontSize: 20}}>↻</div><div><div style={{fontSize: 11, letterSpacing: 2, color: MUTED, fontWeight: 900}}>STATUS / {scene === 'payment-track' ? 'REFUND' : 'ORDER'}</div><div style={{fontSize: 25, fontWeight: 900}}>{item.text}</div></div></Focus>;
	if (item.id === 'payment-ledger') return <Focus active={isActive} style={{...base, background: '#FFFDF5', borderRadius: 4, padding: 18, transform: 'rotate(1deg)', borderColor: isActive ? BLUE : '#A6AAA5'}}><div style={{position: 'absolute', left: '50%', top: 0, bottom: 0, width: 3, background: '#D9D5C8'}} /><div style={{fontSize: 25, fontWeight: 900, letterSpacing: 1}}>付款紀錄</div><div style={{height: 3, background: '#A6AAA5', margin: '11px 0 12px'}} /><div style={{display: 'grid', gridTemplateColumns: '1.1fr 1fr 1fr', gap: 8, color: MUTED, fontSize: 16}}><span>款項</span><span>方式</span><span>狀態</span><b style={{height: 19, background: '#DCE1E1'}} /><b style={{height: 19, background: '#DCE1E1'}} /><b style={{height: 19, background: '#D4E8E0'}} /><b style={{height: 19, background: '#DCE1E1'}} /><b style={{height: 19, background: '#DCE1E1'}} /><b style={{height: 19, background: '#D4E8E0'}} /></div><div style={{position: 'absolute', left: 20, right: 20, bottom: 20, borderTop: '2px solid #D9D5C8', paddingTop: 7, color: MUTED, fontSize: 13, letterSpacing: 2}}>OPEN LEDGER / TRACEABLE</div></Focus>;
	if (item.id === 'amount' || item.id === 'method' || item.id === 'progress') return <Focus active={isActive} style={{...base, background: isActive ? '#D6E4FF' : '#EFF3F0', borderRadius: 4, padding: 12, display: 'grid', placeItems: 'center', transform: `rotate(${item.id === 'amount' ? -2 : item.id === 'method' ? 1 : 3}deg)`}}><Pin color={isActive ? BLUE : '#A6AAA5'} /><span style={{fontSize: 21, fontWeight: 900}}>{item.text}</span></Focus>;
	if (item.id === 'trace-line') return <Focus active={isActive} style={{...base, border: 0, boxShadow: 'none', background: 'transparent', display: 'flex', alignItems: 'center', gap: 12}}><div style={{height: 9, flex: 1, background: `repeating-linear-gradient(90deg, ${BLUE} 0 32px, transparent 32px 42px)`, borderRadius: 9}} /><span style={{fontSize: 18, fontWeight: 900, whiteSpace: 'nowrap'}}>{item.text}</span></Focus>;
	return <Focus active={isActive} style={{...base, background: '#EFF3F0', borderRadius: 4, padding: 12, display: 'grid', placeItems: 'center'}}><span style={{fontSize: 22, fontWeight: 900}}>{item.text}</span></Focus>;
};

const DeskString: React.FC<{scene: string}> = ({scene}) => <svg width="1280" height="560" viewBox="0 0 1280 560" style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>{scene === 'review-handoff' && <path d="M430 344 C550 285 660 215 836 175" stroke={BLUE} strokeWidth="6" fill="none" strokeLinecap="round" opacity="0.7" />}{scene === 'payment-track' && <path d="M420 258 C515 300 580 414 650 474" stroke={BLUE} strokeWidth="6" fill="none" strokeLinecap="round" opacity="0.7" />}</svg>;

const Scene: React.FC = () => {
	const frame = useCurrentFrame();
	const state = currentState(frame);
	const active = new Set(state.active ?? []);
	const visible = state.visible ?? state.items ?? [];
	const t = state.t ?? frame / 30;
	const scene = state.scene ?? 'order-apply';
	return <AbsoluteFill style={{background: props.background ?? DESK, color: INK, fontFamily: 'PingFang TC, Arial, sans-serif', overflow: 'hidden'}}><DeskSurface scene={scene} /><Header scene={scene} /><DeskString scene={scene} /><div style={{position: 'absolute', left: 54, top: 170, color: '#C8B99E', fontSize: 76, fontWeight: 900, letterSpacing: -5}}>{scene === 'order-apply' ? '01' : scene === 'review-handoff' ? '02' : '03'}</div><div style={{position: 'absolute', left: 54, top: 256, color: MUTED, fontSize: 13, letterSpacing: 3, writingMode: 'vertical-rl'}}>PAPER → HAND → LEDGER</div><Hand x={730} y={470} visible={active.has('submit-button')} /><Hand x={690} y={305} flip visible={active.has('reviewer')} />{visible.map((item) => <Item key={item.id} item={item} active={active} scene={scene} t={t} />)}</AbsoluteFill>;
};

export const RemotionRoot: React.FC = () => <Composition id={props.composition ?? 'Main'} component={Scene} durationInFrames={props.frameCount} fps={props.fps} width={props.width} height={props.height} />;
