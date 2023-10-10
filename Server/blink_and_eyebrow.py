import cv2
import dlib
import imutils
import numpy as np
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils

# Function to calculate the eye aspect ratio
def calculate_eye_aspect_ratio(eye):
    # Calculate the euclidean distances between the vertical landmarks
    vertical_1 = dist.euclidean(eye[1], eye[5])
    vertical_2 = dist.euclidean(eye[2], eye[4])

    # Calculate the euclidean distance between the horizontal landmarks
    horizontal = dist.euclidean(eye[0], eye[3])

    # Calculate the eye aspect ratio
    eye_aspect_ratio = (vertical_1 + vertical_2) / (2.0 * horizontal)

    # Return the eye aspect ratio
    return eye_aspect_ratio

# Function to calculate the relative position of the eyebrows
def calculate_eyebrow_position(eyebrow):
    # Calculate the y-coordinate range of the eyebrow
    min_y = np.min(eyebrow[:, 1])
    max_y = np.max(eyebrow[:, 1])

    # Calculate the relative position of the eyebrow based on the y-coordinate range
    eyebrow_position = (max_y - min_y) / 2.0

    # Return the relative position of the eyebrow
    return eyebrow_position

# Set the threshold for eye aspect ratio and consecutive frames
EAR_THRESHOLD = 0.3
EYE_AR_CONSECUTIVE_FRAMES = 5
blink_counter = 0
total_blinks = 0

# Initialize the frontal face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize the video capture
cap = cv2.VideoCapture(0)

while True:
    # Read frame from the video capture
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=500, height=500)

    # Define the indexes for left and right eye landmarks
    (left_eye_start, left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (right_eye_start, right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    # Preprocess the image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(gray)

    # Detect faces in the grayscale image
    detections = detector(clahe_image, 0)

    for detection in detections:
        shape = predictor(gray, detection)
        shape = face_utils.shape_to_np(shape)

        left_eye = shape[left_eye_start:left_eye_end]
        right_eye = shape[right_eye_start:right_eye_end]

        left_eye_hull = cv2.convexHull(left_eye)
        right_eye_hull = cv2.convexHull(right_eye)
        cv2.drawContours(clahe_image, [left_eye_hull], -1, (255, 0, 0), 1)
        cv2.drawContours(clahe_image, [right_eye_hull], -1, (255, 0, 0), 1)

        # Calculate the eye aspect ratio for each eye
        left_eye_ear = calculate_eye_aspect_ratio(left_eye)
        right_eye_ear = calculate_eye_aspect_ratio(right_eye)

        average_ear = (left_eye_ear + right_eye_ear) / 2.0

        if average_ear < EAR_THRESHOLD:
            blink_counter += 1
        else:
            if blink_counter >= EYE_AR_CONSECUTIVE_FRAMES:
                total_blinks += 1
            blink_counter = 0

        # Calculate the eyebrow positions
        left_eyebrow_position = calculate_eyebrow_position(shape[17:22])
        right_eyebrow_position = calculate_eyebrow_position(shape[22:27])

        # Display the blink count and eyebrow positions
        cv2.putText(clahe_image, "Blinks: {}".format(total_blinks), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(clahe_image, "Left Eyebrow: {:.2f}".format(left_eyebrow_position), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(clahe_image, "Right Eyebrow: {:.2f}".format(right_eyebrow_position), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow("Frame", clahe_image)

    # Check for key press to exit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Release the video capture and close windows
cv2.destroyAllWindows()
cap.release()
