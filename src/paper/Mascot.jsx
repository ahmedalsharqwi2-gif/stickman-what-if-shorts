import React from 'react';
import {interpolate} from 'remotion';

// Paper-presenter protagonist v4: rage-comic / meme stickman (owner reference
// reel "ستيك مان في أول يوم عمل", 2026-11-19; replaces v3's plain face).
// White head with thick dark outline, white-sclera eyes with outlined eyelids
// (per-expression lid position), iris+pupil with highlight, thin expressive
// brows, shaped mouths (grin/smirk/wail/gritted/oval...), oval feet, soft
// drop shadow, optional sweat drops. No hair curl (off for this look).
// Same 12-expression / 8-action contract as v2/v3 - drawplan schema unchanged.

export const CHARACTER_COLORS = {skin: '#FFFFFF', line: '#101719', tongue: '#E23B2E'};
export const EXPRESSIONS = ['smile', 'shock', 'tired', 'angry', 'curious', 'sad', 'proud', 'scared', 'laugh', 'wink', 'confused', 'determined'];
export const ACTIONS = ['walk', 'run', 'jump', 'fall', 'point', 'turn', 'hang', 'sleep'];

// Rig geometry: origin between the feet; head center at (0, -150), r=116.
// Total height ~620 units before scale. Same anchors as v2/v3.

// Mouth shapes. kind: 0 grin, 1 open oval (shock/scared), 2 gritted teeth,
// 3 small smile, 4 frown, 5 flat line, 6 open laugh, 7 slanted line (confused),
// 8 asymmetric smirk, 9 wail (teeth + tongue)
const Mouth = ({kind}) => {
  const L = CHARACTER_COLORS.line;
  if (kind === 1) return <ellipse cx="0" cy="-84" rx="26" ry="34" fill={L} />;
  if (kind === 2) return (
    <g>
      <path d="M-48 -100 L48 -100 L44 -64 L-44 -64 Z" fill="white" stroke={L} strokeWidth="7" strokeLinejoin="round" />
      <path d="M-16 -100 L-16 -64 M16 -100 L16 -64" stroke={L} strokeWidth="5" fill="none" />
    </g>
  );
  if (kind === 3) return <path d="M-32 -76 Q0 -54 32 -76" fill="none" stroke={L} strokeWidth="9" strokeLinecap="round" />;
  if (kind === 4) return <path d="M-42 -56 Q0 -84 42 -56" fill="none" stroke={L} strokeWidth="9" strokeLinecap="round" />;
  if (kind === 5) return <path d="M-32 -70 L32 -70" fill="none" stroke={L} strokeWidth="9" strokeLinecap="round" />;
  if (kind === 6) return <path d="M-46 -88 Q0 -18 46 -88 Z" fill={L} />;
  if (kind === 7) return <path d="M-30 -64 L30 -76" fill="none" stroke={L} strokeWidth="9" strokeLinecap="round" />;
  if (kind === 8) return <path d="M-48 -80 Q4 -48 44 -88" fill="none" stroke={L} strokeWidth="9" strokeLinecap="round" />;
  if (kind === 9) return (
    <g>
      <path d="M-34 -108 Q0 -116 34 -108 Q40 -62 0 -52 Q-40 -62 -34 -108 Z" fill={L} />
      <path d="M-30 -104 Q0 -112 30 -104 L28 -92 Q0 -98 -28 -92 Z" fill="white" />
      <ellipse cx="0" cy="-64" rx="18" ry="9" fill={CHARACTER_COLORS.tongue} />
    </g>
  );
  // default: big open grin curve
  return <path d="M-52 -82 Q0 -32 52 -82" fill="none" stroke={L} strokeWidth="10" strokeLinecap="round" />;
};

