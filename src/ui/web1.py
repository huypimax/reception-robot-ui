import threading, requests, time, os
from PyQt6.QtCore import QUrl, QTimer, QLoggingCategory, QStandardPaths
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEngineScript
from PyQt6.QtWidgets import QWidget, QVBoxLayout

QLoggingCategory.setFilterRules("qt.webenginecontext=false")

def inject_perf_script(profile: QWebEngineProfile, fps=30):
    """
    Tiêm script JavaScript để giới hạn tốc độ khung hình (FPS) cho trang web.
    Loại bỏ hoàn toàn các can thiệp vào canvas để tránh lỗi WebGL.
    """
    js = f"""
(() => {{
    const FPS = {fps};

    function safeRun() {{
        try {{
            // Giới hạn tốc độ khung hình (Throttle rAF)
            const nativeRAF = window.requestAnimationFrame.bind(window);
            let last = 0, interval = 1000 / FPS;
            window.requestAnimationFrame = (cb) => nativeRAF(function onTick(t) {{
                if (t - last >= interval) {{ 
                    last = t;
                    cb(t); 
                }}
                else {{ 
                    nativeRAF(onTick); 
                }}
            }});
        }} catch (e) {{
            // Nuốt lỗi
        }}
    }}

    if (document.readyState === 'complete' || document.readyState === 'interactive') {{
        safeRun();
    }} else {{
        document.addEventListener('DOMContentLoaded', safeRun, {{ once: true }});
    }}
}})();
"""
    script = QWebEngineScript()
    script.setName("PerfTuner")
    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
    script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
    script.setRunsOnSubFrames(False)
    script.setSourceCode(js)
    profile.scripts().insert(script)

def tune_profile_and_settings():
    """
    Cấu hình hồ sơ và cài đặt của QWebEngineProfile để tối ưu hiệu suất.
    """
    profile = QWebEngineProfile.defaultProfile()

    # Bật cache đĩa để giảm tải mạng
    cache_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation), "web_cache")
    storage_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation), "web_storage")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(storage_dir, exist_ok=True)
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    profile.setCachePath(cache_dir)
    profile.setPersistentStoragePath(storage_dir)
    profile.setHttpCacheMaximumSize(256 * 1024 * 1024)

    s = profile.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)

    # Chỉ chèn script giới hạn FPS
    inject_perf_script(profile, fps=40)

class WebTab1(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

        tune_profile_and_settings()

        self.url_str = "https://hcmut.edu.vn/virtual-tour/"
        self.url = QUrl(self.url_str)

        self.browser = QWebEngineView(self)
        self.browser.setUrl(self.url)

        # Đặt Zoom về 1.0 để hiển thị đúng kích thước
        self.browser.setZoomFactor(1.0) 

        layout = self.ui.web_layout.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.web_layout)
            self.ui.web_layout.setLayout(layout)
        layout.addWidget(self.browser)

        self.connected = True
        self.check_thread = threading.Thread(target=self.check_connection_loop, daemon=True)
        self.check_thread.start()

        self.browser.page().runJavaScript("""
            (function() {
                try {
                    const c=document.createElement('canvas');
                    const gl=c.getContext('webgl')||c.getContext('experimental-webgl');
                    return !!(window.WebGLRenderingContext && gl);
                } catch(e) {
                    return false;
                }
            })();
        """, lambda ok: print("[WARN] WebGL có thể đang Software!" if not ok else "[OK] WebGL sẵn sàng"))

    def check_connection_loop(self):
        while True:
            try:
                res = requests.get(self.url_str, timeout=5)
                if res.status_code == 200:
                    if not self.connected:
                        self.connected = True
                        QTimer.singleShot(0, self.restore_browser)
                else:
                    raise Exception("bad status")
            except:
                if self.connected:
                    self.connected = False
            time.sleep(5)

    def restore_browser(self):
        self.browser.setUrl(self.url)