import React from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
// Light motion layer over a generated full-scene image: slow Ken Burns drift,
// a ±jitterPx hand-drawn wobble, and comic motion lines that flash on beat
// changes. No paid image-to-video; everything is plain Remotion transforms.
export function SubtleMotion({src,altSrc,kenBurnsPct=4,jitterPx=1,motionLines=true,swapFrames=0,accent='#ffda34',line='#12bce5'}:{src:string;altSrc?:string;kenBurnsPct?:number;jitterPx?:number;motionLines?:boolean;swapFrames?:number;accent?:string;line?:string}){
 const f=useCurrentFrame(),{durationInFrames}=useVideoConfig();
 const t=f/30,zoom=1+(kenBurnsPct/100)*(f/Math.max(1,durationInFrames));
 const jx=jitterPx?Math.sin(t*2.1)*jitterPx:0,jy=jitterPx?Math.cos(t*1.7)*jitterPx:0;
 const showAlt=altSrc&&swapFrames>0&&Math.floor(f/swapFrames)%2===1;
 const beat=Math.floor(f/90),flash=motionLines&&f%90<14;
 return <AbsoluteFill style={{overflow:'hidden'}}>
  <Img src={staticFile(showAlt?altSrc:src)} style={{width:'100%',height:'100%',objectFit:'cover',transform:`scale(${zoom}) translate(${jx}px, ${jy}px)`}}/>
  {flash&&<svg width="1080" height="1920" style={{position:'absolute',inset:0,pointerEvents:'none'}}>
   {[0,1,2].map(i=>{const y=420+i*90+((beat*53)%40);const left=beat%2===0;
    return <g key={i} stroke={i%2?line:accent} strokeWidth={16-i*3} strokeLinecap="round" opacity={0.85-i*0.18}>
     <line x1={left?70+i*40:1010-i*40} y1={y} x2={left?190+i*40:890-i*40} y2={y}/>
    </g>;})}
  </svg>}
 </AbsoluteFill>;
}
