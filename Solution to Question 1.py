"""Q1: Are the Mega Millions numbers evenly distributed? (chi-square goodness-of-fit)"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

CSV_PATH = "Lottery_Mega_Millions_Winning_Numbers.csv"

# Load up and Clean
df = pd.read_csv(CSV_PATH)
df["Draw Date"] = pd.to_datetime(df["Draw Date"])
# only where the main numbers were 1-70 and Mega Ball was 1-25
df = df[(df["Draw Date"] >= "2017-10-28") & (df["Draw Date"] <= "2025-04-07")]
df = df.sort_values("Draw Date").reset_index(drop=True)

# "Winning Numbers" is one string like "05 12 33 41 70" -> turn into 5 separate ints
main = df["Winning Numbers"].str.split().apply(lambda x: [int(n) for n in x])
main = np.array(main.tolist())            
mega = df["Mega Ball"].astype(int).to_numpy()
n_draws = len(df)

print(f"Draws used: {n_draws}  ({df['Draw Date'].min().date()} to {df['Draw Date'].max().date()})")
print(f"Main number range: {main.min()}-{main.max()}   Mega Ball range: {mega.min()}-{mega.max()}")

#Count how often each number showed up
main_counts = np.bincount(main.ravel(), minlength=71)[1:71]   # numbers 1..70
mega_counts = np.bincount(mega, minlength=26)[1:26]           # numbers 1..25

main_expected = n_draws * 5 / 70    # 5 balls per draw, 70 equally likely numbers
mega_expected = n_draws / 25

#Chi-square test
chi_main, p_main = stats.chisquare(main_counts)
chi_mega, p_mega = stats.chisquare(mega_counts)

print("\nMain numbers (1-70)")
print(f"Expected count per number: {main_expected:.2f}")
print(f"Observed min/max: {main_counts.min()} (#{main_counts.argmin()+1}) / {main_counts.max()} (#{main_counts.argmax()+1})")
print(f"Chi-square = {chi_main:.2f}, df = 69, p-value = {p_main:.4f}")
print("Result:", "no evidence of bias (p > 0.05)" if p_main > 0.05 else "evidence of bias (p <= 0.05)")

print("\nMega Ball (1-25)")
print(f"Expected count per number: {mega_expected:.2f}")
print(f"Observed min/max: {mega_counts.min()} (#{mega_counts.argmin()+1}) / {mega_counts.max()} (#{mega_counts.argmax()+1})")
print(f"Chi-square = {chi_mega:.2f}, df = 24, p-value = {p_mega:.4f}")
print("Result:", "no evidence of bias (p > 0.05)" if p_mega > 0.05 else "evidence of bias (p <= 0.05)")

#Plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))

ax1.bar(range(1, 71), main_counts, color="tab:blue")
ax1.axhline(main_expected, color="red", linestyle="--", label=f"Expected ({main_expected:.1f})")
ax1.set_title(f"Main Number Frequency (p = {p_main:.3f})")
ax1.set_xlabel("Main number (1-70)")
ax1.set_ylabel("Times drawn (count)")
ax1.legend()

ax2.bar(range(1, 26), mega_counts, color="tab:blue")
ax2.axhline(mega_expected, color="red", linestyle="--", label=f"Expected ({mega_expected:.1f})")
ax2.set_title(f"Mega Ball Frequency (p = {p_mega:.3f})")
ax2.set_xlabel("Mega Ball (1-25)")
ax2.set_ylabel("Times drawn (count)")
ax2.legend()

fig.suptitle("Mega Millions: Draw Frequency vs. Uniform Expectation")
plt.tight_layout()
plt.savefig("q1_frequency.png", dpi=200)
plt.show()