# Mystery Announcement Video

## Video File Required

For the countdown section to work properly, you need to add the announcement video:

**File:** `videos/mystery-announcement.mp4`

### Video Specifications:
- **Format:** MP4 (H.264)
- **Resolution:** 1920x1080 (Full HD) or 1280x720 (HD)
- **Duration:** 30-90 seconds recommended
- **Aspect Ratio:** 16:9
- **File Size:** Keep under 50MB for web performance

### Content Suggestions:
- Mystery reveal of what's coming
- Dramatic announcement
- New project/location reveal
- Special event announcement
- Teaser of new offerings

### Placeholder:
Currently using `carousel1.jpg` as video poster. The video will auto-play when countdown reaches zero.

### How to Add:
1. Create your announcement video
2. Name it `mystery-announcement.mp4`
3. Upload to the `videos/` folder on your server
4. Test the countdown functionality

### Countdown Timer:
- Currently set to 5 days from when page loads
- Edit line in `script.js` to set specific date:
  ```javascript
  countdownDate = new Date("2025-01-25T10:00:00").getTime();
  ```

### Testing:
Uncomment the test line in script.js to trigger countdown completion after 5 seconds:
```javascript
// setTimeout(countdownComplete, 5000);
```

### Mysterious Theme:
- No spoilers about what's coming
- Dark, mysterious design
- "¿Qué viene?" (What's coming?) navigation
- Subtle glow effects
- Anticipation building text
