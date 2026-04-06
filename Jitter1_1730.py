import numpy as np
from scipy import stats

# 1. LOAD THE DATA
data = np.genfromtxt("J1909-3744.DMtimeseries.txt")
mjd, dm = data[:, 0], data[:, 1]

# 2. THE COMMAND LINE "QUICK FIT"
delta_dm = np.diff(dm)
psd = np.abs(np.fft.fft(delta_dm))**2
freqs = np.fft.fftfreq(len(delta_dm))

# Focus on the signal window (0.1 to 0.4)
mask = (freqs > 0.1) & (freqs < 0.4)
log_f = np.log10(freqs[mask])
log_p = np.log10(psd[mask])

# 3. CALCULATING THE SLOPE AND THE "SOMETHING" (std_err)
slope, intercept, r, p, std_err = stats.linregress(log_f, log_p)

# The Kolmogorov Correction
storm_alpha = abs(slope)
kolmogorov_noise = 0.4551
final_alpha = storm_alpha - kolmogorov_noise

# 4. PRINTING THE FINAL RESULT FOR THE PAPER
print("\n" + "="*50)
print(f"FINAL SIGNATURE (α) = {final_alpha:.4f}")
print(f"UNCERTAINTY (± X)   = {std_err:.4f}") 
print("="*50)
print(f"FOR THE PAPER: {final_alpha:.4f} ± {std_err:.4f}")
print("="*50)
