import argparse
import asyncio
import json
import os
import platform

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer

pcs = set()
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>AR Stream Viewer</title></head>
<body style="margin:0;background:#000;">
<video id="v" autoplay playsinline style="width:100vw;height:100vh;object-fit:contain;"></video>
<script>
(async () => {
  const pc = new RTCPeerConnection();
  const video = document.getElementById('v');
  pc.ontrack = (event) => { video.srcObject = event.streams[0]; };

  const offer = await pc.createOffer({offerToReceiveVideo: true, offerToReceiveAudio: false});
  await pc.setLocalDescription(offer);

  const resp = await fetch('/offer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})
  });
  const answer = await resp.json();
  await pc.setRemoteDescription(new RTCSessionDescription(answer));
})();
</script>
</body>
</html>
"""

def create_player(args):
    # Chọn backend capture theo OS
    sys = platform.system().lower()
    if sys == "windows":
        # Capture toàn màn hình (gdigrab). Có thể thay -offset_x/-offset_y/-video_size để crop 1 cửa sổ.
        return MediaPlayer(
            "desktop", format="gdigrab",
            options={
                "framerate": str(args.fps),
                "video_size": args.resolution  # ví dụ "1280x720"
            }
        )
    elif sys == "linux":
        # Linux: x11grab, cần DISPLAY và độ phân giải.
        display = os.environ.get("DISPLAY", ":0.0")
        return MediaPlayer(
            f"{display}+0,0", format="x11grab",
            options={
                "framerate": str(args.fps),
                "video_size": args.resolution
            }
        )
    else:
        raise RuntimeError("OS chưa được cấu hình capture. Hãy dùng Windows/Linux.")

async def index(request):
    return web.Response(content_type="text/html", text=INDEX_HTML)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    # Giới hạn bitrate để mạng LAN/IPC ổn định hơn (ví dụ 2.5 Mbps)
    # Lưu ý: đặt sau khi addTrack và trước khi createAnswer.
    player = request.app["player"]
    if player and player.video:
        video_track = player.video

        @video_track.on("ended")
        async def on_ended():
            print("Video track ended.")

        sender = pc.addTrack(video_track)

        # Thiết lập bitrate (nếu trình duyệt hỗ trợ)
        params = sender.getParameters()
        if params.encodings is None or len(params.encodings) == 0:
            params.encodings = [{}]
        params.encodings[0]["maxBitrate"] = 2_500_000  # 2.5 Mbps
        await sender.setParameters(params)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--resolution", default="1280x720")  # hạ xuống để mượt
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()

    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer)

    # Khởi tạo MediaPlayer (capture desktop)
    app["player"] = create_player(args)

    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
