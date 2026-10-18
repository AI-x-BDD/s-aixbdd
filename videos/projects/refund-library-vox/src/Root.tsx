import React from 'react';
import {AbsoluteFill, Composition, useCurrentFrame} from 'remotion';
import props from '../public/render-props.json';
import stateData from '../public/state.json';

// B 候選：y2_vox 編輯式證據桌面。所有位置、鏡頭、標記進度與 active 只讀 public/state.json，
// 由 projects/refund-library-vox/scene_state.py 產生；本檔只負責畫法，不另算幾何。

type Rect = {x: number; y: number; w: number; h: number};
type Item = {id: string; text: string; kind: string; opacity: number; world: Rect; rot: number; z: number; parent?: string | null; mode?: string};
type Mark = {id: string; kind: string; owner: string; rect?: number[]; pts?: number[][]; p: number; rot?: number; text?: string};
type FrameState = {frame: number; t: number; scene: string; active: string[]; camera: {cx: number; cy: number; s: number}; visible: Item[]; marks: Mark[]};
type StateFile = {view: number[]; link_label: number[]; frames: FrameState[]};

const data = stateData as unknown as StateFile;
const DESK = '#E4DDCF';
const PAPER = '#F2EFE9';
const INK = '#1B1B1A';
const RED = '#B8433F';
const RED_DARK = '#93403C';
const MUTED_RED = '#A37C74';
const HIGHLIGHT = 'rgba(218,207,8,0.9)';
const SANS = '"PingFang TC", "Noto Sans TC", sans-serif';
const SERIF = '"Songti TC", "PingFang TC", serif';

// 依 id 固定的微小抖動，讓手畫線不完美但每次渲染一致。
const seeded = (id: string, k: number) => {
	let h = 2166136261;
	for (const c of id + k) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
	return ((h >>> 0) % 1000) / 1000 - 0.5;
};

const tornClip = (id: string) => {
	const pts: string[] = [];
	for (let i = 0; i <= 6; i++) pts.push(`${(seeded(id, i) * 2 + 1).toFixed(2)}% ${(i / 6) * 100}%`);
	for (let i = 6; i >= 0; i--) pts.push(`${(99 - seeded(id, i + 9) * 2).toFixed(2)}% ${(i / 6) * 100}%`);
	return `polygon(${pts.join(',')})`;
};

const Tag: React.FC<{text: string; size: number; active?: boolean; style?: React.CSSProperties}> = ({text, size, active, style}) => (
	<div style={{position: 'absolute', display: 'flex', alignItems: 'center', ...style}}>
		{active && <div style={{width: size * 0.32, alignSelf: 'stretch', background: RED, marginRight: 4}} />}
		<div style={{background: INK, color: '#F4F1EA', fontFamily: SANS, fontWeight: 800, fontSize: size, lineHeight: 1, padding: `${size * 0.26}px ${size * 0.42}px`, letterSpacing: size * 0.04, whiteSpace: 'nowrap', clipPath: tornClip(text)}}>{text}</div>
	</div>
);

const Bars: React.FC<{x: number; y: number; widths: number[]; gap?: number; h?: number; color?: string}> = ({x, y, widths, gap = 22, h = 10, color = '#CFC8BA'}) => <>
	{widths.map((w, i) => <div key={i} style={{position: 'absolute', left: x, top: y + i * gap, width: w, height: h, background: color, borderRadius: 2}} />)}
</>;

const Tape: React.FC<{x: number; y: number; rot: number}> = ({x, y, rot}) => <div style={{position: 'absolute', left: x, top: y, width: 92, height: 30, background: 'rgba(246,242,226,0.62)', transform: `rotate(${rot}deg)`, boxShadow: '0 1px 2px rgba(0,0,0,0.08)'}} />;

const paperStyle = (item: Item, extra?: React.CSSProperties): React.CSSProperties => ({
	position: 'absolute', left: item.world.x, top: item.world.y, width: item.world.w, height: item.world.h,
	transform: `rotate(${item.rot}deg)`, transformOrigin: 'center', opacity: item.opacity,
	background: PAPER, boxShadow: '3px 6px 10px rgba(0,0,0,0.28)', zIndex: item.z, ...extra,
});

const Veil: React.FC<{on: boolean}> = ({on}) => on ? <div style={{position: 'absolute', inset: 0, background: 'rgba(228,221,207,0.42)'}} /> : null;

