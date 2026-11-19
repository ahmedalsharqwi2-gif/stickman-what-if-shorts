// One-off character-sheet generator: builds expressions.png and poses.png grids
// from public/character/reference.png via Gemini image generation. Run manually
// once the GEMINI_API_KEY secret exists:  node pipeline/character-sheet.mjs
// Review the grids by hand; only then are they locked as generation references.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {provider} from './provider-client.mjs';
import {loadStickmanStyle} from './stickman-style.mjs';
const sheets=[
 {file:'expressions.png',prompt:'Using the attached character reference, draw the exact same character in a 3x4 expression grid (12 panels, plain white background, no text): smile, shock, tired, angry, curious, sad, proud, scared, laugh, wink, confused, determined. Same colors, same thick black outlines, same flat cartoon style, head and shoulders per panel.'},
 {file:'poses.png',prompt:'Using the attached character reference, draw the exact same character in a 2x4 pose grid (8 panels, plain white background, no text): walk, run, jump, fall, point, turn, hang, sleep. Full body per panel, same colors, same thick black outlines, same flat cartoon style.'},
];
const style=await loadStickmanStyle();
if(!style)throw Error('MISSING_STYLE_CONFIG');
const reference=(await readFile('public/'+style.referenceImage)).toString('base64');
const client=await provider();
await mkdir('public/character',{recursive:true});
for(const sheet of sheets){
 const response=await client.generate('image',{contents:[{parts:[{inlineData:{mimeType:'image/png',data:reference}},{text:sheet.prompt}]}],generationConfig:{responseModalities:['TEXT','IMAGE']}},{settings:{styleVersion:3,aspectRatio:'1:1'},useCache:false});
 const part=response.candidates[0].content.parts.find(p=>p.inlineData?.mimeType?.startsWith('image/'))?.inlineData;
 if(!part||!['image/png','image/jpeg','image/webp'].includes(part.mimeType))throw Error('SHEET_PROVIDER_NO_SUPPORTED_IMAGE');
 await writeFile('public/character/'+sheet.file,Buffer.from(part.data,'base64'));
 console.log('wrote public/character/'+sheet.file+' via '+response._pipeline.model);
}
