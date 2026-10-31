# Fifth channel candidate v2: partial acceptance

Branch: `codex/rebuild-production-v2`. Existing remote repository
`ahmedalsharqwi2-gif/stickman-what-if-shorts` was verified with `git ls-remote`;
no duplicate GitHub repository was created. The existing demo and acting prototype
were preserved, and no schedule or social publisher was enabled.

The local review is `out/candidate-v2-visual-review.mp4`:

- 120.000 seconds; 1080×1920; H.264; 24 fps; 2,880 decoded frames.
- 6,346,222 bytes; SHA-256 `91a710cfcd02b22b95ba37edada529dc908e9c4120bb05fc493bbf8f70728e68`.
- Full independent `ffmpeg -v error -xerror -i ... -f null -` decode passed.
- Actual MP4 frames at 2, 60 and 118 seconds were extracted and visually inspected.
  See [contact sheet](candidate-v2-contact.jpg): Arabic is shaped, text is inside
  the safe area, independent actors/props move, and the explicit review notice
  remains visible. This is perspective 2D character animation, not a claim of
  physically based 3D rendering.
- Seven tests passed, covering immutable outputs, required narration, duration,
  within-scene movement, timeline boundaries, Arabic shaping and safe text widths.

**This review has no audio stream.** It is explicitly marked as a silent visual
review, and its manifest says `publishable: false`. No synthetic tone or silent
track is substituted for Arabic narration. No new production episode, narration
quality, measured subtitle timing, music mix or publishing receipt is claimed.
The checked-in JSON records this actual review; newer candidate manifests name
narration presence separately from semantic verification.

The manual `candidate-v2-review.yml` can render and upload a review artifact.
It has not been dispatched or claimed successful remotely. No public artifact
URL is available from this local test. Full narrated production acceptance
requires Gemini/original Arabic narration and completed publishing integration;
therefore no old workflow is retired and this candidate is not activated.
