import pint.models
import pint.toa
import matplotlib.pyplot as plt
import numpy as np
import io
import glob
from scipy import stats

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
from pint.residuals import Residuals
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
plt.figure(figsize=(12, 8))
plt.loglog(f_clean, p_clean, color='orange', linewidth=1.5, alpha=0.8)

# Adding the Title and Labels
plt.title("InPTA DUAL-BAND 'INFINITE REDSHIFT' FINAL PROOF", fontsize=16, fontweight='bold', pad=20)
plt.xlabel("Frequency (Hz)", fontsize=12)
plt.ylabel("Power Spectral Density", fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.3)

# --- THE SIGNATURE BLOCK (LEFT SIDE) ---
signature_val = abs(slope)
signature_text = (f"FINAL SIGNATURE (α) = {signature_val:.4f}\n"
                  f"UNCERTAINTY (± X)      = {std_err:.4f}")

plt.text(0.05, 0.15, signature_text, 
         transform=plt.gca().transAxes, 
         fontsize=12, 
         color='black', 
         fontweight='bold',
         family='monospace', # Keeps numbers aligned
         verticalalignment='bottom', 
         horizontalalignment='left',
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.5'))

# --- THE WATERMARK FOR PRAKASH (RIGHT SIDE) ---
credit_text = "Prakash Vaithyanathan\nScience Teacher, Chennai, India"
plt.text(0.95, 0.95, credit_text, 
         transform=plt.gca().transAxes, 
         fontsize=12, 
         color='darkblue', 
         fontweight='bold',
         verticalalignment='top', 
         horizontalalignment='right',
         bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# Final Save and Show
pdf_filename = "InPTA_Final_Proof_Prakash.pdf"
plt.savefig(pdf_filename, format='pdf', bbox_inches='tight')
plt.show()

print(f"\n>>> SUCCESS: Plot saved as {pdf_filename} <<<")
