from flask import Flask, request, Response, render_template
import cv2
import time
import numpy as np


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/frame', methods=['POST'])
def handle_frame():
    frame = request.files['frame'].read()
    npimg = np.fromstring(frame, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    cv2.imwrite(f"realtime_frames/frame_{time.time()}.jpg", img)

    return Response("Frame received", status=200)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