const ItemView: React.FC<{item: Item; active: string; emphasis: boolean; linkLabel: number[]}> = ({item, active, emphasis, linkLabel}) => {
	const isActive = item.id === active;
	const w = item.world.w;
	const h = item.world.h;
	if (item.kind === 'doc') return <div style={paperStyle(item)}>
		<Tape x={w - 120} y={-14} rot={6} />
		<Tag text={item.text} size={40} active={isActive} style={{left: 18, top: 26}} />
		<div style={{position: 'absolute', right: 30, top: 40, fontFamily: SERIF, fontSize: 24, color: '#7E776B'}}>訂單明細</div>
		<div style={{position: 'absolute', left: 30, right: 30, top: 136, height: 2, background: '#D3CCBE'}} />
		<Bars x={30} y={372} widths={[420, 300, 360]} />
		<Veil on={!emphasis} />
	</div>;
	if (item.kind === 'row') return <div style={{position: 'absolute', left: item.world.x, top: item.world.y, width: w, height: h, zIndex: item.z}}>
		<div style={{position: 'absolute', left: 14, top: 14, fontFamily: SANS, fontWeight: 800, fontSize: 36, color: INK, letterSpacing: 2}}>{item.text}</div>
		<Bars x={Math.max(120, item.text.length * 40 + 40)} y={22} widths={[w - Math.max(120, item.text.length * 40 + 40) - 30, (w - Math.max(120, item.text.length * 40 + 40)) * 0.55]} gap={24} />
		<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 1, background: '#DAD3C5'}} />
		<Veil on={!emphasis} />
	</div>;
	if (item.kind === 'slip') return <div style={paperStyle(item)}>
		<Tape x={w / 2 - 46} y={-14} rot={-4} />
		<Tag text={item.text} size={38} active={isActive} style={{left: 16, top: 26}} />
		<Bars x={22} y={104} widths={[230, 170, 200]} gap={24} />
		<Veil on={!emphasis} />
	</div>;
	if (item.kind === 'badge') return <div style={paperStyle(item, {background: '#F4F0E6', backgroundImage: 'repeating-linear-gradient(0deg, transparent 0 37px, rgba(120,140,160,0.22) 37px 38px)'})}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 26, background: RED_DARK, opacity: 0.85}} />
		<svg width={150} height={150} style={{position: 'absolute', left: (w - 150) / 2, top: 64}}>
			<defs><pattern id="ht" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="4.5" cy="4.5" r="2.6" fill="#55534E" /></pattern></defs>
			<circle cx={75} cy={75} r={70} fill="url(#ht)" />
			<circle cx={75} cy={75} r={70} fill="none" stroke="#55534E" strokeWidth={3} />
		</svg>
		<div style={{position: 'absolute', left: 0, right: 0, top: 232, textAlign: 'center', fontFamily: SERIF, fontSize: 24, color: '#6E685E'}}>確認條件</div>
		<Tag text={item.text} size={46} active={isActive} style={{left: 34, top: 280}} />
		<Veil on={!emphasis} />
	</div>;
	if (item.kind === 'conditions') return <div style={paperStyle(item)}>
		<Tape x={30} y={-14} rot={-7} />
		<Tag text={item.text} size={38} active={isActive} style={{left: 16, top: 26}} />
		{[0, 1, 2].map((i) => <React.Fragment key={i}>
			<div style={{position: 'absolute', left: 30, top: 112 + i * 80, width: 40, height: 40, border: `3px solid ${INK}`, background: '#FBF9F4'}} />
			<Bars x={92} y={118 + i * 80} widths={[260 - i * 40, 180 + i * 20]} gap={20} />
		</React.Fragment>)}
		<Veil on={!emphasis} />
	</div>;
	if (item.kind === 'stamp') return <div style={{position: 'absolute', left: item.world.x, top: item.world.y, width: w, height: h, transform: `rotate(${item.rot}deg)`, zIndex: item.z, opacity: emphasis ? 0.95 : 0.6, mixBlendMode: 'multiply', border: `5px double ${RED}`, borderRadius: 8, display: 'grid', placeItems: 'center', color: RED, fontFamily: SANS, fontWeight: 900, fontSize: h * 0.56, letterSpacing: h * 0.12}}>{item.text}</div>;
	if (item.kind === 'refund') {
		// 未撕下時是原訂單的下緣：同色、同陰影且裁掉頂邊陰影，與訂單接成同一張紙；降階狀態跟隨訂單。
		if (item.mode === 'attached') return <div style={{...paperStyle(item), clipPath: 'inset(0px -40px -40px -40px)'}}>
			{item.text && <Tag text={item.text} size={38} style={{left: 18, top: 30}} />}
			<Bars x={item.text ? 200 : 30} y={48} widths={[item.text ? 340 : 520, 240]} gap={24} />
			<Veil on={!emphasis} />
		</div>;
		return <div style={paperStyle(item, {borderLeft: `14px solid ${RED}`})}>
			<Tape x={w - 110} y={-12} rot={8} />
			<Tag text={item.text} size={40} active={isActive} style={{left: 16, top: 30}} />
			<Bars x={200} y={44} widths={[300, 220]} gap={26} />
			<Veil on={!emphasis} />
		</div>;
	}
	if (item.kind === 'link') {
		const [lx, ly, lw, lh] = linkLabel;
		return <div style={{position: 'absolute', left: lx, top: ly, width: lw, height: lh, zIndex: item.z, display: 'grid', placeItems: 'center', fontFamily: SANS, fontWeight: 900, fontSize: 32, color: isActive ? RED : MUTED_RED, opacity: item.opacity}}>{item.text}</div>;
	}
	if (item.kind === 'ledger') return <div style={paperStyle(item)}>
		<Tape x={40} y={-14} rot={-5} />
		<Tape x={w - 130} y={-12} rot={7} />
		<Tag text={item.text} size={40} active={isActive} style={{left: 18, top: 24}} />
		<div style={{position: 'absolute', left: 30, right: 30, top: 88, height: 2, background: '#D3CCBE'}} />
		<Veil on={!emphasis} />
	</div>;
	if (item.kind === 'label') return <div style={{position: 'absolute', left: item.world.x, top: item.world.y, width: w, height: h, transform: `rotate(${item.rot}deg)`, zIndex: item.z, opacity: item.opacity}}>
		<Tag text={item.text} size={46} active={isActive} style={{left: 0, top: 6}} />
	</div>;
	return null;
};

