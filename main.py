from collections import deque
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import cv2
import numpy as np  # NumPy 사용
import threading

# 최근 3개의 모션 감지 기록을 저장할 deque 생성
motion_records = deque(maxlen=100)

# 모션 감지 설정값
MOTION_THRESHOLD = 100  # 모션 감지 임계값

# HTTP 서버 설정값
HTTP_PORT = 23481


class MotionDetectionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            records_list = sorted(list(motion_records),
                                  key=lambda x: x['timestamp'], reverse=True)
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="icon" href="./favicon.ico" type="image/x-icon">
                <style>
                    body { font-family: Arial, sans-serif; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    @media (prefers-color-scheme: dark) {
                        body { background-color: #121212; color: #ffffff; }
                        th, td { border-color: #444; }
                        th { background-color: #333; }
                    }
                </style>
                <title>Motion Detection Records</title>
                <script>
                    setInterval(function() {
                        window.location.reload();
                    }, 5000);
                </script>
            </head>
            <body>
                <h2>Motion Detection Records</h2>
                <p>The page will refresh every 5 seconds while it is open.</p>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>Motion Value</th>
                        <th>Time Difference (seconds)</th>
                    </tr>
            """
            previous_timestamp = None
            for record in records_list:
                motion_value = record['motion_value']
                if motion_value > 20000:
                    motion_level = "Very High"
                elif motion_value > 10000:
                    motion_level = "High"
                elif motion_value > 5000:
                    motion_level = "Medium"
                elif motion_value > 1000:
                    motion_level = "Low"
                else:
                    motion_level = "Very Low"

                timestamp = datetime.strptime(
                    record['timestamp'], '%Y-%m-%d %H:%M:%S')
                time_diff = abs(int(
                    (timestamp - previous_timestamp).total_seconds())) if previous_timestamp else 0
                previous_timestamp = timestamp

                html_content += f"""
                    <tr>
                        <td>{timestamp.strftime('%m-%d %H:%M:%S')}</td>
                        <td>{motion_level}</td>
                        <td>{time_diff}</td>
                    </tr>
                """
            html_content += """
                </table>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode())
        elif self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            with open('favicon.ico', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()


def detect_motion():
    # 웹캠 초기화
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 24)  # FPS를 24로 설정

    # 첫 프레임 초기화
    ret, frame1 = cap.read()
    if not ret:
        print("Cannot open webcam!")
        return

    # 첫 프레임을 그레이스케일로 변환 및 가우시안 블러 적용
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)

    while True:
        ret, frame2 = cap.read()
        if not ret:
            break

        # 현재 프레임을 그레이스케일로 변환 및 가우시안 블러 적용
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

        # 프레임 차이 계산
        diff = cv2.absdiff(gray1, gray2)

        # 임계값 처리
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # NumPy를 사용하여 픽셀 합계 계산
        motion_pixels = float(np.sum(thresh) / 255)

        # 임계값을 넘는 움직임이 감지되면 기록
        if motion_pixels > MOTION_THRESHOLD:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if motion_records and motion_records[-1]['timestamp'] == current_time:
                if motion_records[-1]['motion_value'] < int(motion_pixels):
                    motion_records[-1]['motion_value'] = int(motion_pixels)
            else:
                motion_record = {
                    'timestamp': current_time,
                    'motion_value': int(motion_pixels),
                }
                motion_records.append(motion_record)
                print(f"Motion detected: {motion_record}")

        # 다음 비교를 위해 현재 프레임 저장
        gray1 = gray2

        # 모션 감지 창 표시 (디버깅용)
        cv2.imshow('Motion Detection', thresh)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 리소스 해제
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # 서버 설정
    server_address = ('', HTTP_PORT)
    httpd = HTTPServer(server_address, MotionDetectionHandler)

    # 모션 감지를 별도 스레드로 실행
    motion_thread = threading.Thread(target=detect_motion)
    motion_thread.daemon = True
    motion_thread.start()

    print(f"Server running on port {HTTP_PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server.")
        httpd.server_close()
