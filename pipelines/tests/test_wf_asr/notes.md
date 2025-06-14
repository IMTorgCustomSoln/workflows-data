# Notes on WF-ASR

## Creating .mp4 files

Creating simple audio files in .mp4 format is frustratingly difficult.  You may use QuickTime to create a recording.  However, you then need to use ffmpeg to fix oddities in the format.

The "moov atom" is essential for playback.  Run FFmpeg with the -movflags faststart option to try to fix the "moov atom" issue:
```
ffmpeg -i input.mp4 -movflags faststart output.mp4
```

Once that is complete, test ffmpeg to ensure it outputs .mp3, correctly.
