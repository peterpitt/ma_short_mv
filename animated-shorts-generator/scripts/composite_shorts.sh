#!/bin/bash
# Composite animated shorts with music and text overlays
# Usage: ./composite_shorts.sh <concat_list> <music_file> <output_file> [duration] [font_path]

set -e

CONCAT_LIST="${1:?Error: concat_list required}"
MUSIC_FILE="${2:?Error: music_file required}"
OUTPUT_FILE="${3:?Error: output_file required}"
DURATION="${4:-30}"
FONT_PATH="${5:-/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc}"

if [ ! -f "$CONCAT_LIST" ]; then
  echo "Error: concat_list file not found: $CONCAT_LIST"
  exit 1
fi

if [ ! -f "$MUSIC_FILE" ]; then
  echo "Error: music_file not found: $MUSIC_FILE"
  exit 1
fi

if [ ! -f "$FONT_PATH" ]; then
  echo "Warning: Font not found at $FONT_PATH, using system default"
  FONT_PATH=""
fi

echo "Compositing shorts..."
echo "  Concat list: $CONCAT_LIST"
echo "  Music: $MUSIC_FILE"
echo "  Output: $OUTPUT_FILE"
echo "  Duration: ${DURATION}s"
echo "  Font: ${FONT_PATH:-system default}"

# Step 1: Merge video clips
echo "Step 1: Merging video clips..."
ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -an /tmp/shorts_merged.mp4 2>&1 | grep -E "frame=|error" || true

# Step 2: Add music and encode
echo "Step 2: Adding music and encoding..."
FILTER_COMPLEX="[0:v][vout];[1:a]atrim=0:${DURATION},asetpts=PTS-STARTPTS,volume=0.8[aout]"

if [ -n "$FONT_PATH" ]; then
  FILTER_COMPLEX="[0:v]drawtext=fontfile='${FONT_PATH}':text='':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=100:enable='between(t,0,${DURATION})'[vout];[1:a]atrim=0:${DURATION},asetpts=PTS-STARTPTS,volume=0.8[aout]"
fi

ffmpeg -y \
  -i /tmp/shorts_merged.mp4 \
  -i "$MUSIC_FILE" \
  -filter_complex "$FILTER_COMPLEX" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -t "$DURATION" \
  "$OUTPUT_FILE" 2>&1 | grep -E "frame=|error|kb/s" || true

# Cleanup
rm -f /tmp/shorts_merged.mp4

echo "✅ Compositing complete: $OUTPUT_FILE"
ls -lh "$OUTPUT_FILE"
