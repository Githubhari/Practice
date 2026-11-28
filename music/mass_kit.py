"""MASS KIT - reusable synth instruments for original cinematic / Telugu-mass style BGMs.

Everything is synthesized from scratch (no samples, no copied melodies).
    from mass_kit import Mix, tanpura, bansuri, choir, brass, dhol_bass, dhol_slap, ...
"""
import numpy as np
from scipy import signal

SR = 44100
TAU = 2 * np.pi
_rng = np.random.default_rng(2026)


def note(n):
    return 440.0 * 2 ** ((np.asarray(n, dtype=float) - 69) / 12)


def tl(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return _rng.standard_normal(int(d * SR))


def lowpass(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR * 0.45) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def highpass(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bandpass(x, f0, q=4.0):
    b, a = signal.iirpeak(min(f0, SR * 0.45) / (SR / 2), q)
    return signal.lfilter(b, a, x)


def saw(freq, tt):
    """Band-limited-ish saw from a phase accumulator (freq may be an array)."""
    f = np.broadcast_to(np.asarray(freq, dtype=float), tt.shape)
    ph = np.cumsum(f) / SR
    nh = int(max(1, min(40, SR / 2 / max(float(np.max(f)), 1))))
    return sum(np.sin(TAU * h * ph) / h for h in range(1, nh + 1)) * 0.6


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    tt = np.arange(n) / SR
    dur = n / SR
    env = np.where(tt < a, tt / max(a, 1e-4), np.where(tt < a + d, 1 - (1 - s) * (tt - a) / max(d, 1e-4), s))
    rel = np.clip((dur - tt) / max(r, 1e-4), 0, 1)
    return env * rel


# ------------------------------------------------------------------ Indian colour
def tanpura(root, d, cycle=1.3):
    """Pa-Sa-Sa-Sa drone with a buzzing (jawari) shimmer."""
    out = np.zeros(int(d * SR))
    strings = [root - 5, root, root, root - 12]
    t0, k = 0.0, 0
    while t0 < d:
        n = strings[k % 4]
        L = min(int(4.0 * SR), len(out) - int(t0 * SR))
        if L <= 0:
            break
        tt = np.arange(L) / SR
        f = float(note(n))
        s = np.zeros(L)
        for h in range(1, 16):
            shimmer = 0.5 + 0.5 * np.sin(TAU * (0.3 + 0.07 * h) * tt + h)
            s += np.sin(TAU * f * h * tt) * (1 / h ** 0.8) * shimmer * np.exp(-tt * (0.6 + 0.05 * h))
        i0 = int(t0 * SR)
        out[i0:i0 + L] += s * np.minimum(1, tt / 0.01) * 0.25
        t0 += cycle
        k += 1
    return out


def bansuri(notes, glide=0.08, vib=0.012):
    """notes: list of (midi, duration). Breathy flute with meend glides between notes."""
    total = sum(d for _, d in notes)
    tt = tl(total)
    f = np.zeros(len(tt))
    env = np.zeros(len(tt))
    t0 = 0.0
    prev = None
    for n, d in notes:
        i0, i1 = int(t0 * SR), int((t0 + d) * SR)
        seg = np.arange(i1 - i0) / SR
        target = float(note(n))
        if prev is None:
            f[i0:i1] = target
        else:
            g = np.clip(seg / glide, 0, 1)
            f[i0:i1] = prev * (target / prev) ** (g * g * (3 - 2 * g))
        e = np.minimum(1, seg / 0.06) * np.clip((d - seg) / 0.12, 0.35, 1)
        env[i0:i1] = e
        prev = target
        t0 += d
    f *= 1 + vib * np.sin(TAU * 5.3 * tt) * np.minimum(1, tt / 0.5)
    ph = np.cumsum(f) / SR
    tone = np.sin(TAU * ph) + 0.2 * np.sin(TAU * 2 * ph) + 0.06 * np.sin(TAU * 3 * ph)
    breath = bandpass(noise(total), 1800, 1.5) * 0.12
    return (tone + breath) * lowpass(env, 30, 1)


# ------------------------------------------------------------------ orchestra
FORMANTS = {"ah": [(730, 1.0), (1090, 0.5), (2440, 0.25)],
            "oh": [(570, 1.0), (840, 0.45), (2410, 0.2)],
            "eh": [(530, 1.0), (1840, 0.5), (2480, 0.3)],
            "oo": [(320, 1.0), (800, 0.35), (2400, 0.12)]}


def choir(notes, d, vowel="ah", voices=3, attack=0.6):
    """Formant-filtered vocal pad (each note sung by several detuned voices)."""
    tt = tl(d)
    src = np.zeros(len(tt))
    for n in notes:
        for v in range(voices):
            det = 1 + (v - (voices - 1) / 2) * 0.006
            vib = 1 + 0.008 * np.sin(TAU * (4.8 + 0.4 * v) * tt + v)
            src += saw(float(note(n)) * det * vib, tt)
    out = sum(a * bandpass(src, f0, 6) for f0, a in FORMANTS[vowel])
    out += 0.05 * bandpass(noise(d), 3000, 1)
    env = np.minimum(1, tt / attack) * np.clip((d - tt) / 0.6, 0, 1)
    return out * env / (len(notes) * voices) * 3


def brass(n, d, bright=1.0, swell=0.03):
    """Detuned saw section with a filter envelope (dark -> bright -> settle)."""
    tt = tl(d)
    s = sum(saw(float(note(n)) * dt, tt) for dt in (1.0, 1.004, 0.996, 2.0 * 0.999))
    dark, br = lowpass(s, 500), lowpass(s, 2600 * bright)
    fenv = np.minimum(1, tt / swell) * (0.45 + 0.55 * np.exp(-tt * 3))
    return (dark + fenv * (br - dark)) * adsr(len(tt), swell, 0.2, 0.75, 0.12) * 0.5


def strings_stacc(n, d=0.14):
    tt = tl(d)
    s = sum(saw(float(note(n)) * dt, tt) for dt in (1.0, 1.006, 0.994))
    return lowpass(s, 1800) * np.exp(-tt * 14) * np.minimum(1, tt / 0.004) * 0.5


def braam(notes, d=3.0):
    tt = tl(d)
    s = sum(saw(float(note(n)) * dt, tt) for n in notes for dt in (1.0, 1.007, 0.993))
    s = lowpass(s, 900) / len(notes)
    sub = np.sin(TAU * float(note(notes[0] - 12)) * tt)
    env = np.minimum(1, tt / 0.03) * np.exp(-tt * 1.0)
    return (s + sub) * env * 0.6


# ------------------------------------------------------------------ percussion
def dhol_bass(pitch=1.0, d=0.6):
    tt = tl(d)
    f = (70 + 70 * np.exp(-tt * 18)) * pitch
    body = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 6)
    thump = lowpass(noise(d), 300) * np.exp(-tt * 40) * 2
    return np.tanh((body + thump) * 1.8)


def dhol_slap(d=0.15):
    tt = tl(d)
    crack = bandpass(noise(d), 2800, 1.2) * np.exp(-tt * 45) * 2.5
    tone = np.sin(TAU * 420 * tt) * np.exp(-tt * 30)
    return crack + 0.6 * tone


def kick(d=0.5):
    tt = tl(d)
    f = 42 + 140 * np.exp(-tt * 28)
    return np.tanh(np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 6) * 2.5)


