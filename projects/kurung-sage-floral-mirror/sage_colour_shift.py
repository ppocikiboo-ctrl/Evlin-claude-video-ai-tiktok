# Shift the olive/yellow-green fabric toward the cooler grey-sage of the product photo.
import sys, subprocess, numpy as np, cv2
src, dst = sys.argv[1], sys.argv[2]
W, H = 720, 1280
rd = subprocess.Popen(['ffmpeg','-v','error','-i',src,'-f','rawvideo','-pix_fmt','bgr24','-'], stdout=subprocess.PIPE)
wr = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r','24','-i','-',
                       '-c:v','libx264','-crf','10','-preset','fast','-pix_fmt','yuv420p',dst], stdin=subprocess.PIPE)
def ramp(x, a, b):  # 0 at a, 1 at b
    return np.clip((x - a) / (b - a), 0, 1)
n = W * H * 3
while True:
    buf = rd.stdout.read(n)
    if len(buf) < n: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = ramp(h, 20, 24) * (1 - ramp(h, 60, 70)) * ramp(s, 12, 20) * (1 - ramp(s, 140, 170))
    m = cv2.GaussianBlur(m, (0, 0), 1.5)
    h2 = h + 9 * m            # yellow-olive -> sage green
    s2 = s * (1 - 0.25 * m)   # a little greyer
    v2 = np.clip(v * (1 + 0.06 * m), 0, 255)
    out = cv2.cvtColor(np.dstack([h2, s2, v2]).astype(np.uint8), cv2.COLOR_HSV2BGR)
    wr.stdin.write(out.tobytes())
wr.stdin.close(); wr.wait(); rd.wait()
