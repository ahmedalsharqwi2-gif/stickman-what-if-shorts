import {readFile} from 'node:fs/promises';
export async function loadStickmanStyle(dir='config/stickman-style.json'){
 try{const style=JSON.parse(await readFile(dir,'utf8'));
  if(!style.lockedStylePrompt||!style.referenceImage)throw Error('STICKMAN_STYLE_INCOMPLETE');
  return style;
 }catch(e){if(e.code==='ENOENT')return null;throw e;}
}
export async function readReferenceImage(style,publicRoot='public'){
 try{const data=await readFile(publicRoot+'/'+style.referenceImage);return data.length?data.toString('base64'):null;}catch(e){if(e.code==='ENOENT')return null;throw e;}
}
export function expressionName(style,index){const names=style.expressionNames||[];return names[index]||'smile';}
export function buildScenePrompt(style,scene){
 return style.lockedStylePrompt
  +'\nScene action: '+scene.summary+'. Expression: '+expressionName(style,scene.expression)+'. Prop: '+(scene.keyword||scene.title)+'.';
}
export function buildSceneRequest(style,scene,referenceBase64){
 const parts=[{text:buildScenePrompt(style,scene)}];
 if(referenceBase64)parts.unshift({inlineData:{mimeType:'image/png',data:referenceBase64}});
 return {contents:[{parts}],generationConfig:{responseModalities:['TEXT','IMAGE']}};
}
