import * as THREE from 'three';
import {proceduralDirector} from './procedural_story.js';
const W=1080,H=1920,renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.setClearColor(0x071625);renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;document.body.prepend(renderer.domElement);
const stage=new THREE.Scene();stage.fog=new THREE.FogExp2(0x071625,.025);stage.add(new THREE.HemisphereLight(0xc3e7ed,0x29414d,2));
for(const [color,intensity,pos] of [[0xffe4b8,3,[4,6,7]],[0x83cfdf,2,[-5,3,2]]]){const light=new THREE.DirectionalLight(color,intensity);light.position.set(...pos);stage.add(light);}
const camera=new THREE.PerspectiveCamera(42,W/H,.1,100);camera.position.set(0,1,13);
const story=await fetch('./delivery/story.json').then(r=>r.json()),timing=await fetch('./delivery/timing.json').then(r=>r.json());
const director=proceduralDirector(stage,story),canvas=document.querySelector('#text'),ctx=canvas.getContext('2d'),output=document.createElement('canvas');output.width=W;output.height=H;const final=output.getContext('2d'),review=new URLSearchParams(location.search).get('review')==='true';
function text(value,x,y,size,color,width=900){ctx.fillStyle=color;ctx.font='700 '+size+'px Noto';ctx.direction='rtl';ctx.textAlign='center';const words=String(value||'').split(' ');let line='',row=0;for(const word of words){const next=line?line+' '+word:word;if(ctx.measureText(next).width>width&&line){ctx.fillText(line,x,y+row*size*1.55);row++;line=word;}else line=next;}if(line)ctx.fillText(line,x,y+row*size*1.55);}
window.renderAt=(t,duration=timing.duration)=>{
 const index=Math.max(0,timing.scenes.findLastIndex(s=>s.start<=t)),s=timing.scenes[index],p=Math.max(0,Math.min(1,(t-s.start)/(s.end-s.start))),view=director.update(index,p,t);camera.position.set(...view.position);camera.lookAt(...view.target);renderer.render(stage,camera);
 ctx.clearRect(0,0,W,H);ctx.fillStyle='rgba(8,29,44,.93)';ctx.beginPath();ctx.roundRect(45,60,990,260,25);ctx.fill();text('افترض كده',540,120,35,'#8fd4ce');text(story.scenes[index].label,540,210,52,'#f6ce85',900);
 const caption=timing.caption_groups.find(g=>g.start<=t&&t<g.end)?.text||'';
 if(caption){ctx.fillStyle='rgba(8,29,44,.94)';ctx.beginPath();ctx.roundRect(55,1510,970,190,22);ctx.fill();text(caption,540,1588,45,'#f4f1e4',880);}
 if(review)text('عينة مراجعة، لا تُنشر تلقائيًا',540,1760,28,'#efbe74');
 text('حكاية افتراضية • رسوم توضيحية',540,1820,24,'#9ebdc5');ctx.fillStyle='#36586a';ctx.fillRect(80,1860,920,4);ctx.fillStyle='#8fd4ce';ctx.fillRect(80,1860,920*Math.min(1,t/duration),4);window.topicDirecting=view;return {scene:index+1,time:t,duration,originalVoice:true};
};window.captureFrame=()=>{final.drawImage(renderer.domElement,0,0);final.drawImage(canvas,0,0);return output.toDataURL('image/jpeg',.96).split(',')[1];};
await document.fonts.load('700 52px Noto');window.brandingStatus={profile:'stickman',logoApplied:false};window.renderAt(0);window.ready=true;
