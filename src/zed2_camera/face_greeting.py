#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Face Greeting Script v4.2 (Debounce + Hysteresis + Single-greet-per-presence)
-----------------------------------------------------------------------------
Fixes:
- Không chào liên tục khi đứng yên: dùng đếm khung (debounce) + hysteresis "near".
- Chỉ chào 1 lần cho mỗi lượt hiện diện (presence). Kết thúc lượt khi không có mặt đủ lâu.
- Giảm lag: thread lấy hình riêng + phát WAV async.

Logic chính:
1) Xác nhận "có mặt" khi có khuôn mặt trong >= FACE_ON_FRAMES khung liên tiếp.
2) Xác nhận "mất mặt" khi không có khuôn mặt trong >= FACE_OFF_FRAMES khung liên tiếp.
3) NEAR hysteresis:
   - Chỉ coi là "near" khi face_frac_ema >= NEAR_ENTER.
   - Rời "near" chỉ khi face_frac_ema < NEAR_EXIT (NEAR_EXIT < NEAR_ENTER).
4) Greet khi: chuyển từ (not near) -> (near) TRONG KHI presence_active == True và chưa chào trong lượt.
5) Chỉ cho phép start lượt mới để chào lại khi đã "mất mặt" đủ lâu (>= ABSENCE_RESET_SEC).

Cài đặt:
    pip install opencv-python simpleaudio pyttsx3
Chạy:
    python face_greeting_v4_2.py