// expression -> [mouthKind, browDy, browTilt, lidT, pupilR, browAsym, sweat]
// lidT: 0 = wide open, 1 = fully closed. pupilR: iris radius.
// browTilt > 0: inner ends down (angry); < 0: inner ends up (sad/scared).
const EXPR = [
  [0, 0, 0, 0, 16, 0, 0],       // smile
  [1, -12, 0, 0, 9, 0, 0],      // shock (small pupils)
  [5, 6, 0, 0.55, 14, 0, 0],    // tired (heavy lids)
  [2, 14, 26, 0.3, 14, 0, 0],   // angry
  [3, -4, 0, 0, 16, -14, 0],    // curious (one brow up)
  [4, 6, -14, 0.3, 14, 0, 0],   // sad
  [8, -4, 6, 0.42, 15, 0, 0],   // proud (smirk + half lid - the smug face)
  [1, -8, -12, 0, 9, 0, 1],     // scared (small pupils + sweat)
  [6, -6, 0, 1, 16, 0, 0],      // laugh (eyes closed)
  [0, 0, 0, 0, 16, 0, 0],       // wink (right eye closed)
  [7, 2, 0, 0.15, 14, -12, 0],  // confused
  [5, 8, 18, 0.3, 14, 0, 0],    // determined
];

// One eye: white sclera + lid cap + iris with highlight, or a closed arc.
const Eye = ({cx, cy, lidT, pupilR, gx, closed}) => {
  const L = CHARACTER_COLORS.line;
  if (closed) return <path d={`M${cx - 26} ${cy} Q${cx} ${cy + 24} ${cx + 26} ${cy}`} fill="none" stroke={L} strokeWidth="9" strokeLinecap="round" />;
  const RX = 34, RY = 46;
  const lidY = cy - RY + lidT * 78;
  return (
    <g>
      <ellipse cx={cx} cy={cy} rx={RX} ry={RY} fill="white" stroke={L} strokeWidth="7" />
      <circle cx={cx + gx} cy={cy + 4} r={pupilR} fill={L} />
      <circle cx={cx + gx + pupilR * 0.35} cy={cy + 4 - pupilR * 0.35} r={Math.max(2.5, pupilR * 0.28)} fill="white" />
      {lidT > 0.02 && (
        <g>
          <path d={`M${cx - RX - 4} ${cy - RY - 4} L${cx + RX + 4} ${cy - RY - 4} L${cx + RX + 4} ${lidY} Q${cx} ${lidY + 12} ${cx - RX - 4} ${lidY} Z`} fill="white" stroke="none" />
          <path d={`M${cx - RX} ${lidY} Q${cx} ${lidY + 12} ${cx + RX} ${lidY}`} fill="none" stroke={L} strokeWidth="7" strokeLinecap="round" />
        </g>
      )}
    </g>
  );
};

const Sweat = () => (
  <g fill="#7FB7D6" stroke={CHARACTER_COLORS.line} strokeWidth="3">
    <path d="M128 -240 Q136 -224 128 -214 Q120 -224 128 -240 Z" />
    <path d="M150 -200 Q158 -184 150 -174 Q142 -184 150 -200 Z" />
    <path d="M-140 -228 Q-132 -212 -140 -202 Q-148 -212 -140 -228 Z" />
  </g>
);