def clap(d=0.4):
    tt = tl(d)
    n = highpass(noise(d), 900)
    env = np.exp(-tt * 14)
    for off in (0.0, 0.011, 0.022):
        env = env + 0.7 * np.exp(-np.maximum(0, tt - off) * 110) * (tt >= off)
    return n * env * 0.6 + 0.4 * np.sin(TAU * 180 * tt) * np.exp(-tt * 22)


def taiko(pitch=1.0, d=1.4):
    tt = tl(d)
    f = (52 + 110 * np.exp(-tt * 7)) * pitch
    return np.tanh((np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 3.5)
                    + 0.5 * lowpass(noise(d), 1200) * np.exp(-tt * 25)) * 1.5)


def cymbal(d=3.0):
    tt = tl(d)
    return highpass(noise(d), 5000) * np.exp(-tt * 1.4) * 0.5


def chant_hey(pitch=52, voices=5):
    """Crowd 'HEY!' shout: breathy onset + formant-filtered voices with a pitch fall."""
    d = 0.32
    tt = tl(d)
    out = np.zeros(len(tt))
    for v in range(voices):
        p = float(note(pitch + _rng.uniform(-2, 3)))
        f = p * (1.08 - 0.15 * tt / d)
        src = saw(f, tt) + 0.3 * noise(d)
        voice = sum(a * bandpass(src, f0 * _rng.uniform(0.95, 1.05), 5) for f0, a in FORMANTS["eh"])
        delay = int(_rng.uniform(0, 0.02) * SR)
        out[delay:] += voice[:len(out) - delay]
    h = bandpass(noise(d), 2500, 1) * np.exp(-tt * 40)
    env = np.minimum(1, tt / 0.015) * np.exp(-tt * 7)
    return (out / voices * 2.2 + h) * env


