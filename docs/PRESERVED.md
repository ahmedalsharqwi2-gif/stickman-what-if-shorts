# Preserved materials

All listed bytes preserved at their original paths, except the Nafhamha identity receives a new rebuild_tokens member and its exact original is saved beside it as nafhamha-identity.original.json. The full original source remains on the verified backup branch and tag. Additional extracted topic identifiers are in state/legacy-topic-index.json; new reservations never overwrite that index.

| Original path | SHA256 before rebuild |
|---|---|
| `config/channel_identity.json` | `53574f337a2e8de2e7e8c77a03758c6d250b05f226372bc39a34554f47b0219e` |
| `assets/fonts/Noto-Fonts-Copyright.txt` | `075f91382875da1c4b491f1facf2586f55448705133264d98ce15cab6211b125` |
| `assets/fonts/NotoSansArabic-Bold.ttf` | `ded6fc7359ca36d15d7aab9ef0c066e21ce48b26a069994d6602fa2cb9a1b952` |
| `remotion_motion/public/fonts/Arabic-Bold.ttf` | `ded6fc7359ca36d15d7aab9ef0c066e21ce48b26a069994d6602fa2cb9a1b952` |
| `remotion_motion/public/fonts/Arabic-Regular.ttf` | `504d7407d86875acf7d04dfaa0fd7524d0b8797723bc4aa18022f29db25b0b6e` |

Original logo present in checkout: no. The owner subsequently supplied inline logo references. Their original file bytes have not been exposed by the upload tool; no replacement has been drawn. See config/logo-intake.json. Original font files and their available notices remain. Charon and intended 17:00 Africa/Cairo destination names remain in config. No .mp4 files were tracked on the cloned main snapshots; no approved media was deleted from remote media branches. Legacy scheduling files are in the backup, but the new branch has only one active workflow.

## Follow-up original logo installation

Source: Owner supplied logos.zip / stickman-what-if-shorts.jpg

Canonical file: `brand/logo/logo.jpg`

SHA-256: `29806778333572189dfe658c3fb4cd3b289b9d0a4c9c87f94d8758b4c66e934b`

Byte-for-byte copy verified; no redraw, recolor, background removal, raster edit or vectorization. The public/brand/logo directory is a symlink to the canonical directory. Header, intro/outro and thumbnail use the same Logo component and source.
