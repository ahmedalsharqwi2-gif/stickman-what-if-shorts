import React from 'react';
import {interpolate,useCurrentFrame,useVideoConfig} from 'remotion';
import type {DialogueTurn} from './types';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const Actor=({speaker,x,y,scale,active,reacting,stage}:{speaker:'a'|'b';x:number;y:number;scale:number;active:boolean;reacting:boolean;stage:string})=>{const f=useCurrentFrame();const {fps}=useVideoConfig();const t=f/fps;const right=speaker==='a';const color=right?'#192b3e':'#276c72';const blink=(f+(right?0:71))%(5*fps)<4;const gest=active?Math.sin(t*5.5):Math.sin(t*1.2)*.18;const running=stage==='escalation'||stage==='fail';const stride=running?Math.sin(t*8)*23:Math.sin(t*1.5)*3;const tilt=reacting?(right?-5:5):active?Math.sin(t*2)*2:0;return <g transform={`translate(${x} ${y}) scale(${scale}) rotate(${tilt} 0 -90)`}>
 <ellipse cx="0" cy="4" rx="54" ry="8" fill="#20344a" opacity=".1"/>
 <circle cy="-195" r="40" fill="#fff5df" stroke={color} strokeWidth="5.2"/>
 {speaker==='b'?<><path d="M-35 -213q35 -18 70 0" stroke={color} strokeWidth="7" fill="none"/><circle cx="-13" cy="-199" r="11" fill="none" stroke={color} strokeWidth="2.5"/><circle cx="13" cy="-199" r="11" fill="none" stroke={color} strokeWidth="2.5"/><path d="M-2 -199H2" stroke={color} strokeWidth="2.5"/></>:null}
 {blink?<path d="M-18 -198h10m16 0h10" stroke={color} strokeWidth="3"/>:<><circle cx={-13+(right?3:-3)} cy="-199" r="3.2" fill={color}/><circle cx={13+(right?3:-3)} cy="-199" r="3.2" fill={color}/></>}
 <path d={reacting?'M-22 -224l14 -7m16 7l14 -7':'M-22 -221h13m17 0h13'} stroke={color} strokeWidth="2.4" fill="none"/>
 {active?<ellipse cx="2" cy="-179" rx={7+Math.sin(t*14)*1.5} ry={3+Math.abs(Math.sin(t*19))*6} fill={color}/>:<path d={reacting?'M-7 -176q10 -10 20 0':'M-9 -178q10 5 20 -1'} stroke={color} strokeWidth="2.6" fill="none"/>}
 <path d={`M0 -154L${running?8:0} -80L${-32+stride} -2M${running?8:0} -80L${34-stride} -2M0 -140L-35 ${-102-gest*18}L-68 ${-116-gest*26}M0 -140L38 ${-110+gest*15}L73 ${-152+gest*26}`} stroke={color} strokeWidth="6.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
 <circle cx="-68" cy={-116-gest*26} r="7" fill="#e3b65d" stroke={color} strokeWidth="1.7"/><circle cx="73" cy={-152+gest*26} r="7" fill={speaker==='a'?'#e3b65d':'#8fc5ba'} stroke={color} strokeWidth="1.7"/>
 {active?<path d={right?'M45 -225l18 -8m-15 24l20 0':'M-45 -225l-18 -8m15 24l-20 0'} stroke={right?'#bd7756':'#438d8e'} strokeWidth="2.3" opacity=".7"/>:null}
 </g>};
export const DuoActors=({turns,sceneStart,scenario,stage}:{turns:DialogueTurn[];sceneStart:number;scenario:string;stage:string})=>{const f=useCurrentFrame();const {fps}=useVideoConfig();const t=f/fps;const now=sceneStart+t;const turn=turns.find(item=>now>=item.start&&now<item.end);const active=turn?.speaker;const index=turn?turns.indexOf(turn):-1;const gravity=scenario==='gravity';const y=gravity?1130+Math.sin(t*.8)*35:1210;const scale=scenario==='tiny'?1.25:scenario==='giant'?1.9:1.7;const beat=turn?interpolate(now,[turn.start,Math.min(turn.end,turn.start+.35)],[0,1],clamp):0;const color=active==='b'?'#276c72':'#8e573e';const bubbleX=active==='b'?570:55;return <>
 <Actor speaker="a" x={315+Math.sin(t*.8)*10} y={y} scale={scale} active={active==='a'} reacting={active==='b'&&index%2===1} stage={stage}/>
 <Actor speaker="b" x={760+Math.cos(t*.8)*10} y={y} scale={scale} active={active==='b'} reacting={active==='a'&&index%3===0} stage={stage}/>
 {turn?<g opacity={beat}><rect x={bubbleX} y="535" width="455" height="190" rx="25" fill="#fff9eaf5" stroke={color} strokeWidth="3"/><path d={`M${bubbleX+205} 725l25 28l18 -28`} fill="#fff9ea" stroke={color} strokeWidth="3"/><foreignObject x={bubbleX+24} y="552" width="407" height="158"><div dir="rtl" lang="ar" style={{fontFamily:'Arabic',fontSize:turn.text.length>90?29:33,lineHeight:1.55,textAlign:'center',color,display:'flex',alignItems:'center',justifyContent:'center',height:158}}>{turn.text}</div></foreignObject></g>:null}
 </>};
