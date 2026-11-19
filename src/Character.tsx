import React from 'react';
import {MascotRig, CHARACTER_COLORS, EXPRESSIONS, ACTIONS} from './paper/Mascot.jsx';

// Classic-mode character: adapter over the paper stickman rig (owner decision
// 2026-11-19: one plain white stick figure everywhere, blue character removed
// entirely). Keeps the legacy signature (frame, expression, action) and the
// absolute placement Episode.tsx expects.
export {CHARACTER_COLORS, EXPRESSIONS, ACTIONS};
export function Character({frame, expression = 0, action = 'point'}:{frame:number;expression?:number;action?:string}){
 return (
  <g transform="translate(540 950)">
   <MascotRig frame={frame} expression={expression} action={action} />
  </g>
 );
}
