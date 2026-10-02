# Rebuilding the ad

`bash make_ad.sh` regenerates `marketing/findnet-ad-20s-zh.mp4` (20 s, 1080x1920,
30 fps, Mandarin narration over an original music bed, loudness -14 LUFS).

## Requirements

- Python 3.10+ with `pip install pillow numpy scipy sherpa-onnx`
- `ffmpeg`
- Fonts (SIL Open Font License, not included):
  - `fonts/Outfit-Bold.ttf` from Google Fonts, or set `FONT_DIR`
  - Noto Sans CJK `.ttc` files (`NotoSansCJK-Bold.ttc`, `-Medium`, `-Regular`);
    defaults to `/usr/share/fonts/opentype/noto`, or set `NOTO_DIR`
- Voice model (MeloTTS Chinese+English, MIT License, about 170 MB):

```bash
mkdir -p models && cd models
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2
tar xjf vits-melo-tts-zh_en.tar.bz2 && rm vits-melo-tts-zh_en.tar.bz2
```

## Build

```bash
bash make_ad.sh
```

Frames, narration clips and the mix are written to `build/` (ignored by git).
Rendering the frames takes a few minutes. Edit the copy in `render_zh.py`
(scenes `s1` to `s6`) and the narration lines in `build_audio.py` (`LINES`).
