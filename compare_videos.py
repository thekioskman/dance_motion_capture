import cv2
from skimage.metrics import structural_similarity as ssim
import mediapipe as mp
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

def compare_frames(video1_path, video2_path):
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)

    similarities = []
    while cap1.isOpened() and cap2.isOpened():
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break

        # Resize to same dimensions if needed
        frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))

        # Convert to grayscale for SSIM calculation
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Calculate SSIM (Structural Similarity Index)
        score, diff = ssim(gray1, gray2, full=True)
        similarities.append(score)

    cap1.release()
    cap2.release()
    return similarities

# similarities = compare_frames("sample_videos/vid1.MOV", "sample_videos/vid2.MOV")
# print("Average SSIM Similarity:", np.mean(similarities))
# "Average SSIM Similarity: 0.6064674307483849"

mp_pose = mp.solutions.pose

def extract_pose_landmarks(video_path):
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose()
    landmarks_list = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            # Collect pose landmarks for each frame
            landmarks = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]
            landmarks_list.append(landmarks)

    cap.release()
    return landmarks_list

# Extract landmarks from both videos
# landmarks1 = extract_pose_landmarks("sample_videos/vid1.MOV")
# landmarks2 = extract_pose_landmarks("sample_videos/vid2.MOV")

# Compare landmarks with a similarity measure

def calculate_dtw_difference(landmarks1, landmarks2):
    """
    Use DTW to calculate the difference between landmarks of two videos.
    Parameters:
        landmarks1: List of landmarks per frame for video 1
        landmarks2: List of landmarks per frame for video 2
    Returns:
        dtw_distance: The DTW distance between the two landmark sequences.
    """
    # Flatten each frame's landmarks into a 1D array for DTW comparison
    flattened_landmarks1 = [np.array(frame).flatten() for frame in landmarks1]
    flattened_landmarks2 = [np.array(frame).flatten() for frame in landmarks2]

    # Calculate DTW distance between the two sequences
    dtw_distance, _ = fastdtw(flattened_landmarks1, flattened_landmarks2, dist=euclidean)
    return dtw_distance

# dtw_difference = calculate_dtw_difference(landmarks1, landmarks2)
# print("DTW Motion Difference:", dtw_difference)
# "DTW Motion Difference: 1045.272274242002"

"""
We need to decide on which type of comparison to perform:
DTW Motion Difference: Dynamic Time Warping (DTW)
or
Average SSIM Similarity: Structural Similarity Index Measure (SSIM)
Need more research to be done

Also, we need to find out how to store videos properly
Suggestion:
AWS S3 Buckets
Google Cloud
"""