#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Weijie Zhang
"""Synthesize the Mandarin narration (MeloTTS via sherpa-onnx), compose the music bed,
duck the music under the voice and write build/mix.wav (20 s, 44.1 kHz stereo)."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve
import sherpa_onnx

SR, DUR = 44100, 20.0
N = int(SR*DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ.get("MELO_DIR", os.path.join(HERE, "models", "vits-melo-tts-zh_en"))
BUILD = os.path.join(HERE, "build"); os.makedirs(BUILD, exist_ok=True)

LINES = [
    (0.28,  3.30, "一个人没劲，一起才带劲。"),
    (3.48,  6.10, "出门走走，就有人等你。"),
    (6.38, 10.60, "打开 FindNet，附近谁在动，一看就知道。"),
    (10.82,14.60, "找到朋友，看他们在哪儿动，约上就出发。"),
    (14.88,17.58, "他们都在动，就差你一个。"),
    (17.72,20.00, "有伴才有劲，免费下载。"),
]

cfg = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=f"{D}/model.onnx", lexicon=f"{D}/lexicon.txt",
            tokens=f"{D}/tokens.txt", dict_dir=f"{D}/dict"),
        provider="cpu", num_threads=4),
    rule_fsts=f"{D}/date.fst,{D}/number.fst,{D}/phone.fst,{D}/new_heteronym.fst",
    max_num_sentences=1)
tts = sherpa_onnx.OfflineTts(cfg)

# pitch down 3% (and the matching 3% slowdown rides along as extra gravitas)
CHAIN = ("highpass=f=85,equalizer=f=200:t=q:w=1.0:g=1.5,"
         "equalizer=f=3000:t=q:w=1.4:g=2.0,"
         "acompressor=threshold=-20dB:ratio=2.8:attack=10:release=170:makeup=2,"
         "alimiter=limit=0.94")

def dur_of(p):
    o = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",p], capture_output=True, text=True)
    return float(o.stdout.strip())

VO = os.path.join(BUILD, "vo"); os.makedirs(VO, exist_ok=True)
vo = np.zeros(N); rep = []
for i,(t0,t1,txt) in enumerate(LINES):
    slot = t1-t0
    for speed in (1.02, 1.06, 1.10, 1.15, 1.20):
        a = tts.generate(txt, sid=0, speed=speed)
        x = np.array(a.samples, dtype=np.float64)
        x /= max(1e-9, np.abs(x).max())
        raw, proc = os.path.join(VO, f"r{i}.wav"), os.path.join(VO, f"p{i}.wav")
        wavfile.write(raw, a.sample_rate, (x*0.95*32767).astype(np.int16))
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af",CHAIN,
                        "-ar","44100","-ac","1",proc], check=True)
        d = dur_of(proc)
        if d <= slot: break
    rep.append((i, speed, round(d,2), round(slot,2)))
    sr, y = wavfile.read(proc)
    y = y.astype(np.float64)/32768.0
    if y.ndim > 1: y = y.mean(axis=1)
    fi, fo = int(0.012*SR), int(0.030*SR)
    y *= np.clip(np.arange(len(y))/fi, 0, 1)
    y *= np.clip((len(y)-np.arange(len(y)))/fo, 0, 1)
    s = int(t0*SR); n = min(len(y), N-s)
    vo[s:s+n] += y[:n]

print("line speed  dur  slot")
for r in rep: print("  %d  %.2f %5.2f %5.2f" % r)
vo *= 0.95/max(1e-9, np.abs(vo).max())

# ------------------------------------------------- music (same bed as before)
BPM = 96.0; SPB = 60.0/BPM; BAR = SPB*4
def mid(n): return 440.0*2**((n-69)/12.0)
CH = [([60,64,67],36), ([59,62,67],43), ([60,64,69],45), ([60,65,69],41),
      ([60,64,67],36), ([59,62,67],43), ([60,65,69],41), ([60,64,67],36)]
rng = np.random.default_rng(5)
def et(n): return np.arange(n)/SR
def pluck(f,d,dec=0.33):
    t=et(int(d*SR))
    w=(np.sin(2*np.pi*f*t)+0.45*np.sin(2*np.pi*2*f*t)
       +0.22*np.sin(2*np.pi*3*f*t)+0.10*np.sin(2*np.pi*4*f*t))
    return w*np.exp(-t/dec)*(1-np.exp(-t/0.004))
def padv(f,d):
    t=et(int(d*SR))
    w=(np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2*f*t+0.4)+0.25*np.sin(2*np.pi*3*f*t+1.1))
    return w*np.clip(t/0.35,0,1)*np.clip((d-t)/0.55,0,1)*(1+0.004*np.sin(2*np.pi*4.5*t))
def bassv(f,d,dec=0.42):
    t=et(int(d*SR))
    return (np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t))*np.exp(-t/dec)*(1-np.exp(-t/0.006))
def kickv(d=0.32):
    t=et(int(d*SR)); f=112*np.exp(-t/0.035)+46
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.11)
def noisy(d,dec):
    n=int(d*SR); x=rng.standard_normal(n); x=np.diff(np.concatenate([[0.0],x]))
    return x*np.exp(-et(n)/dec)
def add(buf,t0,sig,amp=1.0):
    i=int(t0*SR)
    if i>=N or amp<=0: return
    n=min(len(sig),N-i); buf[i:i+n]+=sig[:n]*amp

arp=np.zeros(N); pad=np.zeros(N); bs=np.zeros(N); dr=np.zeros(N); mel=np.zeros(N)
g_arp=[.55,.65,.75,.80,.90,.90,.95,1.0]; g_pad=[.60,.70,.80,.80,.85,.85,.90,1.0]
g_bs=[0,.85,.95,1,1,1,1,1]; g_hat=[0,0,.55,.70,.85,.85,.95,.90]
g_kick=[0,0,0,.85,1,1,1,1]; g_clap=[0,0,0,0,.70,.70,.80,.80]
MEL={4:[72,74,76,79],5:[79,76,74,71],6:[69,72,74,77],7:[76,74,72,72]}
APAT=[0,1,2,3,2,1,0,1]
for b,(tones,root) in enumerate(CH):
    t0=b*BAR
    for k,ix in enumerate(APAT):
        f=mid(tones[ix%3]+12*(ix//3)+12)
        add(arp,t0+k*SPB/2,pluck(f,0.55),0.16*g_arp[b]*(1.0 if k%2==0 else 0.72))
    for tn in tones: add(pad,t0,padv(mid(tn-12),BAR*1.02),0.065*g_pad[b])
    add(bs,t0,bassv(mid(root),BAR*0.52),0.30*g_bs[b])
    add(bs,t0+2*SPB,bassv(mid(root),BAR*0.36),0.26*g_bs[b])
    add(bs,t0+3.5*SPB,bassv(mid(root+12),BAR*0.18),0.18*g_bs[b])
    for beat in (0,2): add(dr,t0+beat*SPB,kickv(),0.52*g_kick[b])
    for beat in (1,3): add(dr,t0+beat*SPB,noisy(0.22,0.075),0.085*g_clap[b])
    for k in range(8):
        add(dr,t0+k*SPB/2,noisy(0.06,0.016),0.045*g_hat[b]*(1.0 if k%2==0 else 0.58))
    if b in MEL:
        for k,nt in enumerate(MEL[b]): add(mel,t0+k*SPB,pluck(mid(nt),0.75,0.42),0.13*g_arp[b])

t=et(int(0.9*SR)); imp=rng.standard_normal(len(t))*np.exp(-t/0.26); imp[0]=1.0
imp/=np.abs(imp).max()
wide=arp+pad+mel
wet=fftconvolve(wide,imp)[:N]
wet/=max(1e-9,np.abs(wet).max()/max(1e-9,np.abs(wide).max()))
wide=wide*0.80+wet*0.20
dly=int(0.009*SR)
L=wide.copy(); R=np.concatenate([np.zeros(dly),wide[:-dly]])*0.96
center=bs+dr; L+=center; R+=center
music=np.stack([L,R],axis=1)
music*=0.57/max(1e-9,np.abs(music).max())
music[:int(0.25*SR)]*=np.linspace(0,1,int(0.25*SR))[:,None]
music[-int(0.9*SR):]*=np.linspace(1,0,int(0.9*SR))[:,None]

# ------------------------------------------------- duck + mix
win=int(0.05*SR)
rms=np.sqrt(np.convolve(vo**2,np.ones(win)/win,mode="same")); rms/=max(1e-9,rms.max())
env=np.zeros(N); a_at=np.exp(-1/(0.030*SR)); a_rl=np.exp(-1/(0.320*SR)); p=0.0
for i in range(N):
    x=rms[i]; p=x+(p-x)*(a_at if x>p else a_rl); env[i]=p
duck=1.0-0.50*np.clip(env*1.6,0,1)
mix=music*duck[:,None]+np.stack([vo,vo],axis=1)*0.92
mix=np.tanh(mix*1.05); mix*=0.89/max(1e-9,np.abs(mix).max())
wavfile.write(os.path.join(BUILD, "mix.wav"), SR, (mix*32767).astype(np.int16))
wavfile.write(os.path.join(BUILD, "music.wav"), SR, (music*32767).astype(np.int16))
print("build/mix.wav written")
