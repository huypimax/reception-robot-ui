import threading, requests, time, os
from PyQt6.QtCore import QUrl, QTimer, QLoggingCategory, QStandardPaths
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWidgets import QWidget, QVBoxLayout

# Tắt log Qt WebEngine
QLoggingCategory.setFilterRules("qt.webenginecontext=false")

def tune_webengine_profile():
    """Thiết lập cache và bật các thuộc tính trên PROFILE & VIEW-agnostic."""
    profile = QWebEngineProfile.defaultProfile()

    # Đường dẫn cache/storage
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

    # ⚠️ Thay vì defaultSettings(), dùng settings() từ profile cho tương thích PyQt6 cũ
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

        # Gọi tune trước khi tạo view
        tune_webengine_profile()

        self.url_str = "https://hcmut.edu.vn/virtual-tour/"
        self.url = QUrl(self.url_str)

        self.browser = QWebEngineView(self)
        self.browser.setUrl(self.url)

        # Bật attributes ở mức VIEW (phòng khi profile settings không đủ trên bản Qt)
        vs = self.browser.settings()
        vs.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        vs.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        vs.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)

        # Giảm zoom để nhẹ tải raster
        self.browser.setZoomFactor(0.8)  # thử 0.75 nếu còn nặng

        layout = self.ui.web_layout.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.web_layout)
            self.ui.web_layout.setLayout(layout)
        layout.addWidget(self.browser)

        self.connected = True
        self.check_thread = threading.Thread(target=self.check_connection_loop, daemon=True)
        self.check_thread.start()

        # Kiểm tra WebGL có thực sự bật không (in cảnh báo nếu không)
        self.browser.page().runJavaScript("""
            (function(){
                try{
                  const c=document.createElement('canvas');
                  const gl=c.getContext('webgl')||c.getContext('experimental-webgl');
                  return !!(window.WebGLRenderingContext && gl);
                }catch(e){return false;}
            })();
        """, self._on_webgl_checked)

    def _on_webgl_checked(self, has_webgl):
        if not has_webgl:
            print("[WARN] WebGL không khả dụng (có thể đang Software). Kiểm tra driver GPU & flags.")

    def check_connection_loop(self):
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
        self.browser.setUrl(self.url)
