import cv2
import os

video_name = "videos/video2.mp4"       
output_folder = "frames_from_video"  
interval_sec = 15              

os.makedirs(output_folder, exist_ok=True)
cap = cv2.VideoCapture(video_name)

if not cap.isOpened():
    print(f"Error: Could not open {video_name}")
    exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 30.0  # Fallback if FPS detection fails

# How many frames correspond to 15 seconds
frame_step = int(fps * interval_sec)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"FPS: {fps:.2f} | Extracting 1 frame every {interval_sec}s (~{frame_step} frames)...")

saved_count = 0
for frame_idx in range(0, total_frames, frame_step):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    success, frame = cap.read()
    if not success:
        break
    
    timestamp_sec = int(frame_idx / fps)
    filename = os.path.join(output_folder, f"frame_{timestamp_sec:05d}s.jpg")
    cv2.imwrite(filename, frame)
    saved_count += 1

cap.release()
print(f"Done! Saved {saved_count} frames into '{output_folder}'.")