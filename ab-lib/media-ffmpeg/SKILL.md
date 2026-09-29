---
name: media-ffmpeg
description: Video and audio processing with ffmpeg/ffprobe — inspecting media, cutting and concatenating, extracting or replacing audio, detecting silence, re-encoding vs stream-copying, and verifying outputs. Use for any task that reads, edits, converts, or analyzes video/audio files. Not for still-image-only editing.
---

# media-ffmpeg

Every media task starts with ffprobe and ends with ffprobe. In between,
prefer the least destructive operation that satisfies the requirement.

## Applicability & fallback

- Tools: `ffmpeg`/`ffprobe` CLI (install via apt if absent). Python wrappers
  (moviepy, pydub) are fine when present, but the CLI is the dependable path
  and everything below works with `subprocess`.
- If a filter/codec is missing from the build, re-encode via an intermediate
  (wav for audio, mp4/h264 for video) rather than fighting the build.

## Probe first — never assume media properties

```bash
ffprobe -v error -print_format json -show_format -show_streams input.mp4
```

Read from the JSON: duration, codec per stream, resolution, fps
(`r_frame_rate` is a fraction — eval it), sample rate, channel count, and
**whether an audio stream exists at all**. Downstream commands silently
misbehave when these assumptions are wrong.

## Cut, copy, re-encode (choose deliberately)

- **Stream copy** (`-c copy`) is lossless and fast but cuts land on
  keyframes — start times shift by up to a GOP. Use when the task tolerates
  approximate cuts or realigns on keyframes.
- **Re-encode** for frame-accurate cuts and any filtering:
  `ffmpeg -i in.mp4 -ss 3.25 -to 8.5 -c:v libx264 -c:a aac out.mp4`.
  Put `-ss` after `-i` for accuracy (before `-i` = fast but keyframe-snapped).
- Concatenate same-codec files with the concat demuxer:
  `printf "file '%s'\n" part*.mp4 > list.txt && ffmpeg -f concat -safe 0 -i
  list.txt -c copy out.mp4`. Different codecs/resolutions → re-encode via the
  concat *filter* instead.
- Always pass `-y` in scripts (overwrite without prompt) and check the
  subprocess return code — a nonzero exit with a partial file on disk is a
  failure, not a result.

## Audio work

- Extract: `ffmpeg -i in.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 out.wav`
  (16 kHz mono pcm is the safe analysis format).
- Silence detection:
  `ffmpeg -i in.wav -af silencedetect=noise=-30dB:d=0.5 -f null - 2>&1`
  emits `silence_start` / `silence_end` lines on **stderr**. Tune both the
  threshold (dB) and minimum duration to the task's definition of silence —
  defaults rarely match a spec exactly.
- Replace/mux audio: `-map 0:v -map 1:a -c:v copy -shortest`. Watch
  `-shortest` vs duration requirements when streams differ in length.

## Timing precision

- Seconds are floats; represent timestamps as `HH:MM:SS.mmm` or plain
  seconds consistently, and respect the task's rounding for reported times.
- Output duration ≠ (end − start) exactly after re-encoding; frame and
  audio-priming offsets of ~1 frame are normal. If the task asserts strict
  duration bounds, verify against ffprobe and adjust cut points.

## Verify before finishing

1. `ffprobe` the output: duration within the required tolerance, expected
   stream count and codecs, resolution/sample rate as specified.
2. Confirm the file plays: a zero-byte or header-only file passes `ls` but
   fails `ffprobe` — probing is the check.
3. For reports (timestamps, segment lists): recompute one entry from the raw
   detection output and confirm formats/units match the spec.
4. Exact output path, container, and extension as requested.
