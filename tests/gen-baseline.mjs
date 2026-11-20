// One-off generator for tests/fixtures/character-engineering-baseline.json.
// Run: node tests/gen-baseline.mjs
import {readFileSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {XMLParser} from 'fast-xml-parser';

function compile(file){
 const compiled=ts.transpileModule(readFileSync(file,'utf8'),{fileName:file,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.React,esModuleInterop:true}});
 return compiled.outputText;
}
function loadModule(file,extra={}){
 const module={exports:{}};const local=createRequire(file);
 Function('require','module','exports',compile(file))(id=>extra[id]||local(id),module,module.exports);
 return module.exports;
}
const interpolate=(x,inp,out,{extrapolateLeft,extrapolateRight}={})=>{const r=(x-inp[0])/(inp[1]-inp[0]);let v=out[0]+(out[1]-out[0])*r;if(extrapolateLeft==='clamp')v=Math.max(v,Math.min(...out));if(extrapolateRight==='clamp')v=Math.min(v,Math.max(...out));return v;};
const rig=loadModule(path.resolve('src/paper/Mascot.jsx'),{remotion:{interpolate}});
const {Character,EXPRESSIONS,ACTIONS}=loadModule(path.resolve('src/Character.tsx'),{'./paper/Mascot.jsx':rig,remotion:{interpolate}});
const hash=t=>createHash('sha256').update(t).digest('hex');
const render=(e=0,a='point',f=45)=>renderToStaticMarkup(React.createElement('svg',{viewBox:'0 0 1080 1920'},React.createElement(Character,{expression:e,action:a,frame:f})));
const frames=[0,12,24,45,75,105];
const geometry=(a,f)=>{const svg=render(0,a,f);const g=new XMLParser({ignoreAttributes:false,attributeNamePrefix:'@',parseAttributeValue:true}).parse(svg).svg.g.g;return {transform:g['@transform'],markup:svg.length+':'+hash(svg).slice(0,16)};};
const baseline={
 schema:1,
 purpose:'Engineering regression fingerprints of the current owner-directed white stickman SVG rig (2026-11-19). Not a visual approval or comparison with any reference.',
 ownerApproved:false,
 referenceVideoParityAssessed:false,
 frames,
 proportions:{headToTorsoHeight:232/164,declaredLegLength:138},
 expressions:Object.fromEntries(EXPRESSIONS.map((n,i)=>[n,hash(render(i,'point',45))])),
 actions:Object.fromEntries(ACTIONS.map(a=>[a,hash(JSON.stringify(frames.map(f=>geometry(a,f))))])),
};
writeFileSync('tests/fixtures/character-engineering-baseline.json',JSON.stringify(baseline,null,1));
console.log('baseline written');
