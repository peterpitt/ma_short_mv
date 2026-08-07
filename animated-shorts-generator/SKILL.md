---
name: animated-shorts-generator
description: Generate high-quality animated short videos (YouTube Shorts, TikTok, Reels) from concept to final output. Use for creating cute/whimsical 30-second clips with multi-scene composition, background music, and animated text overlays. Supports chibi/cartoon animation styles and custom scene generation.
---

# Animated Shorts Generator

Generate professional 30-second animated short videos with multi-scene composition, background music, and dynamic text overlays. This skill automates the entire pipeline from concept to final YouTube-ready output.

## When to Use This Skill

- Creating animated shorts for YouTube Shorts, TikTok, Instagram Reels
- Generating cute/whimsical character animations (animals, chibi style)
- Building multi-scene compositions with transitions
- Adding synchronized background music and text overlays
- Producing content with consistent visual style across multiple clips

## Workflow Overview

The skill follows a 5-phase pipeline:

| Phase | Task | Output |
|-------|------|--------|
| 1 | Generate scene reference images (9:16 portrait) | 3+ static scene images |
| 2 | Compose background music | 30-second BGM (MP3/WAV) |
| 3 | Generate animated video clips | 8-10 second video segments |
| 4 | Composite clips + add music/subtitles | 30-second final video |
| 5 | Deliver video ready for upload | MP4 (720x1280, H.264) |

## Core Requirements

### Input Specifications

- **Concept/Theme**: Clear description of what the video should show (e.g., "cute pandas eating bamboo in a forest")
- **Scene Count**: Minimum 3 distinct scenes for dynamic pacing
- **Duration**: Target 30 seconds (can adjust to 15-60 seconds)
- **Aspect Ratio**: 9:16 portrait (YouTube Shorts standard) or 16:9 landscape
- **Animation Style**: Specify style (chibi, realistic, watercolor, etc.)
- **Music Tone**: Cheerful, dramatic, calm, energetic, etc.
- **Text Overlays**: Optional subtitles/captions with timing

### Output Specifications

- **Format**: MP4 (H.264 video, AAC audio)
- **Resolution**: 720x1280 (9:16) or 1280x720 (16:9)
- **Bitrate**: 2000-2500 kbps video, 128 kbps audio
- **Duration**: Exactly 30 seconds (or specified duration)
- **Framerate**: 24-30 fps
- **Audio**: Synchronized background music + optional sound effects

## Step-by-Step Process

### Phase 1: Generate Scene Reference Images

Create 3-4 distinct scene images that will form the visual foundation:

1. **Prompt each scene** with detailed descriptions including:
   - Character/subject details (size, pose, expression)
   - Environment (background, lighting, weather)
   - Composition (camera angle, depth, focal point)
   - Art style (must match across all scenes)

2. **Use 9:16 aspect ratio** for portrait videos, 16:9 for landscape

3. **Generate in batch** to ensure visual consistency

Example prompt structure:
```
[Art style] [character description], [environment], [composition], [lighting]. 
[Specific action/emotion]. [Duration] seconds. Aspect ratio: 9:16. 
Resolution: 720p. [Additional style notes].
```

### Phase 2: Compose Background Music

Generate or source 30-second background music:

1. **Describe music requirements**:
   - Genre/style (upbeat, ambient, playful, dramatic)
   - Instrumentation (xylophone, ukulele, strings, synth)
   - Tempo (BPM if specific)
   - Emotional tone

2. **Structure the music** with clear sections:
   - [0:00-0:08] Intro: establish mood
   - [0:08-0:22] Main: build energy/narrative
   - [0:22-0:30] Outro: satisfying conclusion

3. **Ensure no vocals** for broad appeal (unless specifically requested)

### Phase 3: Generate Animated Video Clips

Convert static scene images into 8-10 second animated clips:

1. **Use video generation** with first-frame keyframe to maintain visual consistency
2. **Describe motion/animation**:
   - Camera movement (pan, zoom, static)
   - Character animation (movement, interaction)
   - Environmental effects (wind, particles, transitions)

3. **Generate without audio** (music added in Phase 4)

4. **Ensure consistent resolution** (720x1280 or 1280x720) across all clips

### Phase 4: Composite and Finalize

Merge clips with music and text overlays using FFmpeg:

1. **Concatenate clips** in sequence
2. **Add background music** with volume normalization (0.8 volume recommended)
3. **Overlay text** with:
   - Font: Chinese-compatible (Noto Sans CJK TC recommended)
   - Size: 36-52pt depending on content
   - Color: White with black border for readability
   - Timing: Synchronized to scene changes
4. **Trim to exactly 30 seconds**
5. **Encode** with H.264 (preset: fast, CRF: 22-23)

### Phase 5: Deliver and Upload

Output is YouTube-ready MP4:

1. **Verify specs**: Resolution, duration, codec, bitrate
2. **Provide download link** to user
3. **Suggest upload metadata**:
   - Title: Descriptive, keyword-rich
   - Description: Hook + CTA
   - Tags: Relevant hashtags
   - Thumbnail: Frame from video or custom

## Technical Implementation

### Tools Used

| Tool | Purpose |
|------|----------|
| `generate_image` | Create scene reference images |
| `generate_music` | Compose background music |
| `generate_video` | Animate static scenes |
| `ffmpeg` | Composite clips, add music/text, encode |

### FFmpeg Composite Command Template

```bash
ffmpeg -y \
  -f concat -safe 0 -i concat_list.txt \
  -i background_music.mp3 \
  -filter_complex "
    [0:v]
    drawtext=fontfile='font.ttc':text='Text':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=100:enable='between(t,0,10)',
    [vout];
    [1:a]atrim=0:30,asetpts=PTS-STARTPTS,volume=0.8[aout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -t 30 \
  output.mp4
```

## Common Variations

### 15-Second Clips (TikTok/Reels)
- Reduce scene count to 2-3
- Shorten music to 15 seconds
- Adjust text timing accordingly

### 60-Second Long-Form
- Increase to 5-6 scenes
- Extend music composition
- Add intro/outro sequences

### Landscape (16:9)
- Adjust all scene images to 16:9
- Use 1280x720 resolution
- Modify text positioning for wider canvas

### Multiple Characters/Scenes
- Generate 4-5 distinct scenes
- Ensure visual continuity across scenes
- Use consistent color palette and art style

## Best Practices

1. **Visual Consistency**: All scenes should use the same art style, color palette, and character design
2. **Pacing**: Vary scene duration (8-10 seconds each) to maintain viewer interest
3. **Music Sync**: Align text/scene changes with musical beats or transitions
4. **Text Readability**: Use high-contrast colors (white text + black border) for mobile viewing
5. **Aspect Ratio**: Always match aspect ratio across all generation phases
6. **File Sizes**: Aim for 8-12MB MP4 for fast upload/streaming

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Inconsistent scene visuals | Use same art style description across all prompts; reference first image in subsequent generations |
| Audio sync issues | Ensure all clips are exactly 10s; use `atrim` to trim music precisely |
| Text rendering errors | Use full font path; escape special characters in drawtext filter |
| Resolution mismatch | Verify all clips are 720x1280; use FFmpeg `-s` filter to force resolution |
| Slow encoding | Use `preset:fast` instead of `slow`; reduce CRF value (higher = faster but lower quality) |

## References

See `/home/ubuntu/skills/animated-shorts-generator/references/` for:
- `ffmpeg_filters.md` - Advanced FFmpeg filter syntax
- `music_prompting.md` - Detailed music generation guidelines
- `scene_prompting.md` - Scene image generation best practices
