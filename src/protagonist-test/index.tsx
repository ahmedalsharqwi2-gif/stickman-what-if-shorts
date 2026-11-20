import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {ProtagonistTest} from './Scene';

registerRoot(() => (<>
  <Composition id="ProtagonistTest" component={ProtagonistTest as any} width={1080} height={1920} fps={30} durationInFrames={30} />
</>));
