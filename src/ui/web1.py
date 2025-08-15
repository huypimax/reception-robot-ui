import threading
import requests
import time
import os
from PyQt6.QtCore import QUrl, QTimer, QLoggingCategory, QStandardPaths
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWidgets import QWidget, QVBoxLayout

# Tắt log Qt WebEngine để tránh spam console
QLoggingCategory.setFilterRules("qt.webenginecontext=false")

def tune_webengine_profile():
    """Cấu hình WebEngine để giả lập trình duyệt Cốc Cốc và tối ưu hiệu năng."""
    profile = QWebEngineProfile.defaultProfile()

    # Set user-agent giả làm trình duyệt Cốc Cốc
    coccoc_user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36 "
        "CocCocBrowser/117.0.145"
    )
    profile.setHttpUserAgent(coccoc_user_agent)

    # Thiết lập cache và storage
    cache_dir = os.path.join(
        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation),
        "web_cache"
    )
    storage_dir = os.path.join(
        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation),
        "web_storage"
    )
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(storage_dir, exist_ok=True)

    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    profile.setCachePath(cache_dir)
    profile.setPersistentStoragePath(storage_dir)
    profile.setHttpCacheMaximumSize(256 * 1024 * 1024)  # 256MB

    # Cấu hình các attribute hỗ trợ WebGL, tăng tốc
    s = profile.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)


class WebTab1(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

        # Thiết lập profile trước khi tạo browser
        tune_webengine_profile()

        self.url_str = "https://hcmut.edu.vn/virtual-tour/"
        self.url = QUrl(self.url_str)

        # Tạo trình duyệt WebEngineView
        self.browser = QWebEngineView(self)
        self.browser.setUrl(self.url)

        # Cấu hình attribute riêng cho view (phòng trường hợp profile không đủ)
        vs = self.browser.settings()
        vs.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        vs.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        vs.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)

        # Giảm zoom để nhẹ tải hiển thị (75-80%)
        self.browser.setZoomFactor(0.8)

        # Inject JS để xử lý hình ảnh (tuỳ chỉnh thêm nếu cần)
        # self.browser.loadFinished.connect(self.inject_js_to_reduce_image_quality)

        # Gắn browser vào layout giao diện chính
        layout = self.ui.web_layout.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.web_layout)
            self.ui.web_layout.setLayout(layout)
        layout.addWidget(self.browser)

        # Bắt đầu luồng kiểm tra kết nối
        self.connected = True
        self.check_thread = threading.Thread(target=self.check_connection_loop, daemon=True)
        self.check_thread.start()

        # Kiểm tra WebGL có thực sự được bật không
        self.browser.page().runJavaScript("""
            (function(){
                try {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                    return !!(window.WebGLRenderingContext && gl);
                } catch (e) {
                    return false;
                }
            })();
        """, self._on_webgl_checked)

    def _on_webgl_checked(self, has_webgl):
        if not has_webgl:
            print("[⚠️ WARN] WebGL không khả dụng — kiểm tra lại driver GPU, flags Chromium, hoặc tắt Remote Desktop.")

    def check_connection_loop(self):
        """Luồng chạy nền kiểm tra kết nối mỗi 5 giây."""
        while True:
            try:
                res = requests.get(self.url_str, timeout=2)
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
        """Tải lại trang nếu mất kết nối trước đó."""
        self.browser.setUrl(self.url)

    def inject_js_to_reduce_image_quality(self):
        """Tuỳ chọn: thay ảnh nặng bằng ảnh nhẹ (nếu có phiên bản `_low.jpg`)."""
        js_script = """
        const imgs = document.querySelectorAll("img");
        imgs.forEach(img => {
            if (img.src.includes(".jpg")) {
                const lowSrc = img.src.replace(".jpg", "_low.jpg");
                img.src = lowSrc;
            }
        });
        """
        self.browser.page().runJavaScript(js_script)
