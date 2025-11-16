# Error Fixes Applied

## Issue 1: `extract_frames` returning None
**Error**: `TypeError: object of type 'NoneType' has no len()`

**Cause**: The `extract_frames` function was incomplete - missing the return statement.

**Fix**: Added proper implementation with return statement:
```python
subprocess.run(cmd, check=True, capture_output=True)
return sorted(frame_dir.glob("frame_*.jpg"))
```

---

## Issue 2: FFmpeg CalledProcessError (Exit 251)
**Error**: `subprocess.CalledProcessError: Command '['ffmpeg', ...]' returned non-zero exit status 251`

**Cause**: FFmpeg exit code 251 typically indicates:
- Unsupported video codec
- Corrupted video file
- Missing codec libraries
- Incompatible video format

**Fixes Applied**:

### 1. Enhanced Error Handling
- Added detailed error logging (stdout, stderr, command)
- Added file existence check before processing
- Added timeout (5 minutes) for large videos
- Better error messages explaining the issue

### 2. Fallback Strategy
If 3 FPS extraction fails, automatically retry with 1 FPS:
```python
# Fallback approach
cmd_fallback = [
    "ffmpeg", "-i", str(video_path),
    "-vf", "fps=1",
    "-q:v", "3",
    str(frame_dir / "frame_%05d.jpg"), 
    "-y"
]
```

### 3. Improved FFmpeg Command
Added more compatible parameters:
```python
cmd = [
    "ffmpeg", 
    "-i", str(video_path),
    "-vf", f"fps={fps}",
    "-vsync", "vfr",  # Variable frame rate - handles issues better
    "-q:v", "2",      # Quality setting
    "-start_number", "0",
    str(frame_dir / "frame_%05d.jpg"), 
    "-y",
    "-loglevel", "error"  # Only show errors
]
```

### 4. Task-Level Error Handling
Enhanced `tasks.py` with:
- Max retries: 2
- Specific error handling for different error types
- User-friendly error messages
- Automatic retry with 10-second countdown

---

## Expected Behavior Now

### Success Case:
1. Video uploaded → FFmpeg extracts at 3 FPS
2. Frames processed → Crime analysis runs
3. Results returned with detailed crime detection

### Error Cases:

#### Case 1: 3 FPS fails, 1 FPS succeeds
```
⚠️ Warning: Retrying with fps=1 as fallback...
✅ Fallback extraction successful at 1 FPS
→ Processing continues with fewer frames
```

#### Case 2: Video file not found
```
❌ Error: Video file not found
Details: /app/uploads/xyz.mp4 does not exist
```

#### Case 3: Unsupported format
```
❌ Error: Video processing failed
Details: Failed to extract frames from video
Suggestion: Please ensure the video is in a supported format (MP4, AVI, MOV) with H.264/H.265 codec
```

#### Case 4: Corrupted video
```
❌ Error: No frames extracted
Details: Video may be corrupted, empty, or in an unsupported format
Supported formats: mp4, avi, mov, mkv with H.264/H.265 codec
```

---

## Troubleshooting

### If FFmpeg still fails:

1. **Check video codec**:
   ```bash
   docker exec crime_ai_worker ffmpeg -i /app/uploads/your_video.mp4
   ```
   Look for codec information (should be H.264, H.265, VP9, etc.)

2. **Check FFmpeg codecs available**:
   ```bash
   docker exec crime_ai_worker ffmpeg -codecs | grep h264
   ```

3. **Test manual extraction**:
   ```bash
   docker exec crime_ai_worker ffmpeg -i /app/uploads/your_video.mp4 -vf fps=1 /tmp/test_%05d.jpg -y
   ```

4. **Check video file size/permissions**:
   ```bash
   docker exec crime_ai_worker ls -lh /app/uploads/
   ```

### Common Video Issues:

| Issue | Solution |
|-------|----------|
| Old codec (MPEG-2, DivX) | Re-encode with H.264: `ffmpeg -i input.mp4 -c:v libx264 output.mp4` |
| High bitrate/resolution | System may timeout - reduce to 1080p or lower |
| Corrupted file | Try re-downloading or use different source |
| Wrong container | Remux to MP4: `ffmpeg -i input.avi -c copy output.mp4` |

### Supported Formats:
✅ MP4 (H.264, H.265)
✅ AVI (with common codecs)
✅ MOV (H.264, H.265)
✅ MKV (H.264, H.265)
✅ WebM (VP8, VP9)

❌ Proprietary/rare codecs
❌ DRM-protected videos
❌ Ultra high resolution (>4K may timeout)

---

## Files Modified

1. **backend/processing.py**
   - Enhanced `extract_frames()` with error handling
   - Added fallback strategy
   - Added video validation
   - Added detailed logging

2. **backend/tasks.py**
   - Added error-specific handling
   - Added retry logic (max 2 retries)
   - Added user-friendly error messages
   - Added logging

---

## Next Steps

1. **Restart Docker containers** to apply changes:
   ```bash
   docker-compose restart
   ```

2. **Check logs** when uploading video:
   ```bash
   docker-compose logs -f crime_ai_worker
   ```

3. **If error persists**, check:
   - Video codec compatibility
   - File size (<500MB recommended)
   - File permissions in uploads directory

4. **Try a different video** to isolate if it's file-specific