const bezierPoint = (pts: number[][], u: number) => {
	const [p0, p1, p2, p3] = pts;
	const a = (1 - u) ** 3, b = 3 * (1 - u) ** 2 * u, c = 3 * (1 - u) * u ** 2, d = u ** 3;
	return [a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]];
};

const handLine = (id: string, x: number, y: number, w: number) => {
	const segs = 6;
	let d = `M ${x} ${y + seeded(id, 0) * 4}`;
	for (let i = 1; i <= segs; i++) d += ` L ${x + (w * i) / segs} ${y + seeded(id, i) * 5}`;
	return d;
};

const handEllipse = (id: string, x: number, y: number, w: number, h: number) => {
	const cx = x + w / 2, cy = y + h / 2, n = 28;
	let d = '';
	for (let i = 0; i <= n; i++) {
		const a = -Math.PI * 0.95 + (i / n) * Math.PI * 2.12; // 一筆畫、首尾略交叉不閉合
		const r = 1 + seeded(id, i) * 0.06;
		const px = cx + Math.cos(a) * (w / 2) * r, py = cy + Math.sin(a) * (h / 2) * r;
		d += `${i === 0 ? 'M' : ' L'} ${px.toFixed(1)} ${py.toFixed(1)}`;
	}
	return d;
};

const MarkView: React.FC<{mark: Mark; tone: 'active' | 'past' | 'idle'}> = ({mark, tone}) => {
	if (mark.p <= 0) return null;
	const color = tone === 'active' ? RED : MUTED_RED;
	const dash = {pathLength: 1, strokeDasharray: 1, strokeDashoffset: 1 - mark.p} as const;
	const [x = 0, y = 0, w = 0, h = 0] = mark.rect ?? [];
	if (mark.kind === 'underline') return <path d={handLine(mark.id, x, y + h / 2, w)} stroke={color} strokeWidth={7} fill="none" strokeLinecap="round" {...dash} />;
	if (mark.kind === 'circle') return <path d={handEllipse(mark.id, x, y, w, h)} stroke={color} strokeWidth={6} fill="none" strokeLinecap="round" {...dash} />;
	if (mark.kind === 'highlight') return <rect x={x} y={y} width={w * mark.p} height={h} fill={HIGHLIGHT} opacity={tone === 'active' ? 1 : 0.55} style={{mixBlendMode: 'multiply'}} rx={4} />;
	if (mark.kind === 'check') return <path d={`M ${x + 4} ${y + h * 0.55} L ${x + w * 0.42} ${y + h - 2} L ${x + w + 10} ${y - 12}`} stroke={color} strokeWidth={8} fill="none" strokeLinecap="round" strokeLinejoin="round" {...dash} />;
	if (mark.kind === 'perforation') return <line x1={x} y1={y} x2={x + w * mark.p} y2={y} stroke={color} strokeWidth={5} strokeDasharray="14 10" />;
	if (mark.kind === 'string' && mark.pts) {
		const pts = mark.pts;
		const d = `M ${pts[0][0]} ${pts[0][1]} C ${pts[1][0]} ${pts[1][1]}, ${pts[2][0]} ${pts[2][1]}, ${pts[3][0]} ${pts[3][1]}`;
		const head = bezierPoint(pts, mark.p);
		return <g>
			<path d={d} stroke={color} strokeWidth={tone === 'active' ? 6 : 4} fill="none" strokeLinecap="round" {...dash} />
			<circle cx={pts[0][0]} cy={pts[0][1]} r={9} fill={color} />
			<circle cx={head[0]} cy={head[1]} r={9} fill={color} />
		</g>;
	}
	if (mark.kind === 'stamp') {
		const scale = 1.45 - 0.45 * mark.p;
		const cx = x + w / 2, cy = y + h / 2;
		return <g transform={`translate(${cx} ${cy}) rotate(${mark.rot ?? 0}) scale(${scale})`} style={{mixBlendMode: 'multiply'}} opacity={tone === 'idle' ? 0.55 : 0.92}>
			<rect x={-w / 2} y={-h / 2} width={w} height={h} rx={6} fill="none" stroke={RED} strokeWidth={5} />
			<text x={0} y={h * 0.2} textAnchor="middle" fontFamily={SANS} fontWeight={900} fontSize={h * 0.56} fill={RED} letterSpacing={4}>{mark.text}</text>
		</g>;
	}
	return null;
};