export const MascotRig = ({frame, expression = 0, action = 'point', gazeX = 10}) => {
  const t = frame / 30, speed = action === 'run' ? 14 : 6, walk = ['walk', 'run'].includes(action) ? Math.sin(t * speed) * 20 : 0;
  // Animation principles: idle blink every ~3.5s, arms counter-swing the legs,
  // jump gets a short anticipation crouch before takeoff.
  const blink = ((frame + 52) % 105) < 3;
  const jumpPhase = (t * 4) % (Math.PI * 2);
  const jumpY = jumpPhase < 0.5 ? 16 * Math.sin(jumpPhase / 0.5 * Math.PI) : -Math.abs(Math.sin(t * 4)) * 95;
  const y = action === 'jump' ? jumpY : action === 'hang' ? Math.sin(t * 3) * 12 : 0;
  const rotation = action === 'fall' ? Math.min(85, t * 90) : action === 'sleep' ? 85 : action === 'turn' ? Math.sin(t * 2) * 9 : 0;
  const e = EXPR[expression] || EXPR[0];
  const [mouthKind, browDy, browTilt, lidT, pupilR, browAsym, sweat] = e;
  const sleeping = action === 'sleep';
  const L = CHARACTER_COLORS.line;
  const BODY = 26;
  const eyesClosed = sleeping || blink;
  const gx = eyesClosed ? 0 : gazeX;
  // Stickman body: spine, legs from hips, arms from shoulder point on the spine.
  const spine = 'M0 -34 L0 130';
  const legs = `M0 130 L${-50 + walk} 268 M0 130 L${50 - walk} 268`;
  const armL = `M0 -2 Q${-96} ${action === 'hang' ? -200 : 40 - walk} ${-118} ${action === 'hang' ? -260 : -58}`;
  const armR = action === 'point'
    ? 'M0 -2 Q82 -62 124 -110'
    : `M0 -2 Q96 ${action === 'hang' ? -200 : 44 - walk} 118 ${action === 'hang' ? -260 : 24}`;
  const bL = browDy + browAsym, bR = browDy;
  return (
    <g transform={`translate(0 ${y}) rotate(${rotation})`} strokeLinecap="round" strokeLinejoin="round">
      {/* drop shadow */}
      <ellipse cx="0" cy="296" rx="120" ry="16" fill="#101719" opacity="0.10" stroke="none" />
      {/* body lines */}
      <path d={spine} fill="none" stroke={L} strokeWidth={BODY} />
      <path d={legs} fill="none" stroke={L} strokeWidth={BODY} />
      {/* oval feet */}
      <ellipse cx={-56 + walk} cy="270" rx="28" ry="11" fill={L} stroke="none" />
      <ellipse cx={56 - walk} cy="270" rx="28" ry="11" fill={L} stroke="none" />
      <path d={armL} fill="none" stroke={L} strokeWidth={BODY} />
      <path d={armR} fill="none" stroke={L} strokeWidth={BODY} />
      {/* head */}
      <circle cx="0" cy="-150" r="116" fill={CHARACTER_COLORS.skin} stroke={L} strokeWidth="11" />
      {/* eyes */}
      <Eye cx={-46} cy={-164} lidT={eyesClosed ? 1 : lidT} pupilR={pupilR} gx={gx} closed={eyesClosed} />
      <Eye cx={46} cy={-164} lidT={eyesClosed || expression === 9 ? 1 : lidT} pupilR={pupilR} gx={gx} closed={eyesClosed || expression === 9} />
      {/* brows */}
      {!eyesClosed && (
        <g stroke={L} strokeWidth="10" fill="none">
          <path d={`M-80 ${-232 + bL - browTilt} L-24 ${-232 + bL + browTilt}`} />
          <path d={`M24 ${-232 + bR + browTilt} L80 ${-232 + bR - browTilt}`} />
        </g>
      )}
      {sweat ? <Sweat /> : null}
      <Mouth kind={mouthKind} />
    </g>
  );
};

// Choreographed presenter: walks in from offscreen to (x, y), then performs
// the beats list: [{frame, action, expression, duration}] in absolute frames;
// outside beats he idles with a subtle bob.
export const Mascot = ({frame, x, y, scale = 0.55, enterFrame = 0, beats = [], idleExpression = 0}) => {
  const enterDur = 45;
  const enter = interpolate(frame, [enterFrame, enterFrame + enterDur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (enter <= 0) return null;
  const entering = enter < 1;
  const current = beats.filter(b => frame >= b.frame).pop();
  const action = entering ? 'walk' : (current?.action || 'idle');
  const expression = entering ? 0 : (current?.expression ?? idleExpression);
  const bob = entering || action !== 'idle' ? 0 : Math.sin(frame / 30 * 1.6) * 6;
  const px = interpolate(enter, [0, 1], [1080 + 260, x]);
  return (
    <g transform={`translate(${px} ${y + bob}) scale(${scale})`}>
      <MascotRig frame={frame} action={action === 'idle' ? 'point' : action} expression={expression} />
    </g>
  );
};