def sub808(n, d, glide_to=None):
    tt = tl(d)
    f0 = float(note(n))
    f = np.full(len(tt), f0)
    if glide_to is not None:
        g = np.clip((tt - d * 0.6) / (d * 0.3), 0, 1)
        f = f0 * (float(note(glide_to)) / f0) ** g
    s = np.sin(TAU * np.cumsum(f) / SR)
    return np.tanh(s * 2) * adsr(len(tt), 0.005, 0.3, 0.8, 0.05)


def riser(d, f0=200, f1=2400):
    tt = tl(d)
    ph = np.cumsum(np.linspace(f0, f1, len(tt))) / SR
    s = 0.4 * np.sin(TAU * ph) + 0.6 * highpass(noise(d), 1500)
    return s * (tt / d) ** 2.5


def heartbeat():
    out = np.zeros(int(0.7 * SR))
    for off, amp in ((0, 1.0), (0.26, 0.7)):
        tt = tl(0.35)
        f = 55 * np.exp(-tt * 3)
        seg = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 14) * amp
        i = int(off * SR)
        out[i:i + len(seg)] += seg
    return out


def bell(f=880.0, d=3.0):
    tt = tl(d)
    return sum(a * np.sin(TAU * f * m * tt) * np.exp(-tt * dc)
               for m, a, dc in ((1, 1, 1.2), (2.76, 0.45, 2), (5.4, 0.25, 3.5), (8.9, 0.1, 5)))


# ------------------------------------------------------------------ mixer
class Mix:
    """Stereo timeline with per-event gain/pan and per-bus reverb send."""

    def __init__(self, dur):
        self.n = int(dur * SR)
        self.dry = np.zeros((2, self.n))
        self.wet = np.zeros((2, self.n))

    def add(self, sig, t0, gain=1.0, pan=0.0, verb=0.25):
        i0 = int(t0 * SR)
        if i0 >= self.n:
            return
        if i0 < 0:
            sig, i0 = sig[-i0:], 0
        i1 = min(self.n, i0 + len(sig))
        s = sig[:i1 - i0] * gain
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.dry[0, i0:i1] += s * l * 1.414
        self.dry[1, i0:i1] += s * r * 1.414
        if verb > 0:
            self.wet[0, i0:i1] += s * l * verb
            self.wet[1, i0:i1] += s * r * verb

    def render(self, tail=2.2, drive=1.4, fade_out=0.8):
        out = self.dry.copy()
        for ch in range(2):
            ir_t = tl(tail)
            ir = lowpass(_rng.standard_normal(len(ir_t)), 6000) * np.exp(-ir_t * 2.8)
            ir[: int(0.012 * SR)] = 0
            L = 1 << int(np.ceil(np.log2(self.n + len(ir))))
            wet = np.fft.irfft(np.fft.rfft(self.wet[ch], L) * np.fft.rfft(ir, L), L)[: self.n]
            out[ch] += wet * 0.08
        t = np.arange(self.n) / SR
        out *= np.clip((self.n / SR - t) / fade_out, 0, 1)
        out = np.tanh(out / (np.max(np.abs(out)) + 1e-9) * drive)
        return out / (np.max(np.abs(out)) * 1.05)


