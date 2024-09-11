from flask import Flask, render_template, Response, request
import socket
import cv2

app = Flask(__name__, static_folder='static', template_folder='templates')

# 라즈베리 파이 서버의 주소와 포트
HOST_RPI = '192.168.137.29'
PORT_VIDEO = 8089
PORT_CONTROL = 8090

# 라즈베리 파이로부터 영상을 수신하는 함수
def generate_video_stream():
    cap = cv2.VideoCapture('tcp://192.168.137.29:5000')  # 라즈베리파이에서 전송한 스트림을 받음

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html', current_page='home')

@app.route('/introduce')
def introduce():
    return render_template('introduce.html', current_page='introduce')

@app.route('/play')
def play():
    return render_template('play.html', current_page='play')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    command = request.form['command']
    print(f"Received command: {command}")

    # 라즈베리파이로 명령 전송
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_control:
        client_control.connect((HOST_RPI, PORT_CONTROL))
        client_control.send(command.encode('utf-8'))

    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
