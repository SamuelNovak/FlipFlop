import random, os, io, base64
from flask import Flask, render_template, request, jsonify, send_file, abort
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
from urllib.parse import urlparse, urljoin

import process_img

load_dotenv()


credentials = CognitiveServicesCredentials(os.environ['face_api_key'])
face_client = FaceClient(os.environ['face_api_endpoint'], credentials=credentials)

emotions = ['anger','contempt','disgust','fear','happiness','sadness','surprise']

app = Flask(__name__)

def best_emotion(emotion):
    emotions = {}
    emotions['anger'] = emotion.anger
    emotions['contempt'] = emotion.contempt
    emotions['disgust'] = emotion.disgust
    emotions['fear'] = emotion.fear
    emotions['happiness'] = emotion.happiness
    emotions['neutral'] = emotion.neutral
    emotions['sadness'] = emotion.sadness
    emotions['surprise'] = emotion.surprise
    return max(zip(emotions.values(), emotions.keys()))[1]

app = Flask(__name__, static_folder="ou_mama_web")

@app.route('/face', methods=['POST'])
def check_results():
    body = request.get_json()

    image_bytes = base64.b64decode(body['image_base64'].split(',')[1])
    image = io.BytesIO(image_bytes)

    faces = face_client.face.detect_with_stream(image,
                                                return_face_attributes=['emotion', "hair"],
                                                return_face_landmarks=True)

    if len(faces) == 1:
        detected_emotion = best_emotion(faces[0].face_attributes.emotion)
        landmarks = faces[0].face_landmarks.serialize()
        rect = faces[0].face_rectangle.as_dict()
        new_img = "data:image/jpeg;base64," \
            + base64.b64encode(process_img.process(image_bytes, detected_emotion, rect, landmarks)).decode()
        hair = faces[0].face_attributes.hair.serialize()
        return jsonify({
            "status": "ok",
            "emotion": detected_emotion,
            "all_emotions": faces[0].face_attributes.emotion.serialize(),
            "face_rectangle": rect,
            "face_landmarks": landmarks,
            "image_base64": new_img,
            "hair": hair})
    elif len(faces) > 1:
        return jsonify({"status": "error", "message": "Only one face allowed in the picture."})
    else:
        return jsonify({"status": "error", "message": "No face detected."})


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
            ref_url.netloc == test_url.netloc and \
            not ".." in target

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def static_path(path):
    if not path:
        return send_file("static/docs/index.html")
    if is_safe_url(path):
        try:
            return send_file(urljoin("static/docs/", path))
        except:
            return abort(404)
    else:
        return abort(403)