# ------------------------------------------------------------------ emotional instruments (violin, cello, piano, voice, organ)
def _legato_pitch(notes, glide):
    """Build a per-sample frequency curve and note-boundary envelope for a legato phrase."""
    total = sum(d for _, d in notes)
    n = int(total * SR)
    f = np.zeros(n)
    env = np.zeros(n)
    t0, prev = 0.0, None
    for nn, d in notes:
        i0, i1 = int(t0 * SR), min(n, int((t0 + d) * SR))
        seg = np.arange(i1 - i0) / SR
        if nn is None:                       # rest
            f[i0:i1] = prev if prev else 440.0
            env[i0:i1] = 0.0
        else:
            target = float(note(nn))
            if prev is None:
                f[i0:i1] = target
            else:
                g = np.clip(seg / glide, 0, 1)
                f[i0:i1] = prev * (target / prev) ** (g * g * (3 - 2 * g))
            env[i0:i1] = 0.82 + 0.18 * np.minimum(1, seg / 0.12)      # slight re-bow at each note
            prev = target
        t0 += d
    return f, env, total


def bowed(notes, register="violin", glide=0.07, vib=0.007, attack=0.25, release=0.5):
    """Expressive bowed string phrase. notes: list of (midi or None, seconds)."""
    f, env, total = _legato_pitch(notes, glide)
    tt = np.arange(len(f)) / SR
    vib_env = np.clip((tt - 0.2) / 0.6, 0, 1)
    f = f * (1 + vib * vib_env * np.sin(TAU * 5.6 * tt + 0.3 * np.sin(TAU * 0.7 * tt)))
    src = saw(f, tt)
    if register == "violin":
        body = [(450, 1.0, 3), (1100, 0.5, 3), (2600, 0.45, 2.5), (3600, 0.3, 3)]
        lp = 6000
    else:   # cello
        body = [(200, 1.0, 2.5), (420, 0.8, 3), (900, 0.4, 3), (2000, 0.15, 2)]
        lp = 2800
    s = 0.35 * lowpass(src, lp) + sum(a * bandpass(src, f0, q) for f0, a, q in body)
    s += bandpass(noise(total), 3200 if register == "violin" else 1500, 1.5) * 0.04     # bow hair
    amp = lowpass(env, 18, 1) * np.minimum(1, tt / attack) * np.clip((total - tt) / release, 0, 1)
    return s * amp * 0.6


def tremolo_strings(notes, d, register="cello", rate=14):
    tt = tl(d)
    s = sum(bowed([(n, d)], register, attack=0.3) for n in notes)
    return s * (0.6 + 0.4 * np.abs(np.sin(TAU * rate / 2 * tt))) / len(notes)


def piano(n, d=3.0, vel=0.8):
    tt = tl(d)
    f0 = float(note(n))
    B = 0.0004
    s = np.zeros(len(tt))
    for k in range(1, 14):
        fk = k * f0 * np.sqrt(1 + B * k * k)
        if fk > SR * 0.45:
            break
        amp = (1 / k ** 1.1) * (0.6 + 0.4 * vel) ** (k / 4)
        dec = 0.7 + 0.25 * k + f0 / 900
        s += amp * (np.sin(TAU * fk * tt) + 0.5 * np.sin(TAU * fk * 1.0015 * tt)) * np.exp(-tt * dec)
    hammer = bandpass(noise(0.03), 2500, 1) * np.exp(-tl(0.03) * 120) * 0.3
    s[:len(hammer)] += hammer
    return s * vel * np.minimum(1, tt / 0.002) * 0.35


