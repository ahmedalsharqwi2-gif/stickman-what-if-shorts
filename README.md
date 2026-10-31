# تخيل لو! | Stickman What If

Independent stick-figure animation factory. No changes to the four existing video repositories.

## Quick start
Install Python 3.11+, FFmpeg and `pip install -r requirements.txt`.
Run `python -m stickman.factory --demo` for a 12-second non-publishable MP4 at `out/video.mp4`.
Run `pytest -q` for unit checks.

GitHub Actions workflow builds and uploads a demo artifact manually. It does NOT publish.
The real 3–5-minute Gemini/Charon production pipeline, Buffer credentials, cinematic scenes and publishing receipts remain to be implemented and verified. Never publish a demo.

## Opt-in v2 candidate (new development branch)

The existing GitHub repository already provides the fifth channel; no replacement
repository or duplicate channel was created. Legacy prototypes are preserved.
The candidate adds perspective staging, independent foreground/background
parallax, a moving camera, soft contact shadows, articulated acting, and Arabic
scene text inside the vertical safe area. Arabic text uses the included original
Noto font and requires Pillow with RAQM support.

```sh
python -m pytest -q
python -m stickman.candidate --visual-review --duration 120 --fps 24 --output out/review-unique-name.mp4
```

This command produces a **silent, nonpublishable visual review**, not a completed
narrated episode. The review watermark states that narration is absent. It has
no silent audio track masquerading as narration. Full FFmpeg decode, dimensions,
duration and a SHA-256 manifest are validated before the final file appears.
An existing output is never overwritten. `candidate-v2-review.yml` is manual
only and uploads this clearly named review artifact; it has no cron or publisher.

To exercise narration muxing, supply a verified original Arabic narration file
of the same duration with `--narration PATH` instead of `--visual-review`.
Narration generation, semantic verification, measured captions, a music mix,
durable topic reservations and publishing receipts remain required before this
candidate can replace a production workflow. The manifest stays nonpublishable
even when narration is supplied. Gemini and channel publishing credentials are
not available in this environment; their absence must never be replaced with a
synthetic tone, old film, invented receipt, or duplicate social post.

No scheduled production workflow exists here to cut over yet. Neither legacy
manual prototype is disabled until the full narrated channel acceptance is
verified. Never use a prototype or silent candidate as a daily film.
