from flask import Flask, request, jsonify
from scipy.spatial import distance as dist
from imutils import face_utils
import numpy as np
import imutils
import dlib
import cv2
from keras.preprocessing.image import img_to_array
from keras.models import load_model

app = Flask(__name__)
eye_brow_distances = []  # Define eye_brow_distances as a global variable

def calculate_eye_brow_distance(left_eye, right_eye):
    distance = dist.euclidean(left_eye, right_eye)
    eye_brow_distances.append(int(distance))
    return distance

def normalize_values(distances, disp):
    normalized_value = abs(disp - np.min(distances)) / abs(np.max(distances) - np.min(distances))
    stress_value = np.exp(-normalized_value)
    if stress_value >= 50:
        return stress_value, "High Stress"
    else:
        return stress_value, "Low Stress"

def detect_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = dlib.get_frontal_face_detector()
    detections = detector(gray, 0)
    return detections, gray

def extract_facial_landmarks(img, detection):
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    shape = predictor(img, detection)
    shape = face_utils.shape_to_np(shape)
    return shape

def process_image_file(file):
    img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
    img = imutils.resize(img, width=500, height=500)
    return img

def find_emotion_label(emotion_scores):
    EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]
    label = EMOTIONS[np.argmax(emotion_scores)]
    if label in ['scared', 'sad']:
        label = 'stressed'
    else:
        label = 'not stressed'
    return label

def find_emotion(img, detection, emotion_classifier):
    x, y, w, h = face_utils.rect_to_bb(detection)
    face_roi = img[y:y+h, x:x+w]
    roi = cv2.resize(face_roi, (64, 64))
    roi = roi.astype("float") / 255.0
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)
    emotion_scores = emotion_classifier.predict(roi)[0]
    return find_emotion_label(emotion_scores)

def process_image():
    # Load the image from the request
    file = request.files['image']
    img = process_image_file(file)

    detections, gray = detect_faces(img)

    emotion_classifier = load_model("_mini_XCEPTION.102-0.66.hdf5", compile=False)

    (left_brow_start, left_brow_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eyebrow"]
    (right_brow_start, right_brow_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eyebrow"]

    stress_value = 0.0  # Initialize stress_value with a default value
    stress_label = "Cannot identify face"  # Initialize stress_label with a default value
    for detection in detections:
        emotion_label = find_emotion(img, detection, emotion_classifier)
        shape = extract_facial_landmarks(img, detection)

        left_eyebrow = shape[left_brow_start:left_brow_end]
        right_eyebrow = shape[right_brow_start:right_brow_end]

        distance = calculate_eye_brow_distance(left_eyebrow[-1], right_eyebrow[0])
        stress_value, stress_label = normalize_values(eye_brow_distances, distance)

    response = {
        "stress_level": str(int(stress_value * 100)),
        "stress_label": stress_label
    }
    return jsonify(response)

@app.route('/process_image', methods=['POST'])
def process_image_route():
    return process_image()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
