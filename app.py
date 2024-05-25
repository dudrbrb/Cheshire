from flask import Flask, render_template, Response
import socket
import struct
import numpy as np
import cv2
import pickle

app = Flask(__name__, static_folder='static', template_folder='templates')

# 라즈베리 파이 서버의 주소와 포트
HOST_RPI = '192.168.137.29'
PORT = 8089

# 라즈베리 파이로부터 영상을 수신하는 함수
def gen_frames():
    client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_cam.connect((HOST_RPI, PORT))

    while True:
        # 영상 데이터 크기 수신
        data_len_bytes = client_cam.recv(4)
        data_len = struct.unpack('!L', data_len_bytes)[0]

        # 영상 데이터 수신
        frame_data = b''
        while len(frame_data) < data_len:
            frame_data += client_cam.recv(data_len - len(frame_data))

        # 수신한 데이터를 이미지로 디코딩하여 전송
        frame = pickle.loads(frame_data)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 홈 페이지를 렌더링하는 라우트
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/introduce')
def introduce():
    return render_template('introduce.html')

@app.route('/play')
def play():
    return render_template('play.html')

# 비디오 스트리밍을 제공하는 라우트
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
