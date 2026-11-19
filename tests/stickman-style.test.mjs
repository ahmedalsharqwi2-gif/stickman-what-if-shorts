import {test} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {loadStickmanStyle,buildScenePrompt,buildSceneRequest,expressionName} from '../pipeline/stickman-style.mjs';

const style = JSON.parse(await (await import('node:fs/promises')).readFile('config/stickman-style.json', 'utf8'));
const scene = {title: 'ماذا لو اختفت الجاذبية', summary: 'الناس بتطير في الشارع', keyword: 'ميكروباص طاير', expression: 1};

test('style config carries the locked prompt and the channel yellow', () => {
  assert.ok(style.lockedStylePrompt.includes('sky-blue head'));
  assert.ok(style.lockedStylePrompt.includes('zigzag collar'));
  assert.ok(style.lockedStylePrompt.includes('red sneakers'));
  assert.ok(style.lockedStylePrompt.includes('9:16'));
  assert.equal(style.captionHighlight, '#ffda34');
  assert.equal(style.enabled, true);
});

test('locked prompt changes only the scene variables', () => {
  const prompt = buildScenePrompt(style, scene);
  assert.ok(prompt.startsWith(style.lockedStylePrompt));
  assert.ok(prompt.includes('الناس بتطير في الشارع'));
  assert.ok(prompt.includes('Expression: shock'));
  assert.ok(prompt.includes('Prop: ميكروباص طاير'));
});

test('scene request attaches the character reference first when present', () => {
  const withRef = buildSceneRequest(style, scene, 'QUJD');
  assert.equal(withRef.contents[0].parts[0].inlineData.data, 'QUJD');
  assert.equal(withRef.contents[0].parts[0].inlineData.mimeType, 'image/png');
  assert.equal(typeof withRef.contents[0].parts[1].text, 'string');
  const withoutRef = buildSceneRequest(style, scene, null);
  assert.equal(withoutRef.contents[0].parts.length, 1);
});

test('expression names stay aligned with the 0-11 schema', () => {
  assert.equal(style.expressionNames.length, 12);
  assert.equal(expressionName(style, 0), 'smile');
  assert.equal(expressionName(style, 7), 'scared');
  assert.equal(expressionName(style, 11), 'determined');
});

test('loadStickmanStyle returns null when the config file is missing', async () => {
  assert.equal(await loadStickmanStyle('config/does-not-exist.json'), null);
});

test('character reference image is committed', () => {
  assert.ok(existsSync('public/character/reference.png'), 'public/character/reference.png must exist (cropped from the channel logo)');
});
