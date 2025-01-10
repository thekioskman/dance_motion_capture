import moviepy.editor as mp
import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

"""
Parameters:
- video_path: file path to the input video
- audio_output_path: file path where the extracted audio will be saved

Output: None (extracted audio is saved to output path)
"""
def extract_audio_from_video(video_path, audio_output_path):
    """Extract audio from video and save it as a .wav file."""
    video = mp.VideoFileClip(video_path) # Load video from video_path (includes both video frames and the audio track)
    video.audio.write_audiofile(audio_output_path) # Saves audio to the specified audio_output_path in .wav format

"""
Output: 2D numpy array where: 
- each row represents the audio feature vector for a single time frame
- each column represents one of the 20 MFCC coefficients
- e.g. 
[
  [MFCC_1_frame_1, MFCC_2_frame_1, ..., MFCC_20_frame_1],
  [MFCC_1_frame_2, MFCC_2_frame_2, ..., MFCC_20_frame_2],
  ...
]
"""
def compute_audio_features(audio_path):
    """Compute Mel-frequency cepstral coefficients (MFCCs) for the given audio."""
    # y is a 1D numpy array representing the audio signal over time
    # sr is the sampling rate of the audio; sr=None keeps the original sampling rate of the audio file
    y, sr = librosa.load(audio_path, sr=None)  # Load audio

    # n_mfcc = number of MFCCs to compute (first n coefficients for each frame)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)  # Compute MFCCs

    # Converts MFCC matrix from (20, num_frames) to (num_frames, 20)
    return mfccs.T  # Transpose for time alignment


def pad_features(features1, features2):
    """Pad the shorter feature sequence with zeros to match the length of the longer sequence."""
    len1, len2 = features1.shape[0], features2.shape[0]
    
    if len1 == len2:
        return features1, features2
    
    # Determine which sequence is shorter and pad it
    if len1 > len2:
        padded_features2 = np.pad(features2, ((0, len1 - len2), (0, 0)), mode='constant')
        return features1, padded_features2
    else:
        padded_features1 = np.pad(features1, ((0, len2 - len1), (0, 0)), mode='constant')
        return padded_features1, features2

"""
Purpose: Find optimal alignment between two time-series datasets, minimizing cumulative distance while maintaining the order of the elements 

Parameters:
- features1: first sequence of audio features; 2D array or matrix where row is time step and column are feature dimensions (MFCC coeefficients)
- features2: ditto to above but for second audio clip

Output: 
- alignment: a list of coordinate pairs, each representing a point in features1 mapped to a corresponding point in features2
- dist: A matrix where each entry represents the cumulative distance between a point in features1 and features2. Lower values indicate better alignment.
"""
def align_audio_features(features1, features2):
    """Align two sets of audio features using DTW."""
    features1_padded, features2_padded = pad_features(features1, features2)  # Pad the shorter feature set to match the length of the longer feature set
    print(features1_padded.shape)
    print(features2_padded.shape)

    # Convert padded features to list of tuples for fastdtw
    features1_list = [tuple(feature) for feature in features1_padded]
    features2_list = [tuple(feature) for feature in features2_padded]

    # Perform DTW alignment using fastdtw (which is simpler and more robust)
    distance, path = fastdtw(features1_list, features2_list, dist=euclidean)
    return path, distance

def synchronize_videos(video_test_path, video_ref_path, path):
    """
    Trim two videos based on the DTW alignment path so they start at the same time.
    Output two separate synchronized video files.
    """
    video_test = mp.VideoFileClip(video_test_path)
    video_ref = mp.VideoFileClip(video_ref_path)

    # Get the durations of the two videos
    duration1 = video_test.duration
    duration2 = video_ref.duration

    # Find the start times for both videos based on the DTW alignment path
    start_time1 = (path[0][0] / len(path)) * duration1  # Start time for video_test
    start_time2 = (path[0][1] / len(path)) * duration2  # Start time for video_ref

    # Find the end times for both videos based on the DTW alignment path
    end_time1 = (path[-1][0] / len(path)) * duration1  # End time for video_test
    end_time2 = (path[-1][1] / len(path)) * duration2  # End time for video_ref

    # Trim both videos to their respective start and end times
    trimmed_video_test = video_test.subclip(start_time1, end_time1)
    trimmed_video_ref = video_ref.subclip(start_time2, end_time2)

    # Write the trimmed videos to files
    trimmed_video_test.write_videofile("trimmed_video_test.mp4", codec='libx264')
    trimmed_video_ref.write_videofile("trimmed_video_ref.mp4", codec='libx264')


import matplotlib.pyplot as plt


def main(video_test_path, video_ref_path):
    # Step 1: Extract audio from videos
    audio_test_path = "audio_test.wav"
    audio_ref_path = "audio_ref.wav"
    extract_audio_from_video(video_test_path, audio_test_path)
    extract_audio_from_video(video_ref_path, audio_ref_path)

    # Step 2: Compute audio features
    features1 = compute_audio_features(audio_test_path)
    features2 = compute_audio_features(audio_ref_path)

    # Step 3: Perform DTW
    alignment, distance = align_audio_features(features1, features2)

    # Step 4: Synchronize the videos based on the DTW alignment
    synchronize_videos(video_test_path, video_ref_path, alignment)

    # print("DTW Distance:", distance)
    # print("Alignment Path:", alignment)

if __name__ == "__main__":
    # Replace with your video paths
    video_test = "sample_videos/haidilao_test.mov"
    video_ref = "sample_videos/haidilao_ref.mov"
    main(video_test, video_ref)

