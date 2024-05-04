from flask import Flask, request, Response, render_template, jsonify
import requests
import cv2
import time
import numpy as np

app = Flask(__name__)

verified = False


@app.route('/single')
def single_image():
    return render_template('single.html')


@app.route('/send_photo', methods=['POST'])
def send_photo():
    photo = request.files['photo']
    headers = {'Authorization': 'RCJ8v4u8YlK7bKxhGEuRPw0hRmT1nF0xXe6nr3q4oTI'}
    response = requests.post('http://localhost:8000/single_frame',
                             files={'file': (photo.filename, photo.stream, photo.mimetype)}, headers=headers)
    return response.text



@app.route('/')
def index():
    api_key = get_temp_key()
    print(api_key)
    return render_template('index.html', api_key=api_key)


@app.route('/frame', methods=['POST'])
def handle_frame():
    frame = request.files['frame'].read()
    npimg = np.fromstring(frame, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    cv2.imwrite(f"realtime_frames/frame_{time.time()}.jpg", img)

    return Response("Frame received", status=200)


@app.route('/receive_result', methods=['POST'])
def receive_message():
    global verified
    if not request.is_json:
        return jsonify({"error": "Invalid request, JSON required"}), 400

    data = request.get_json()

    if 'api_key' not in data or 'message' not in data:
        return jsonify({"error": "Missing 'api_key' or 'message'"}), 400

    if data['api_key'] != 'your_secret_key':
        return jsonify({"error": "Invalid API key"}), 403

    if data['message'] != 'verified':
        verified = True

    return jsonify({"status": "success", "message": "Message received successfully"})


@app.route('/get-temp-key')
def get_temp_key():
    api_key = "RCJ8v4u8YlK7bKxhGEuRPw0hRmT1nF0xXe6nr3q4oTI"
    response = requests.post('http://localhost:8000/generate-temp-key', json={"api_key": api_key})
    print(response)
    if response.status_code == 200:
        data = response.json()
        new_temp_key = data['new_temp_key']
        return new_temp_key
    else:
        return jsonify({"error": "Failed to generate temp key", "status_code": response.status_code})


@app.route('/events')
def events():
    def generate():
        yield "data: {}\n\n".format({"message": "Верификация успешна"})

    def generate_false():
        yield "data: {}\n\n".format({"message": "Верификация не успешна)"})

    if verified:
        return Response(generate(), mimetype='text/event-stream')
    else:
        return Response(generate_false(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
