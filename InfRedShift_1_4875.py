import pint.models
import pint.toa
import matplotlib.pyplot as plt
import numpy as np
import io
import glob
from scipy import stats
from pint.residuals import Residuals

# 1. THE MAP: Preparing the Indian uGMRT Map
with open("J1909-3744.DMX.par", "r") as f:
    lines = f.readlines()
basics = ["PSR", "RAJ", "DECJ", "F0", "F1", "PEPOCH", "POSEPOCH", "DM", "EPHEM"]
clean_par = ["UNITS TDB\n"]
for line in lines:
    if any(line.startswith(word) for word in basics):
        clean_par.append(line)
m = pint.models.get_model(io.StringIO("".join(clean_par)))

# 2. THE HEARTBEAT: Loading the Cleaned Indian uGMRT signals
all_toas = []
for tim_file in glob.glob("GM_GWB*.tim"):
    with open(tim_file, 'r') as f:
        lines = f.readlines()
    cleaned_tim = []
    for line in lines:
        if line.startswith("FORMAT") or line.startswith("MODE"):
            cleaned_tim.append(line)
        else:
            parts = line.split()
            if len(parts) >= 5:
                cleaned_tim.append(" ".join(parts[:5]) + "\n")
    try:
        all_toas.append(pint.toa.get_TOAs(io.StringIO("".join(cleaned_tim))))
    except:
        continue
t = pint.toa.merge_TOAs(all_toas)

# 3. ANALYSIS: Calculating Jitter and the Signature Slope
res_obj = Residuals(t, m)
jitter = np.array(res_obj.time_resids.to_value('s'), dtype=float)
psd = np.abs(np.fft.fft(jitter))**2
freqs = np.fft.fftfreq(len(jitter))
idx = np.argsort(freqs)
mask = (freqs[idx] > 0)
f_clean, p_clean = freqs[idx][mask], psd[idx][mask]

# 4. THE FINAL MATH: Finding the Slope and the "+/- X" Error
log_f = np.log10(f_clean.astype(float))
log_p = np.log10(p_clean.astype(float))
slope, intercept, r_v, p_v, std_err = stats.linregress(log_f, log_p)

# 5. THE PROOF GRAPH & PDF EXPORT
plt.figure(figsize=(10, 7))
plt.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['font.family'] = "sans-serif"

plt.loglog(f_clean, p_clean, color='darkorange', linewidth=1.2, alpha=0.8, label='InPTA Power Spectrum')

# Clean Labels for Nature Submission
plt.xlabel("Frequency (Hz)", fontsize=13)
plt.ylabel("Power Spectral Density", fontsize=13)
plt.grid(True, which="both", ls="-", alpha=0.15)

# --- THE SIGNATURE BLOCK (LEFT SIDE) ---
signature_val = abs(slope)
# Using LaTeX for professional math symbols in the plot
signature_text = (r"$\alpha$ (Spectral Index) = " + f"{signature_val:.4f}\n"
                  r"$\sigma$ (Uncertainty)   = " + f"{std_err:.4f}")

plt.text(0.05, 0.05, signature_text,
         transform=plt.gca().transAxes,
         fontsize=11,
         color='black',
         family='monospace',
         verticalalignment='bottom',
         horizontalalignment='left',
         bbox=dict(facecolor='white', alpha=0.85, edgecolor='darkorange', boxstyle='round,pad=0.5'))

# Final Save and Show
pdf_filename = "Figure_2_InPTA_Spectral_Analysis.pdf"
plt.savefig(pdf_filename, format='pdf', dpi=300, bbox_inches='tight')
plt.show()

print(f"\n>>> SUBMISSION READY FIGURE: {pdf_filename} generated successfully <<<")
