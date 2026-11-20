import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {XMLParser} from 'fast-xml-parser';

// Compile only this repository's trusted, deterministic rig. No generated code,
// external attachments or provider output are evaluated by these tests.
function compile(file){
 const source=readFileSync(file,'utf8');
 const compiled=ts.transpileModule(source,{fileName:file,reportDiagnostics:true,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.React,esModuleInterop:true}});
 assert.equal((compiled.diagnostics||[]).filter(d=>d.category===ts.DiagnosticCategory.Error).length,0,file);
 return compiled.outputText;
}
function loadModule(file,extra={}){
 const module={exports:{}};
 const local=createRequire(file);
 const customRequire=id=>extra[id]||local(id);
 Function('require','module','exports',compile(file))(customRequire,module,module.exports);
 return module.exports;
}
// Remotion is stubbed: the rig only needs deterministic interpolate.
const interpolate=(x,inp,out,{extrapolateLeft,extrapolateRight}={})=>{
 const r=(x-inp[0])/(inp[1]-inp[0]);let v=out[0]+(out[1]-out[0])*r;
 if(extrapolateLeft==='clamp')v=Math.max(v,Math.min(...out));
 if(extrapolateRight==='clamp')v=Math.min(v,Math.max(...out));
 return v;
};
const rigFile=path.resolve('src/paper/Mascot.jsx');
const rig=loadModule(rigFile,{remotion:{interpolate}});
const characterFile=path.resolve('src/Character.tsx');
const {Character,CHARACTER_COLORS,EXPRESSIONS,ACTIONS}=loadModule(characterFile,{'./paper/Mascot.jsx':rig,remotion:{interpolate}});
const bible=JSON.parse(readFileSync('config/character.json','utf8'));
const baseline=JSON.parse(readFileSync('tests/fixtures/character-engineering-baseline.json','utf8'));
const parser=new XMLParser({ignoreAttributes:false,attributeNamePrefix:'@',parseAttributeValue:true});
const list=x=>Array.isArray(x)?x:[x];
const hash=text=>createHash('sha256').update(text).digest('hex');
function render(expression=0,action='point',frame=45){return renderToStaticMarkup(React.createElement('svg',{viewBox:'0 0 1080 1920'},React.createElement(Character,{expression,action,frame})));}
function geometry(action,frame){const svg=render(0,action,frame);const g=parser.parse(svg).svg.g.g||parser.parse(svg).svg.g;return {transform:g['@transform'],markup:svg.length+':'+hash(svg).slice(0,16)};}

test('stickman palette and fixed geometry agree with the declared character bible',()=>{
 assert.equal(CHARACTER_COLORS.skin,bible.head.skin);assert.equal(CHARACTER_COLORS.line,bible.head.stroke);
 assert.deepEqual(EXPRESSIONS,bible.expressions);assert.deepEqual(ACTIONS,bible.actions);
 for(const expression of EXPRESSIONS.keys())for(const action of ACTIONS){
  const svg=render(expression,action,45);assert.doesNotMatch(svg,/NaN|Infinity|undefined/);
  const head=list(parser.parse(svg).svg.g.g.circle).find(c=>c['@r']===bible.head.radius);
  assert(head,'head circle present');assert.equal(head['@fill'],bible.head.skin);assert.equal(head['@stroke'],bible.head.stroke);assert.equal(head['@stroke-width'],bible.head.strokeWidth);
  assert.equal(head['@cx'],0);assert.equal(head['@cy'],-150);assert.equal(head['@r']*2,bible.proportions.headDiameter);
  assert.match(svg,/stroke-width="26"/,'stick body lines present');
 }
});

test('all twelve expressions are distinct and preserve frozen engineering fingerprints',()=>{
 const fingerprints=Object.fromEntries(EXPRESSIONS.map((name,i)=>[name,hash(render(i,'point',45))]));
 assert.equal(new Set(Object.values(fingerprints)).size,12);assert.deepEqual(fingerprints,baseline.expressions);
});

test('eight actions have distinct pose sequences and the moving actions change geometry',()=>{
 const frames=baseline.frames,series=Object.fromEntries(ACTIONS.map(action=>[action,frames.map(frame=>geometry(action,frame))]));
 assert.equal(new Set(Object.values(series).map(value=>JSON.stringify(value))).size,8);
 for(const action of ['walk','run','jump','fall','turn','hang'])assert(new Set(series[action].map(value=>JSON.stringify(value))).size>1,action+' must change actual body geometry');
 assert.match(geometry('sleep',45).transform,/rotate\(85\)/);assert.match(geometry('fall',0).transform,/rotate\(0\)/);
 const fingerprints=Object.fromEntries(ACTIONS.map(action=>[action,hash(JSON.stringify(series[action]))]));assert.deepEqual(fingerprints,baseline.actions);
});

test('animation principles: idle blink and jump anticipation are active',()=>{
 // Blink: frame 53 (first blink window, (53+52)%105===0) differs from frame 45.
 assert.notEqual(hash(render(0,'point',53)),hash(render(0,'point',45)));
 // Jump anticipation: frame 3 crouches (positive y) before takeoff (frame 12 airborne, negative y).
 const yOf=f=>Number(/translate\(0 (-?\d+)/.exec(parser.parse(render(0,'jump',f)).svg.g.g['@transform'])[1]);
 assert(yOf(3)>0,'crouch');assert(yOf(12)<0,'airborne');
});

test('engineering baseline is explicitly not owner approval or similarity proof',()=>{
 assert.equal(baseline.ownerApproved,false);assert.equal(baseline.referenceVideoParityAssessed,false);assert.match(baseline.purpose,/engineering regression/i);
});
