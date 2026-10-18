import React from 'react';
import {AbsoluteFill,Composition,useCurrentFrame} from 'remotion';
import props from '../public/render-props.json';
import data from '../public/state.json';
const ink='#171A1B',orange='#E26A2C';
const Scene:React.FC=()=>{const f=useCurrentFrame(); const s=data.frames[Math.min(f,data.frames.length-1)]; const active=new Set(s.active); const phase=f/30<7.2?0:f/30<15.56?1:2;
return <AbsoluteFill style={{background:'#FBFBFB',fontFamily:'PingFang TC,sans-serif'}}><svg viewBox="0 0 1280 720" width="1280" height="720">
<defs><filter id="pencil"><feTurbulence type="fractalNoise" baseFrequency=".025" numOctaves="2" result="noise"/><feDisplacementMap in="SourceGraphic" in2="noise" scale="1.1"/></filter><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 9 5 L 0 10" fill="none" stroke="context-stroke" strokeWidth="1.8"/></marker></defs>
<text x="75" y="76" fontSize="16" letterSpacing="5" fill="#777">退款，如何回到你手上？</text>
{['找對訂單','交給審核','回接款項'].map((v,i)=><g key={v}><circle cx={920+i*115} cy={60} r="14" fill={phase===i?orange:'#EEE'}/><text x={920+i*115} y="65" textAnchor="middle" fontSize="14" fill={phase===i?'white':'#888'}>{i+1}</text><text x={920+i*115} y="99" textAnchor="middle" fontSize="14" fill={phase===i?ink:'#999'}>{v}</text></g>)}
{phase===0&&f/30<6.5&&<g stroke={ink} strokeWidth="2" fill="none" opacity={.5} markerEnd="url(#arrow)"><path d="M380 290 Q430 260 470 260"/><path d="M720 310 Q810 310 870 310"/></g>}
{s.visible.map((n:any)=>{const on=active.has(n.id),c=on?orange:ink;const w=n.w,h=n.h, k=n.kind;
return <g key={n.id} transform={`translate(${n.x},${n.y})`} opacity={n.opacity}>
<g fill="none" stroke={c} strokeWidth={on?4:2.5} strokeLinecap="round" strokeLinejoin="round" filter="url(#pencil)" strokeDasharray="2200" strokeDashoffset={2200*(1-n.draw)}>
{(k==='receipt'||k==='paper'||k==='ticket')&&<><path d={`M8 8 L${w-12} 5 L${w-7} ${h-12} L${w-24} ${h-19} L${w-42} ${h-10} L${w-60} ${h-19} L8 ${h-11} Z`}/>{k==='receipt'&&<><path d={`M35 50 H${w-35} M35 79 H${w-65} M35 115 H${w-38} M35 146 H${w-85}`}/><path d="M30 185 L48 201 L80 166"/></>}{k==='paper'&&<path d={`M28 30 L${w-40} 48 L90 ${h-68} L70 66 Z M70 66 L${w-40} 48`}/ >}{k==='ticket'&&n.morph!==undefined&&<path d={`M35 50 H${w-35} M35 79 H${w-65} M35 115 H${w-38}`} opacity={1-n.morph}/>}{k==='ticket'&&<path d={`M30 32 H${w-30} M30 56 H${w-90} M${w-47} 8 V${h-14}`} strokeDasharray="6 8"/>}</>}
{k==='box'&&<><path d={`M38 24 L100 6 L165 28 L165 78 L100 100 L38 80 Z M38 24 L100 45 L165 28 M100 45 V100 M70 15 L135 36`}/></>}
{k==='bubble'&&<path d={`M12 8 H${w-14} V${h-25} H90 L60 ${h-5} L65 ${h-25} H12 Z`}/>}
{k==='person'&&<><circle cx={w/2} cy="45" r="38"/><path d={`M${w/2-75} 180 Q${w/2-76} 96 ${w/2} 96 Q${w/2+75} 96 ${w/2+75} 180 M55 184 H${w-55}`}/><path d="M94 144 L117 165 L167 121"/></>}
{k==='stamp'&&<path d={`M5 5 H${w-5} V${h-5} H5 Z`}/>}
{k==='ledger'&&<><path d={`M8 5 H${w-10} V${h-8} H8 Z M8 67 H${w-10}`}/><path d="M30 9 V59 M40 9 V59"/></>}
{k==='trace'&&<path d="M125 75 V50 H730 V65"/>}
{k==='link'&&<><path d={`M0 53 H${162*n.draw}`} strokeDasharray="none"/>{n.draw>.97&&<><circle cx="0" cy="53" r="4" fill={c}/><circle cx="162" cy="53" r="4" fill={c}/></>}</>}
{k==='field'&&<><path d={`M0 ${h-8} H${w}`} opacity=".2"/>{on&&<path d={`M-4 6 Q${w/2} -6 ${w+3} 7 L${w+2} ${h-9} Q${w/2} ${h+3} -4 ${h-8} Z`}/>}</>}
</g>
{k==='ledger'?<text x="60" y="47" fontSize="30" fill={c} fontWeight="700">{n.text}</text>:<text x={k==='field'?15:w/2} y={k==='trace'?38:k==='field'?42:k==='link'?24:k==='box'?h-5:k==='bubble'?h/2+10:h-24} textAnchor={k==='field'?'start':'middle'} fontSize={n.text.includes('→')?23:k==='trace'?27:k==='link'?22:30} fill={c} fontWeight={on?700:500}>{n.text}</text>}
{k==='field'&&<path d={`M${w-145} 34 H${w-20} M${w-145} 44 H${w-55}`} fill="none" stroke="#B8BCBD" strokeWidth="4"/>}
{on&&!['ledger','field','link','trace','box','bubble'].includes(k)&&<path d={`M${w*.2} ${h-10} Q${w*.5} ${h-4} ${w*.8} ${h-12}`} fill="none" stroke={orange} strokeWidth="3" strokeLinecap="round"/>}
</g>})}
<text x="75" y="560" fontSize="15" fill="#999">WHITEBOARD  /  退款流程示意</text>
</svg></AbsoluteFill>};
export const RemotionRoot:React.FC=()=> <Composition id="Main" component={Scene} durationInFrames={props.frameCount} fps={props.fps} width={props.width} height={props.height}/>;
