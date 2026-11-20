import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {MascotRig, EXPRESSIONS} from '../paper/Mascot.jsx';

const T = {paper:'#EDE4D0', ink:'#1A1512', grid:'#D8CBB2', red:'#B03A2E', orange:'#E0A458', gold:'#C99700'};
const fontFamily = 'ChannelArabic, Cairo, sans-serif';

const Flame = ({x, y, s, f}: {x:number;y:number;s:number;f:number}) => (
  <g transform={`translate(${x},${y}) scale(${s})`}>
    <path d={`M0 0 Q-14 -${22+f%7} 0 -${44+f%9} Q14 -${22+f%5} 0 0 Z`} fill={T.orange} opacity={0.85}/>
    <path d={`M0 -6 Q-8 -${16+f%6} 0 -${30+f%8} Q8 -${16+f%4} 0 -6 Z`} fill={T.gold} opacity={0.9}/>
  </g>
);

const PaperBg = () => (
  <svg width="1080" height="1920" style={{position:'absolute'}}>
    {Array.from({length:25},(_,i)=>(<line key={'h'+i} x1="0" y1={i*80} x2="1080" y2={i*80} stroke={T.grid} strokeWidth="1"/>))}
    {Array.from({length:14},(_,i)=>(<line key={'v'+i} x1={i*80} y1="0" x2={i*80} y2="1920" stroke={T.grid} strokeWidth="1"/>))}
  </svg>
);

// Face-system contact sheet: all 12 expressions, 3x4 grid, labeled.
const FaceGrid = () => (
  <AbsoluteFill style={{background: T.paper, direction: 'rtl'}}>
    <PaperBg />
    <div style={{position:'absolute', top:70, width:'100%', textAlign:'center', fontFamily, fontWeight:800, fontSize:54, color:T.ink}}>شخصية الستيك مان - نظام الوجوه</div>
    <svg width="1080" height="1920" style={{position:'absolute'}}>
      {EXPRESSIONS.map((name, i) => {
        const col = i % 3, row = Math.floor(i / 3);
        const cx = 190 + col * 350, cy = 480 + row * 380;
        return (
          <g key={name} transform={`translate(${cx},${cy}) scale(0.62)`}>
            <MascotRig frame={0} expression={i} action="point" />
          </g>
        );
      })}
    </svg>
    {EXPRESSIONS.map((name, i) => {
      const col = i % 3, row = Math.floor(i / 3);
      const cx = 190 + col * 350, cy = 480 + row * 380;
      return (
        <div key={'l'+name} style={{position:'absolute', left:cx-120, top:cy+130, width:240, textAlign:'center', fontFamily, fontWeight:700, fontSize:30, color:T.ink}}>{i} - {name}</div>
      );
    })}
  </AbsoluteFill>
);

export const ProtagonistTest = ({expression=1, action='fall', flames=true, grid=false, caption='الأرض بتولّع تحته', title='ماذا لو الأرض ولّعت تحتيك؟'}: any) => {
  const frame = useCurrentFrame();
  if (grid) return <FaceGrid />;
  return (
    <AbsoluteFill style={{background: T.paper, direction: 'rtl'}}>
      <PaperBg />
      <div style={{position:'absolute', top:110, width:'100%', textAlign:'center', fontFamily, fontWeight:800, fontSize:58, color:T.ink, padding:'0 60px'}}>{title}</div>
      <svg width="1080" height="1920" style={{position:'absolute'}}>
        {flames && (<g>
          <ellipse cx="540" cy="1550" rx="360" ry="52" fill={T.red} opacity={0.3}/>
          {[280,370,460,550,640,730,810].map((x,i)=>(<Flame key={i} x={x} y={1545} s={1.5+(i%3)*0.35} f={i*13}/>))}
          {[330,430,540,650,750].map((x,i)=>(<Flame key={'b'+i} x={x} y={1580} s={1.1+(i%2)*0.3} f={i*29}/>))}
        </g>)}
        <g transform="translate(540,1250) scale(1.2)">
          <MascotRig frame={frame} expression={expression} action={action} />
        </g>
        {flames && (<g>
          {[360,470,610,720].map((x,i)=>(<Flame key={'f'+i} x={x} y={1620} s={0.9+(i%2)*0.25} f={i*17}/>))}
        </g>)}
      </svg>
      <div style={{position:'absolute', bottom:170, width:'100%', display:'flex', justifyContent:'center', padding:'0 50px'}}>
        <div style={{fontFamily, fontWeight:700, fontSize:44, color:T.ink, background:'rgba(255,255,255,0.75)', borderRadius:18, padding:'10px 28px', border:`2px solid ${T.grid}`}}>{caption}</div>
      </div>
    </AbsoluteFill>
  );
};
