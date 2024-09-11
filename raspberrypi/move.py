import socket
from motor_control import *
import time
import RPi.GPIO as GPIO
import threading
import subprocess

# 서버 설정
HOST = '0.0.0.0'  # 라즈베리파이의 IP
PORT = 8090

# 모터 초기화
GPIO.setmode(GPIO.BCM)
initMotor()

def handle_command(command):
    print(f"Command received: {command}")
    
    if command == 'forward':
        goForward(SPEED_MAX_FB)
    elif command == 'backward':
        goBackward(SPEED_MAX_FB)
    elif command == 'left':
        turnLeft(SPEED_MAX_FB)
    elif command == 'right':
        turnRight(SPEED_MAX_FB)
    elif command == 'stop':
        stopMotor()

    time.sleep(0.1)  # 명령 실행 후 잠시 대기
    stopMotor()

# 모터 제어 서버 실행
def motor_control_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            print(f"Listening on {HOST}:{PORT}")

            while True:
                client_socket, addr = server_socket.accept()
                with client_socket:
                    print(f"Connected by {addr}")
                    command = client_socket.recv(1024).decode('utf-8')
                    if command:
                        handle_command(command)

    finally:
        stopMotor()
        exitMotor()
        GPIO.cleanup()

# GStreamer를 통해 카메라 스트리밍 실행
def start_camera_stream():
    gst_command = [
        'gst-launch-1.0', 'v4l2src', 'device=/dev/video0',
        '!', 'video/x-raw,width=640,height=480,framerate=30/1',
        '!', 'videoconvert', '!', 'jpegenc',
        '!', 'multipartmux', '!', 'tcpserversink', 'host=192.168.137.29', 'port=5000'
    ]
    subprocess.run(gst_command)

# 스레드를 사용하여 두 작업을 동시에 실행
if __name__ == "__main__":
    # 모터 제어 서버를 스레드로 실행
    motor_thread = threading.Thread(target=motor_control_server)
    motor_thread.start()

    # GStreamer 카메라 스트리밍을 스레드로 실행
    camera_thread = threading.Thread(target=start_camera_stream)
    camera_thread.start()

    # 두 스레드가 완료될 때까지 대기
    motor_thread.join()
    camera_thread.join()
