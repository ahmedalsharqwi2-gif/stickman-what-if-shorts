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
const file=path.resolve('src/Character.tsx');
const compiled=ts.transpileModule(readFileSync(file,'utf8'),{fileName:file,reportDiagnostics:true,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.React,esModuleInterop:true}});
assert.equal((compiled.diagnostics||[]).filter(d=>d.category===ts.DiagnosticCategory.Error).length,0);
const module={exports:{}};
Function('require','module','exports',compiled.outputText)(createRequire(file),module,module.exports);
const {Character,CHARACTER_COLORS,EXPRESSIONS,ACTIONS}=module.exports;
const bible=JSON.parse(readFileSync('config/character.json','utf8'));
const baseline=JSON.parse(readFileSync('tests/fixtures/character-engineering-baseline.json','utf8'));
const parser=new XMLParser({ignoreAttributes:false,attributeNamePrefix:'@',parseAttributeValue:true});
const list=x=>Array.isArray(x)?x:[x];
const hash=text=>createHash('sha256').update(text).digest('hex');
function render(expression=0,action='point',frame=45){return renderToStaticMarkup(React.createElement('svg',{viewBox:'0 0 1080 1920'},React.createElement(Character,{expression,action,frame})));}
function geometry(action,frame){const g=parser.parse(render(0,action,frame)).svg.g,paths=list(g.path);return {transform:g['@transform'],legs:paths.find(p=>p['@stroke-width']===48)?.['@d'],arms:paths.find(p=>p['@stroke-width']===50)?.['@d']};}

test('character palette and fixed geometry agree with the declared character bible',()=>{
 assert.deepEqual(CHARACTER_COLORS,{skin:bible.head.skin,shirt:bible.shirt.color,line:bible.head.stroke});
 assert.deepEqual(EXPRESSIONS,bible.expressions);assert.deepEqual(ACTIONS,bible.actions);
 for(const expression of EXPRESSIONS.keys())for(const action of ACTIONS){
  const svg=render(expression,action,45);assert.doesNotMatch(svg,/NaN|Infinity|undefined/);
  const g=parser.parse(svg).svg.g,head=list(g.circle).find(c=>c['@r']===bible.head.radius),paths=list(g.path);
  assert.equal(g['@stroke'],bible.head.stroke);assert.equal(g['@stroke-width'],bible.head.strokeWidth);
  assert.equal(head['@fill'],bible.head.skin);assert.equal(head['@cx'],0);assert.equal(head['@cy'],-150);
  assert.equal(head['@r']*2,bible.proportions.headDiameter);
  assert(paths.some(p=>p['@fill']===bible.shirt.color&&p['@d']==='M-65 -30 L-105 135 Q0 165 105 135 L65 -30Z'));
  assert(paths.some(p=>p['@stroke-width']===48));assert(paths.some(p=>p['@stroke-width']===50));
  assert(paths.some(p=>p['@stroke']===bible.limbs.color&&p['@stroke-width']===32));
 }
 // Quadratic shirt hem reaches y=150, from shoulder y=-30: body height=180.
 assert.equal(bible.proportions.bodyHeight,180);
 assert.equal(bible.proportions.headDiameter/bible.proportions.bodyHeight,baseline.proportions.headToTorsoHeight);
 assert.equal(bible.proportions.legLength,baseline.proportions.declaredLegLength);
});

test('all twelve expressions are distinct and preserve frozen engineering fingerprints',()=>{
 const fingerprints=Object.fromEntries(EXPRESSIONS.map((name,i)=>[name,hash(render(i,'point',45))]));
 assert.equal(new Set(Object.values(fingerprints)).size,12);assert.deepEqual(fingerprints,baseline.expressions);
});

test('eight actions have distinct pose sequences and the moving actions change geometry',()=>{
 const frames=baseline.frames,series=Object.fromEntries(ACTIONS.map(action=>[action,frames.map(frame=>geometry(action,frame))]));
 assert.equal(new Set(Object.values(series).map(value=>JSON.stringify(value))).size,8);
 for(const action of ['walk','run','jump','fall','turn','hang'])assert(new Set(series[action].map(value=>JSON.stringify(value))).size>1,action+' must change actual body geometry');
 assert.match(geometry('point',45).arms,/190 -110$/);assert.match(geometry('hang',45).arms,/190 -280$/);
 assert.match(geometry('sleep',45).transform,/rotate\(85\)/);assert.match(geometry('fall',0).transform,/rotate\(0\)/);
 const fingerprints=Object.fromEntries(ACTIONS.map(action=>[action,hash(JSON.stringify(series[action]))]));assert.deepEqual(fingerprints,baseline.actions);
});

test('engineering baseline is explicitly not owner approval or similarity proof',()=>{
 assert.equal(baseline.ownerApproved,false);assert.equal(baseline.referenceVideoParityAssessed,false);assert.match(baseline.purpose,/engineering regression/i);
});
