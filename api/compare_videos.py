import cv2
import mediapipe as mp
import numpy as np
from math import sqrt

mp_pose = mp.solutions.pose

# Define key joints and their weights
JOINTS = [
    (mp_pose.PoseLandmark.RIGHT_WRIST, "Right Wrist", 20),
    (mp_pose.PoseLandmark.LEFT_WRIST, "Left Wrist", 20),
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, "Right Shoulder", 1),
    (mp_pose.PoseLandmark.LEFT_SHOULDER, "Left Shoulder", 1),
    (mp_pose.PoseLandmark.RIGHT_ELBOW, "Right Elbow", 8),
    (mp_pose.PoseLandmark.LEFT_ELBOW, "Left Elbow", 8),
    (mp_pose.PoseLandmark.RIGHT_HIP, "Right Hip", 4),
    (mp_pose.PoseLandmark.LEFT_HIP, "Left Hip", 4),
    (mp_pose.PoseLandmark.RIGHT_KNEE, "Right Knee", 3),
    (mp_pose.PoseLandmark.LEFT_KNEE, "Left Knee", 3),
]

def extract_keypoints(video_path, pose):
    cap = cv2.VideoCapture(video_path)
    keypoints = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Process frame for pose estimation
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            keypoints.append(results.pose_landmarks.landmark)
        else:
            keypoints.append(None)  # No keypoints detected for this frame

    cap.release()
    return keypoints, fps

def calculate_differences(keypoints1, keypoints2, joints):
    differences = []
    for kp1, kp2 in zip(keypoints1, keypoints2):
        if kp1 is None or kp2 is None:
            differences.append(None)
            continue

        vec1 = []
        vec2 = []
        weights = []

        for joint_idx, joint_name, weight in joints:
            x1, y1 = kp1[joint_idx].x, kp1[joint_idx].y
            x2, y2 = kp2[joint_idx].x, kp2[joint_idx].y

            vec1.extend([x1, y1])
            vec2.extend([x2, y2])
            weights.extend([weight, weight])  # apply weights to both x and y

        # Convert to numpy arrays
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        weights = np.array(weights)

        # Apply weights
        vec1_weighted = vec1 * weights
        vec2_weighted = vec2 * weights

        # L2 normalization
        norm1 = np.linalg.norm(vec1_weighted)
        norm2 = np.linalg.norm(vec2_weighted)

        if norm1 == 0 or norm2 == 0:
            cosine_distance = 1  # Max distance if one vector is zero
        else:
            cosine_similarity = np.dot(vec1_weighted, vec2_weighted) / (norm1 * norm2)
            cosine_distance = 1 - cosine_similarity

        differences.append((cosine_distance, {}))

    return differences

def evaluate_video(differences, fps, thresholds):
    evaluations = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0}
    mismatches = []

    for i, diff in enumerate(differences):
        if diff is None:
            continue  # Skip missing frames

        mean_diff, joint_differences = diff
        if mean_diff < thresholds["Good"]:
            eval_type = "Excellent"
        elif mean_diff < thresholds["Fair"]:
            eval_type = "Good"
        elif mean_diff < thresholds["Poor"]:
            eval_type = "Fair"
        else:
            eval_type = "Poor"

        evaluations[eval_type] += 1

        # Only record mismatches (Fair and Poor)
        if eval_type in ["Fair", "Poor"]:
            mismatches.append({
                "timestamp": i / fps,
                "mean_difference": mean_diff,
                "joint_differences": joint_differences,
                "evaluation": eval_type
            })

    # Overall evaluation based on the majority
    total_frames = sum(evaluations.values())
    overall_evaluation = max(evaluations, key=evaluations.get) if total_frames > 0 else "No Data"

    # Determine matching status
    is_matching = len(mismatches) == 0

    return {
        "is_matching": is_matching,
        "overall_evaluation": overall_evaluation,
        "evaluations": evaluations,
        "mismatches": sorted(mismatches, key=lambda x: x["mean_difference"], reverse=True)[:15]
    }

def compare_videos(video1_path, video2_path):
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    keypoints1, fps1 = extract_keypoints(video1_path, pose)
    keypoints2, fps2 = extract_keypoints(video2_path, pose)

    differences = calculate_differences(keypoints1, keypoints2, JOINTS)

    thresholds = {
        "Good": 0.10,
        "Fair": 0.15,
        "Poor": 0.25
    }

    result = evaluate_video(differences, fps2, thresholds)

    pose.close()
    return result


# video1_path = "sample_videos/vid1.mp4"
# video2_path = "sample_videos/vid2.mp4"
# print(compare_videos(video1_path, video2_path))

"""
Also, we need to find out how to store videos properly
Suggestion:
AWS S3 Buckets
Google Cloud
"""