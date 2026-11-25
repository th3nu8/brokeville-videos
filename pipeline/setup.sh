#!/usr/bin/env bash
# One-time setup per session: python deps + Kokoro voice model. Safe to re-run.
set -e
pip install --break-system-packages -q "bpy==$(cat "$(dirname "$0")/BPY_VERSION")" kokoro-onnx soundfile pillow numpy
mkdir -p ~/kokoro
[ -s ~/kokoro/kokoro-v1.0.onnx ] || curl -sL -o ~/kokoro/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s ~/kokoro/voices-v1.0.bin ] || curl -sL -o ~/kokoro/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
ffmpeg -hide_banner -filters 2>/dev/null | grep -q rubberband || echo "WARNING: ffmpeg has no rubberband filter (voice pitch step will fail)"
python3 -c "import bpy, kokoro_onnx; print('setup ok, blender', bpy.app.version_string)"