VOWELS_F = {"ah": [(850, 1.0, 6), (1220, 0.6, 7), (2810, 0.3, 8)],
            "oo": [(370, 1.0, 6), (870, 0.35, 7), (2670, 0.12, 8)],
            "mm": [(280, 1.0, 4), (1000, 0.06, 6), (2400, 0.03, 6)]}


def voice(notes, vowel="ah", glide=0.09, vib=0.014, breath=0.08, male=False):
    """Solo singing voice (female by default) - a wordless humming / aalaap line."""
    f, env, total = _legato_pitch(notes, glide)
    tt = np.arange(len(f)) / SR
    vib_env = np.clip((tt - 0.3) / 0.7, 0, 1)
    f = f * (1 + vib * vib_env * np.sin(TAU * 5.3 * tt)) * (0.5 if male else 1.0)
    ph = np.cumsum(f) / SR
    src = sum(np.sin(TAU * h * ph) / h ** 1.3 for h in range(1, 30) if h * float(np.max(f)) < SR * 0.45)
    src += breath * highpass(noise(total), 1500)
    s = sum(a * bandpass(src, f0 * (0.85 if male else 1.0), q) for f0, a, q in VOWELS_F[vowel])
    amp = lowpass(env, 14, 1) * np.minimum(1, tt / 0.15) * np.clip((total - tt) / 0.5, 0, 1)
    return s * amp * 0.9


def organ(notes, d, attack=1.5):
    tt = tl(d)
    s = np.zeros(len(tt))
    for n in notes:
        f = float(note(n))
        for ratio, a in ((0.5, 0.8), (1, 1.0), (2, 0.6), (3, 0.35), (4, 0.3), (6, 0.15)):
            for det in (1.0, 1.002):
                s += a * np.sin(TAU * f * ratio * det * tt)
    s *= 1 + 0.06 * np.sin(TAU * 6.5 * tt)
    return s * np.minimum(1, tt / attack) * np.clip((d - tt) / 0.8, 0, 1) / (len(notes) * 4)


def timpani(n=38, d=2.0, roll=0.0):
    tt = tl(d)
    f = float(note(n)) * (1 + 0.05 * np.exp(-tt * 20))
    body = sum(a * np.sin(TAU * f * m_ * tt) * np.exp(-tt * dc) for m_, a, dc in ((1, 1, 2), (1.5, 0.5, 3), (1.98, 0.3, 4)))
    hit = lowpass(noise(d), 800) * np.exp(-tt * 30)
    s = body + hit
    if roll > 0:
        s *= 1 + roll * np.abs(np.sin(TAU * 9 * tt))
    return np.tanh(s * 1.3) * 0.7


def santoor(n, d=2.0, vel=0.8):
    """Hammered-dulcimer shimmer (two detuned strings, bright, fast-decaying upper partials)."""
    tt = tl(d)
    f = float(note(n))
    s = np.zeros(len(tt))
    for k in range(1, 9):
        for det in (1.0, 1.003):
            s += (1 / k) * np.sin(TAU * f * k * det * tt) * np.exp(-tt * (1.5 + 1.2 * k))
    click = bandpass(noise(0.015), 4500, 1) * np.exp(-tl(0.015) * 300) * 0.4
    s[:len(click)] += click
    return s * vel * np.minimum(1, tt / 0.002) * 0.3


def cymbal_swell(d=2.5):
    tt = tl(d)
    return highpass(noise(d), 4000) * (tt / d) ** 2.2 * 0.6
