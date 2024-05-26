from flask import Flask, render_template, Response, request
import socket
import struct
import numpy as np
import cv2
import pickle

app = Flask(__name__, static_folder='static', template_folder='templates')

# 라즈베리 파이 서버의 주소와 포트
HOST_RPI = '192.168.137.29'
PORT_VIDEO = 8089
PORT_CONTROL = 8090

# 라즈베리 파이로부터 영상을 수신하는 함수
def gen_frames():
    client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_cam.connect((HOST_RPI, PORT_VIDEO))

    while True:
        data_len_bytes = client_cam.recv(4)
        data_len = struct.unpack('!L', data_len_bytes)[0]
        frame_data = b''
        while len(frame_data) < data_len:
            frame_data += client_cam.recv(data_len - len(frame_data))

        frame = pickle.loads(frame_data)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/introduce')
def introduce():
    return render_template('introduce.html')

@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    command = request.form['command']
    client_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_control.connect((HOST_RPI, PORT_CONTROL))
    client_control.send(command.encode('utf-8'))
    client_control.close()
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
