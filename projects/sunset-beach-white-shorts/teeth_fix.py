# Fill the dark gaps between the teeth inside the inner-lip contour so the teeth read as one even row.
import sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
debug = len(sys.argv) > 4
W, H, FPS = 720, 1280, 30
INNER = [78,191,80,81,82,13,312,311,310,415,308,324,318,402,317,14,87,178,88,95]
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.VIDEO,
    num_faces=2, min_face_detection_confidence=0.3, min_tracking_confidence=0.3))
rd = subprocess.Popen(['ffmpeg','-v','error','-i',src,'-f','rawvideo','-pix_fmt','bgr24','-'], stdout=subprocess.PIPE)
wr = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
                       '-c:v','libx264','-crf','10','-preset','fast','-pix_fmt','yuv420p',dst], stdin=subprocess.PIPE)
n = W*H*3; i = 0; fixed = 0; tooth_ema = None
while True:
    buf = rd.stdout.read(n)
    if len(buf) < n: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
    res = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), int(i*1000/FPS))
    for face in (res.face_landmarks or []):
        pts = np.array([[p.x*W, p.y*H] for p in face], np.float32)
        poly = pts[INNER]
        gap = np.linalg.norm(pts[13]-pts[14]); width = np.linalg.norm(pts[78]-pts[308])
        if gap < 1.5 or width < 8: continue
        # supersampled mask for sub-pixel accuracy
        S = 4
        x0, y0 = np.floor(poly.min(0)).astype(int) - 4; x1, y1 = np.ceil(poly.max(0)).astype(int) + 4
        x0, y0 = max(x0,0), max(y0,0); x1, y1 = min(x1,W), min(y1,H)
        bw, bh = x1-x0, y1-y0
        if bw < 4 or bh < 3: continue
        m = np.zeros((bh*S, bw*S), np.uint8)
        cv2.fillPoly(m, [((poly-[x0,y0])*S).astype(np.int32)], 255, cv2.LINE_AA)
        m = cv2.resize(m, (bw, bh), interpolation=cv2.INTER_AREA).astype(np.float32)/255
        m = cv2.GaussianBlur(m, (0,0), 0.6)
        roi = img[y0:y1, x0:x1].astype(np.float32)
        lum = roi.mean(2)
        inside = m > 0.5
        if inside.sum() < 4: continue
        # tooth colour from the local light: cheek skin pushed toward off-white
        def patch(k):
            x, y = pts[k].astype(int); r = max(2, int(width*0.08))
            q = img[min(max(y-r,0),H-1):min(y+r,H), min(max(x-r,0),W-1):min(x+r,W)].reshape(-1,3).astype(np.float32)
            return np.median(q, 0)
        skin = (patch(50) + patch(280)) / 2
        white = min(230, skin.max()*0.88) * np.array([0.82, 0.92, 1.0], np.float32)
        c = 0.40*skin + 0.60*white
        tooth_ema = c if tooth_ema is None else 0.8*tooth_ema + 0.2*c
        yy = np.arange(bh, dtype=np.float32)[:, None]
        xs = np.arange(bw)+x0
        up = sorted(zip(poly[:11,0], poly[:11,1])); lo = sorted(zip(list(poly[10:,0])+[poly[0,0]], list(poly[10:,1])+[poly[0,1]]))
        ytop = np.interp(xs, *zip(*up))[None, :] - y0
        ybot = np.interp(xs, *zip(*lo))[None, :] - y0
        t = np.clip((yy - ytop) / np.maximum(ybot - ytop, 1), 0, 1)
        # upper teeth fill the top ~65%, with a soft shadowed biting edge below
        shade = np.where(t < 0.65, 0.80 + 0.20*np.sin(np.pi*np.clip(t/0.65, 0, 1)*0.9 + 0.15), 0.80 - 0.30*(t-0.65)/0.35)
        xx = np.arange(bw, dtype=np.float32)[None, :]
        cx = (pts[78,0]+pts[308,0])/2 - x0
        d = (xx - cx) / (width/2)
        # gentle separations between teeth: wider in front, narrower toward the sides
        k = np.sign(d) * (np.abs(d)**0.8) * 3.4
        sep = 1 - 0.10*np.exp(-((k - np.round(k))**2)/0.02) * (np.abs(d) > 0.05)
        shade = shade * sep
        shade = shade * (1 - 0.45*np.clip(np.abs(d) - 0.55, 0, 1)/0.45)
        fill = tooth_ema[None, None, :] * shade[..., None]
        fill = cv2.GaussianBlur(fill, (0,0), 0.45)
        # keep a trace of the original texture, but lift the dark gaps
        out = fill
        a = (m*0.85)[..., None]
        img[y0:y1, x0:x1] = np.clip(roi*(1-a) + out*a, 0, 255).astype(np.uint8)
        fixed += 1
    wr.stdin.write(img.tobytes()); i += 1
wr.stdin.close(); wr.wait(); rd.wait()
print('frames', i, 'mouth fixes', fixed)
