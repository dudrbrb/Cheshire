import socket
import struct
import cv2
import pickle
import threading

# OpenCV를 통해 웹캠에 접근하기 위한 장치 설정
VIDSRC = 'v4l2src device=/dev/video0 ! video/x-raw,width=640,height=480,framerate=30/1 ! videoconvert ! appsink'

# 서버 설정
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에 바인딩
PORT = 8089       # 사용할 포트 번호

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

server.bind((HOST, PORT))
print('Socket bind complete')

server.listen(10)
print('Socket now listening')

# 클라이언트가 연결될 때까지 대기하고 연결이 수립되면 클라이언트 소켓을 반환
server_cam, addr = server.accept()
print('New Client')

# 카메라 설정
cap = cv2.VideoCapture(VIDSRC, cv2.CAP_GSTREAMER)

# 영상 전송 함수
def send_frames():
    while True:
        # 카메라에서 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            break

        # 프레임을 직렬화하여 클라이언트로 전송
        data = pickle.dumps(frame)
        data_size = struct.pack('!L', len(data))
        server_cam.sendall(data_size + data)

# 영상 전송 스레드 시작
send_thread = threading.Thread(target=send_frames)
send_thread.start()

# 서버 종료 시 모든 리소스 정리
try:
    while True:
        pass
except KeyboardInterrupt:
    pass

send_thread.join()  # 스레드 종료 대기
server_cam.close()
server.close()
cap.release()  # 카메라 리소스 해제
cv2.destroyAllWindows()  # OpenCV 창 닫기
