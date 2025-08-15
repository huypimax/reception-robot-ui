import threading, requests, time, os
from PyQt6.QtCore import QUrl, QTimer, QLoggingCategory, QStandardPaths
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEngineScript
from PyQt6.QtWidgets import QWidget, QVBoxLayout

QLoggingCategory.setFilterRules("qt.webenginecontext=false")

def inject_perf_script(profile: QWebEngineProfile, fps=30, canvas_scale=0.7, css_zoom=0.85):
    js = f"""
(() => {{
  const FPS = {fps};
  const CANVAS_SCALE = {canvas_scale};
  const CSS_ZOOM = {css_zoom};

  // An toàn: chờ DOM sẵn sàng
  function safeRun() {{
    try {{
      const root = document && document.documentElement;
      const body = document && document.body;
      if (root && root.style) root.style.zoom = CSS_ZOOM;
      else if (body && body.style) body.style.zoom = CSS_ZOOM;

      // Throttle rAF
      const nativeRAF = window.requestAnimationFrame.bind(window);
      let last = 0, interval = 1000 / FPS;
      window.requestAnimationFrame = (cb) => nativeRAF(function onTick(t) {{
        if (t - last >= interval) {{ last = t; cb(t); }}
        else {{ nativeRAF(onTick); }}
      }});

      // Downscale canvas
      function tweakCanvas(c) {{
        try {{
          const rect = c.getBoundingClientRect();
          const w = Math.max(1, (rect.width  * CANVAS_SCALE) | 0);
          const h = Math.max(1, (rect.height * CANVAS_SCALE) | 0);
          if (c.width !== w || c.height !== h) {{
            c.width = w; c.height = h;
            const ctx = c.getContext('2d');
            if (ctx && 'imageSmoothingEnabled' in ctx) ctx.imageSmoothingEnabled = true;
          }}
        }} catch (e) {{}}
      }}
      function scan() {{
        try {{ document.querySelectorAll('canvas').forEach(tweakCanvas); }} catch (e) {{}}
      }}
      new MutationObserver(scan).observe(document.documentElement || document, {{ childList:true, subtree:true }});
      window.addEventListener('resize', scan);
      scan();

      // Hooks cho Three.js / Babylon / PlayCanvas (bọc try-catch)
      try {{
        if (window.THREE && THREE.WebGLRenderer) {{
          const _spr = THREE.WebGLRenderer.prototype.setPixelRatio;
          THREE.WebGLRenderer.prototype.setPixelRatio = function(r) {{
            return _spr ? _spr.call(this, Math.min(r, CANVAS_SCALE)) : undefined;
          }};
          const _ss = THREE.WebGLRenderer.prototype.setSize;
          THREE.WebGLRenderer.prototype.setSize = function(w,h,upd) {{
            return _ss.call(this, (w*CANVAS_SCALE)|0, (h*CANVAS_SCALE)|0, upd);
          }};
        }}
      }} catch(e) {{}}

      try {{
        if (window.BABYLON && BABYLON.Engine) {{
          const _setH = BABYLON.Engine.prototype.setHardwareScalingLevel;
          BABYLON.Engine.prototype.setHardwareScalingLevel = function(lvl) {{
            const target = Math.max(lvl, 1 / CANVAS_SCALE);
            return _setH.call(this, target);
          }};
        }}
      }} catch(e) {{}}

      try {{
        if (window.pc && pc.GraphicsDevice) {{
          pc.GraphicsDevice.prototype.maxPixelRatio = Math.min(1, CANVAS_SCALE);
        }}
      }} catch(e) {{}}
    }} catch (e) {{
      // nuốt lỗi
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
    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)  # <= đổi sang DocumentReady
    script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
    script.setRunsOnSubFrames(False)  # <= chỉ khung chính để tránh iframe lạ
    script.setSourceCode(js)
    profile.scripts().insert(script)

def tune_profile_and_settings():
    profile = QWebEngineProfile.defaultProfile()
    # Bật cache đĩa để giảm tải mạng/tái tải
    cache_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation), "web_cache")
    storage_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation), "web_storage")
    os.makedirs(cache_dir, exist_ok=True); os.makedirs(storage_dir, exist_ok=True)
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    profile.setCachePath(cache_dir); profile.setPersistentStoragePath(storage_dir)
    profile.setHttpCacheMaximumSize(256 * 1024 * 1024)

    s = profile.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)

    # Chèn script giảm tải (bạn có thể chỉnh thông số tại đây)
    inject_perf_script(profile, fps=30, canvas_scale=0.7, css_zoom=0.85)

class WebTab1(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

        tune_profile_and_settings()

        self.url_str = "https://hcmut.edu.vn/virtual-tour/"
        self.url = QUrl(self.url_str)

        self.browser = QWebEngineView(self)
        self.browser.setUrl(self.url)

        # Giảm zoom phía Qt thêm một lớp (giảm pixel vẽ)
        self.browser.setZoomFactor(0.75)  # thử 0.75–0.9

        layout = self.ui.web_layout.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.web_layout)
            self.ui.web_layout.setLayout(layout)
        layout.addWidget(self.browser)

        self.connected = True
        self.check_thread = threading.Thread(target=self.check_connection_loop, daemon=True)
        self.check_thread.start()

        # Báo nếu WebGL không hoạt động phần cứng
        self.browser.page().runJavaScript("""
            (()=>{
                try{
                  const c=document.createElement('canvas');
                  const gl=c.getContext('webgl')||c.getContext('experimental-webgl');
                  return !!(window.WebGLRenderingContext && gl);
                }catch(e){return false;}
            })();
        """, lambda ok: print("[WARN] WebGL có thể đang Software!" if not ok else "[OK] WebGL sẵn sàng"))

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
