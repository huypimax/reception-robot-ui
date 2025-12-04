import pygame
import threading

# Khởi tạo mixer 1 lần ngay khi import module
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.init()
_mixer_lock = threading.Lock()

def play_audio(path: str):
    """Phát file âm thanh, đảm bảo không conflict bằng lock."""
    with _mixer_lock:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

def stop_audio():
    with _mixer_lock:
        pygame.mixer.music.stop()