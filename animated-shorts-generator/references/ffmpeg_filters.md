# FFmpeg Filters for Animated Shorts

Advanced FFmpeg filter syntax for video composition, text overlays, and effects.

## Text Overlay (drawtext)

### Basic Syntax
```bash
drawtext=fontfile='font.ttc':text='Your Text':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=100
```

### Parameters
- `fontfile`: Path to TTF/TTC font file
- `text`: Text content (escape special chars with backslash)
- `fontsize`: Font size in pixels
- `fontcolor`: Text color (white, yellow, red, etc.)
- `borderw`: Border width in pixels
- `bordercolor`: Border color
- `x`: Horizontal position (w=width, text_w=text width)
- `y`: Vertical position (h=height, text_h=text height)
- `enable`: Timing condition (e.g., `between(t,0,10)` for 0-10 seconds)

### Common Positioning
```bash
# Center horizontally, 100px from top
x=(w-text_w)/2:y=100

# Center both horizontally and vertically
x=(w-text_w)/2:y=(h-text_h)/2

# Bottom right with padding
x=w-text_w-20:y=h-text_h-20

# Top left with padding
x=20:y=20
```

### Timing Examples
```bash
# Show from 0-10 seconds
enable='between(t,0,10)'

# Show from 5 seconds onwards
enable='t>=5'

# Show for 3 seconds starting at t=2
enable='between(t,2,5)'

# Show during specific scenes (requires coordination)
enable='between(t,0,10)+between(t,20,30)'
```

## Audio Trimming (atrim)

Trim audio to specific duration and reset timestamps:

```bash
[1:a]atrim=0:30,asetpts=PTS-STARTPTS,volume=0.8[aout]
```

- `atrim=0:30`: Keep first 30 seconds
- `asetpts=PTS-STARTPTS`: Reset presentation timestamps to start at 0
- `volume=0.8`: Reduce volume to 80% (0.0-1.0)

## Video Concatenation

Create concat_list.txt:
```
file '/path/to/clip1.mp4'
file '/path/to/clip2.mp4'
file '/path/to/clip3.mp4'
```

Then use:
```bash
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy output.mp4
```

## Complex Filter Examples

### Multiple Text Overlays with Timing
```bash
-filter_complex "
  [0:v]
  drawtext=fontfile='font.ttc':text='Title':fontsize=52:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=80:enable='between(t,0,29)',
  drawtext=fontfile='font.ttc':text='Scene 1':fontsize=42:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=160:enable='between(t,0,10)',
  drawtext=fontfile='font.ttc':text='Scene 2':fontsize=42:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=160:enable='between(t,10,20)',
  drawtext=fontfile='font.ttc':text='CTA':fontsize=36:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-120:enable='between(t,22,29)'
  [vout];
  [1:a]atrim=0:30,asetpts=PTS-STARTPTS,volume=0.8[aout]
" \
-map "[vout]" -map "[aout]"
```

### Scale/Resize Video
```bash
-filter_complex "[0:v]scale=720:1280[vout]"
```

### Add Fade In/Out
```bash
-filter_complex "[0:v]fade=t=in:st=0:d=1,fade=t=out:st=29:d=1[vout]"
```

### Overlay Image on Video
```bash
-filter_complex "[0:v][1:v]overlay=x=10:y=10[vout]"
```

## Encoding Parameters

### Video Codec (libx264)
- `-preset`: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
- `-crf`: Quality (0-51, lower=better, default=28, recommended 22-23)
- `-pix_fmt`: yuv420p (for compatibility)
- `-b:v`: Bitrate (e.g., 2000k for 2 Mbps)

### Audio Codec (aac)
- `-b:a`: Bitrate (128k recommended for shorts)
- `-ar`: Sample rate (44100 or 48000)

### Complete Encoding Command
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  output.mp4
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Text not rendering | Check font path exists; use full absolute path |
| Special characters missing | Escape with backslash; use UTF-8 encoding |
| Audio out of sync | Use `asetpts=PTS-STARTPTS` after atrim |
| Video too large | Reduce CRF (higher value = smaller file, lower quality) |
| Slow encoding | Use `-preset fast` or `ultrafast` |
| Resolution mismatch | Use `scale` filter to force resolution |