const Scene: React.FC = () => {
	const frame = useCurrentFrame();
	const state = data.frames[Math.min(frame, data.frames.length - 1)];
	const active = state.active[0];
	const {cx, cy, s} = state.camera;
	const [vx, vy] = data.view;
	const byId = new Map(state.visible.map((item) => [item.id, item]));
	const activeItem = byId.get(active);
	// 畫面層級：焦點物件、它所屬的單據、它底下的列維持清楚；其餘紙件降一階（覆一層桌面色）。
	const directEmphasis = (id: string, parent?: string | null) => id === active || id === activeItem?.parent || parent === active;
	const emphasis = (item: Item) => item.kind === 'refund' && item.mode === 'attached' ? directEmphasis('order-doc') : directEmphasis(item.id, item.parent);
	const beatOrder = ['order-doc', 'product-row', 'reason-row', 'application-slip', 'reviewer-card', 'conditions-card', 'approval-stamp', 'refund-slip', 'payment-link', 'payment-ledger', 'amount-row', 'method-row', 'progress-row', 'trace-label'];
	const tone = (owner: string): 'active' | 'past' | 'idle' => owner === active ? 'active' : beatOrder.indexOf(owner) < beatOrder.indexOf(active) ? 'past' : 'idle';
	const items = [...state.visible].sort((a, b) => a.z - b.z);
	// 桌面鏡頭只在內容視窗（y < 570）內呈現；其下為乾淨的字幕保留區，背景脈絡不得滑入字幕帶。
	return <AbsoluteFill style={{background: DESK, overflow: 'hidden'}}>
		<div style={{position: 'absolute', left: 0, top: 0, width: 1280, height: 570, overflow: 'hidden'}}>
		<div style={{position: 'absolute', left: 0, top: 0, width: 1, height: 1, transformOrigin: '0 0', transform: `translate(${vx}px, ${vy}px) scale(${s}) translate(${-cx}px, ${-cy}px)`}}>
			<svg width={4000} height={2800} viewBox="-900 -700 4000 2800" style={{position: 'absolute', left: -900, top: -700}}>
				<filter id="fiber" x="0" y="0" width="100%" height="100%">
					<feTurbulence type="fractalNoise" baseFrequency="0.018 0.05" numOctaves={3} seed={7} />
					<feColorMatrix values="0 0 0 0 0.42  0 0 0 0 0.37  0 0 0 0 0.29  0 0 0 0.16 0" />
				</filter>
				<rect x={-900} y={-700} width={4000} height={2800} fill={DESK} />
				<rect x={-900} y={-700} width={4000} height={2800} filter="url(#fiber)" />
			</svg>
			{items.map((item) => <ItemView key={item.id} item={item} active={active} emphasis={emphasis(item)} linkLabel={data.link_label} />)}
			<svg width={4000} height={2800} viewBox="-900 -700 4000 2800" style={{position: 'absolute', left: -900, top: -700, zIndex: 50, overflow: 'visible'}}>
				{state.marks.map((mark) => <MarkView key={mark.id} mark={mark} tone={tone(mark.owner)} />)}
			</svg>
		</div>
		</div>
	</AbsoluteFill>;
};

export const RemotionRoot: React.FC = () => <Composition id={props.composition ?? 'Main'} component={Scene} durationInFrames={props.frameCount} fps={props.fps} width={props.width} height={props.height} />;
