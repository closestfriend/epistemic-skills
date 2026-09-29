---
name: signal-timeseries
description: Numerical analysis of time series and signals with numpy/scipy — periodicity detection (FFT, Lomb-Scargle), filtering and detrending, peak finding, resampling, and unit/axis discipline. Use for tasks involving periodic signals, sensor or waveform data, seasonal/trend decomposition, or frequency analysis. Not for tabular business aggregation (see tabular-data).
---

# signal-timeseries

Signal answers are usually wrong for one of three reasons: wrong sampling
assumptions, wrong units (Hz vs rad/s, period vs frequency), or an unverified
peak. Pin all three.

## Applicability & fallback

- Tools: numpy + scipy (`scipy.signal`, `scipy.fft`). Domain libraries
  (astropy, obspy) are better when present — but check the task's environment
  before importing; everything below needs only numpy/scipy.
- Unevenly sampled data: FFT assumptions break — use Lomb-Scargle
  (`scipy.signal.lombscargle`, or `astropy.timeseries.LombScargle` if
  available) instead of interpolating unless the task says to.

## Sampling discipline (do this first)

```python
t = np.asarray(times, float)
dt = np.diff(t)
print(len(t), dt.min(), dt.median() if hasattr(dt,'median') else np.median(dt), dt.max())
fs = 1.0 / np.median(dt)          # sampling rate; verify dt is ~constant
```

- If `dt` varies more than ~1%, the series is unevenly sampled — see fallback.
- Nyquist: you cannot detect frequencies above `fs/2`; if the target period
  is near `2*dt`, say so rather than reporting an alias.
- Know your time unit (s, days, years) and carry it through — a period in
  "samples" is not an answer.

## Periodicity (FFT path)

```python
from scipy.fft import rfft, rfftfreq
x = x - np.mean(x)                          # remove DC or bin 0 dominates
X = np.abs(rfft(x * np.hanning(len(x))))    # window against leakage
f = rfftfreq(len(x), d=1/fs)
peak = f[np.argmax(X[1:]) + 1]              # skip the zero bin
period = 1.0 / peak
```

- Detrend first when a slow drift exists (`scipy.signal.detrend`, or subtract
  a fitted low-order polynomial) — trends masquerade as low-frequency power.
- Frequency resolution is `fs/len(x)`; refine a peak by zero-padding or by
  quadratic interpolation around the maximum when the task wants precision.
- Report in the units the task asks for: frequency (Hz, 1/day) vs period
  (s, days) vs angular frequency (rad/s) differ by exactly the factors
  people forget (`2π`, reciprocal).

## Filtering & peaks

```python
from scipy.signal import butter, filtfilt, find_peaks
b, a = butter(4, [f_lo, f_hi], btype="band", fs=fs)   # pass fs, not normalized
y = filtfilt(b, a, x)                                  # zero-phase: no time shift
peaks, props = find_peaks(y, height=h, distance=int(min_sep * fs),
                          prominence=p)
```

- `filtfilt` (not `lfilter`) when timing of events matters — one-pass
  filtering shifts peaks.
- `find_peaks` without `prominence`/`distance` returns noise; set them from
  the task's physical definitions (minimum separation, amplitude threshold).
- Convert peak indices back to times (`t[peaks]`) before reporting.

## Verify before finishing

1. Reconstruct: does the detected period fold the data into an aligned cycle
   (plot-free check: standard deviation of phase-folded bins drops)?
2. Cross-check the headline number by a second method when cheap (FFT peak
   vs autocorrelation maximum vs Lomb-Scargle) — agreement within resolution.
3. Confirm output units/precision match the task exactly, and that reported
   times are in the task's time base (absolute vs relative).
