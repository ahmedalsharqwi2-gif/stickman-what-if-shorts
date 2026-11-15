import React from 'react';
export const CHARACTER_COLORS={skin:'#12bce5',shirt:'#ffda34',line:'#101719'};
export const EXPRESSIONS=['smile','shock','tired','angry','curious','sad','proud','scared','laugh','wink','confused','determined'];
export const ACTIONS=['walk','run','jump','fall','point','turn','hang','sleep'];
export function Character({frame,expression=0,action='point'}:{frame:number;expression?:number;action?:string}){
 const t=frame/30,speed=action==='run'?14:6,walk=['walk','run'].includes(action)?Math.sin(t*speed)*20:0;
 const y=action==='jump'?-Math.abs(Math.sin(t*4))*95:action==='hang'?Math.sin(t*3)*12:0;
 const rotation=action==='fall'?Math.min(85,t*90):action==='sleep'?85:action==='turn'?Math.sin(t*2)*9:0;
 const eye=expression===2||action==='sleep'?2:[21,29,2,17,25,15,19,30,24,21,23,16][expression];
 const brow=[-8,-22,10,25,-18,18,-15,30,-12,0,16,-10][expression];
 const mouth=['M-42 -110 Q0 -63 42 -110','M-22 -105 Q-30 -55 0 -55 Q30 -55 22 -105Z','M-30 -80 L30 -80','M-35 -85 L35 -85','M-30 -95 Q0 -110 30 -85','M-42 -80 Q0 -120 42 -80','M-40 -110 Q10 -60 45 -112','M-22 -100 Q0 -60 22 -100Z','M-50 -110 Q0 -35 50 -110Z','M-40 -110 Q0 -70 40 -110','M-40 -85 Q-10 -105 10 -85 T45 -85','M-35 -95 Q0 -75 35 -100'][expression];
 const legs=`M-42 120 L${-50+walk} 285 l-32 5 M42 120 L${50-walk} 285 l32 5`;
 const arms=`M-75 25 Q-170 ${action==='hang'?-220:40+walk} -180 ${action==='hang'?-280:-40} M75 25 Q150 ${action==='hang'?-220:action==='point'?-60:90} 190 ${action==='hang'?-280:action==='point'?-110:30}`;
 return <g transform={`translate(540 ${950+y}) rotate(${rotation})`} stroke={CHARACTER_COLORS.line} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round">
  <path d={legs} fill="none" strokeWidth={48}/><path d={legs} fill="none" stroke={CHARACTER_COLORS.skin} strokeWidth={32}/>
  <ellipse cx={-65+walk} cy="291" rx="31" ry="15" fill="#101719"/><ellipse cx={65-walk} cy="291" rx="31" ry="15" fill="#101719"/>
  <path d="M-65 -30 L-105 135 Q0 165 105 135 L65 -30Z" fill={CHARACTER_COLORS.shirt}/>
  <path d="M-40 -23 L0 18 L40 -23 M0 18 L0 55" fill="none"/>
  <path d={arms} fill="none" strokeWidth={50}/><path d={arms} fill="none" stroke={CHARACTER_COLORS.skin} strokeWidth={34}/>
  <circle cx="0" cy="-150" r="116" fill={CHARACTER_COLORS.skin}/>
  <ellipse cx="-42" cy="-165" rx="32" ry={eye+16} fill="white" strokeWidth="7"/><ellipse cx="42" cy="-165" rx="32" ry={eye+16} fill="white" strokeWidth="7"/>
  <ellipse cx={-35+Math.sin(t)*6} cy="-160" rx="10" ry={eye} fill="#101719" stroke="none"/><ellipse cx={42+Math.sin(t)*6} cy="-160" rx="10" ry={expression===9?2:eye} fill="#101719" stroke="none"/>
  <path d={`M-77 -221 L-15 ${-221+brow} M15 ${-221+brow} L77 -221`} fill="none"/>
  {expression===1||expression===7?<ellipse cx="0" cy="-93" rx="24" ry="31" fill="#101719"/>:<path d={mouth} fill={expression===8?'white':'none'}/>}
 </g>;
}