"""

import cv2
import time
import os
import threading
import tempfile
import platform
import subprocess

# ================== Cấu hình ==================
CAM_INDEX = 0
SHOW_WINDOW = True
GREETING_TEXT = "Hello, I'm AIko, your receptionist assistant, how can I help you?"

# Ngưỡng gần (hysteresis)
NEAR_ENTER = 0.12            # vào trạng thái "near" khi face_frac_ema >= 0.12
NEAR_EXIT  = 0.10            # rời "near" khi face_frac_ema <  0.10 (để tránh rung)

# Debounce theo khung
FACE_ON_FRAMES  = 5          # cần >=5 khung liên tiếp có mặt để coi là 'có mặt' (presence)
FACE_OFF_FRAMES = 10         # cần >=10 khung liên tiếp không mặt để coi là 'mất mặt'
NEAR_ON_FRAMES  = 3          # cần >=3 khung liên tiếp vượt NEAR_ENTER để 'ổn định near' trước khi chào

# Reset sau khi vắng mặt
ABSENCE_RESET_SEC = 3.0      # không thấy mặt >= 3s mới được chào lượt mới

# Làm mượt kích thước khuôn mặt
EMA_ALPHA = 0.3              # ema cho face_frac

# Tốc độ vòng lặp
DETECT_INTERVAL = 0.02

# Output audio file (pre-synthesized)
GREETING_WAV = os.path.join(tempfile.gettempdir(), "aiko_greeting.wav")

# ==============================================
def ensure_greeting_wav():
    """Tạo WAV cho câu chào 1 lần để phát nhanh, không tốn CPU ở runtime."""
    if os.path.exists(GREETING_WAV) and os.path.getsize(GREETING_WAV) > 1024:
        return
    try:
        if platform.system().lower().startswith('win'):
            # PowerShell System.Speech synthesize to WAV
            text = GREETING_TEXT.replace("'", "''")
            ps = (
                "[void][Reflection.Assembly]::LoadWithPartialName('System.Speech');"
                "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
                "$s.Rate=-2;"
                f"$s.SetOutputToWaveFile('{GREETING_WAV}');"
                f"$s.Speak('{text}');"
                "$s.Dispose();"
            )
            subprocess.check_call(["powershell", "-NoProfile", "-Command", ps])
        else:
            # Fallback: pyttsx3
            try:
                import pyttsx3
                engine = pyttsx3.init()
                rate = engine.getProperty('rate')
                engine.setProperty('rate', rate - 20)
                engine.save_to_file(GREETING_TEXT, GREETING_WAV)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print("[TTS] Fallback synthesis error:", e)
    except Exception as e:
        print("[TTS] Synthesis error:", e)

def play_greeting_async():
    """Phát file WAV không chặn luồng chính."""
    if platform.system().lower().startswith('win'):
        import winsound
        try:
            winsound.PlaySound(GREETING_WAV, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print("[AUDIO] winsound error:", e)
    else:
        try:
            import simpleaudio as sa
            def _run():
                try:
                    wave_obj = sa.WaveObject.from_wave_file(GREETING_WAV)
                    wave_obj.play()  # async
                except Exception as _e:
                    print("[AUDIO] simpleaudio error:", _e)
            threading.Thread(target=_run, daemon=True).start()
        except Exception as e:
            print("[AUDIO] simpleaudio not available:", e)

class FrameGrabber(threading.Thread):
    def __init__(self, cam_index):
        super().__init__(daemon=True)
        self.cam_index = cam_index
        self.cap = None
        self.frame_lock = threading.Lock()
        self.latest = None
        self.running = threading.Event()

    def open(self):
        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_MSMF)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.cam_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {self.cam_index}")
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        # Gợi ý giảm độ phân giải nếu muốn mượt hơn:
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def run(self):
        self.running.set()
        while self.running.is_set():
            ok, frame = self.cap.read()
            if not ok:
                continue
            with self.frame_lock:
                self.latest = frame
        self.cap.release()

    def get_latest(self):
        with self.frame_lock:
            return None if self.latest is None else self.latest.copy()

    def stop(self):
        self.running.clear()

def main():
    cv2.setNumThreads(1)

    # Nạp cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        raise RuntimeError("Cannot load haarcascade_frontalface_default.xml")

    ensure_greeting_wav()

    grabber = FrameGrabber(CAM_INDEX)
    grabber.open()
    grabber.start()

    # Trạng thái
    face_on_count = 0          # đếm khung có mặt liên tiếp
    face_off_count = 0         # đếm khung không mặt liên tiếp
    presence_active = False
    greeted_this_presence = False
    no_face_start_ts = None    # thời điểm bắt đầu không thấy mặt (để tính ABSENCE_RESET_SEC)

    # near hysteresis
    face_frac_ema = None
    near_raw = False           # đánh dấu tức thời (không hysteresis)
    near_state = False         # sau hysteresis
    near_on_count = 0          # đếm khung liên tiếp vượt NEAR_ENTER để xác nhận near ổn định

    print("Running v4.2... Press 'q' to quit.")
    try:
        while True:
            frame = grabber.get_latest()
            if frame is None:
                time.sleep(0.005)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60)
            )

            # Chọn mặt lớn nhất
            best = None
            best_area = 0
            for (x, y, w, h) in faces:
                area = w * h
                if area > best_area:
                    best_area = area
                    best = (x, y, w, h)

            H, W = frame.shape[:2]
            now = time.time()

            if best is not None:
                x, y, w, h = best
                face_frac = w / float(W)

                # Cập nhật EMA face_frac
                if face_frac_ema is None:
                    face_frac_ema = face_frac
                else:
                    face_frac_ema = EMA_ALPHA * face_frac + (1 - EMA_ALPHA) * face_frac_ema

                # Debounce presence ON
                face_on_count += 1
                face_off_count = 0

                # Xác nhận presence nếu đủ khung
                if not presence_active and face_on_count >= FACE_ON_FRAMES:
                    # Chỉ cho phép bắt đầu presence mới nếu đã vắng mặt đủ lâu
                    allow_new_presence = True
                    if no_face_start_ts is not None:
                        allow_new_presence = (now - no_face_start_ts) >= ABSENCE_RESET_SEC
                    if allow_new_presence:
                        presence_active = True
                        greeted_this_presence = False
                        # reset các biến near
                        near_state = False
                        near_on_count = 0
                        # Reset mốc vắng mặt
                        no_face_start_ts = None

                # Hysteresis near detection
                if face_frac_ema >= NEAR_ENTER:
                    near_raw = True
                    near_on_count += 1
                elif face_frac_ema < NEAR_EXIT:
                    near_raw = False
                    near_on_count = 0  # reset đếm nếu rời near

                # Nếu đã presence, chưa chào, và "near" ổn định đủ khung -> chào
                if presence_active and (not greeted_this_presence):
                    if (not near_state) and near_raw and (near_on_count >= NEAR_ON_FRAMES):
                        near_state = True  # chuyển trạng thái near
                        print("Phát hiện người mới & đủ gần. Xin chào! (v4.2)")
                        play_greeting_async()
                        greeted_this_presence = True

                # Vẽ
                if SHOW_WINDOW:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"frac={face_frac:.2f} ema={face_frac_ema:.2f} near={int(near_state)}",
                                (x, max(0, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            else:
                # Không thấy mặt
                face_on_count = 0
                face_off_count += 1

                # Bắt đầu mốc không thấy mặt
                if no_face_start_ts is None:
                    no_face_start_ts = now

                # Nếu mất mặt đủ khung -> kết thúc presence
                if presence_active and face_off_count >= FACE_OFF_FRAMES:
                    presence_active = False
                    # Để lần sau cho phép start mới sau khi >= ABSENCE_RESET_SEC (đã đo từ no_face_start_ts)
                    # Reset các biến near/ema để tránh rung
                    face_frac_ema = None
                    near_state = False
                    near_on_count = 0

            if SHOW_WINDOW:
                cv2.imshow("Face Greeting v4.2 (Debounce/Hysteresis)", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            time.sleep(DETECT_INTERVAL)

    finally:
        grabber.stop()
        grabber.join()
        if SHOW_WINDOW:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
