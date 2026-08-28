# Animated Shorts Generator Skill

A Manus skill for generating high-quality animated short videos (YouTube Shorts, TikTok, Reels) from concept to final output.

## Features

- **Multi-Scene Composition**: Generate 3+ distinct scenes with consistent visual style
- **Background Music**: Compose 30-second background music with customizable mood and instrumentation
- **Video Animation**: Convert static scenes into 8-10 second animated clips
- **Text Overlays**: Add synchronized text overlays with Chinese font support
- **YouTube-Ready Output**: Final MP4 (720x1280, H.264) optimized for YouTube Shorts
- **One-Click YouTube Publishing**: Manually trigger a GitHub Actions workflow with secure OAuth Secrets

## Quick Start

1. Describe your video concept (e.g., "cute pandas eating bamboo in a forest")
2. Specify animation style (chibi, realistic, watercolor, etc.)
3. The skill will:
   - Generate 3 scene reference images (9:16 portrait)
   - Compose 30-second background music
   - Create 3 animated video clips
   - Composite everything with text overlays
   - Deliver final YouTube-ready MP4

## Structure

```
animated-shorts-generator/
├── SKILL.md                    # Main skill documentation
├── scripts/
│   └── composite_shorts.sh     # FFmpeg composition script
├── references/
│   ├── ffmpeg_filters.md       # Advanced FFmpeg syntax
│   ├── music_prompting.md      # Music generation guidelines
│   └── scene_prompting.md      # Scene image best practices
└── templates/
```

## Requirements

- FFmpeg with libx264 and aac support
- Noto Sans CJK fonts (for Chinese text)
- Manus image, music, and video generation capabilities

## Usage

See `SKILL.md` for detailed workflow and best practices.

## One-Click YouTube Publishing

The repository includes `.github/workflows/publish-to-youtube.yml`. After setting `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN` as GitHub Actions Secrets, open **Actions → Publish to YouTube → Run workflow**. Provide either a repository-relative MP4 path or a public HTTPS MP4 URL, then choose the title, metadata, and visibility. See [`YOUTUBE_SETUP.md`](YOUTUBE_SETUP.md) for the complete OAuth setup and security notes.

The workflow uses a refresh token and never performs interactive OAuth on the GitHub runner. It defaults to `unlisted` so the first upload can be checked before being made public.

## License

See LICENSE file for terms.
