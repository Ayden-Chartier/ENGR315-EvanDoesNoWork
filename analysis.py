import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, signal
from scipy.optimize import curve_fit
from statsmodels.tsa.stattools import acf
from statsmodels.stats.diagnostic import acorr_ljungbox

rng = np.random.default_rng(315)  # fixed seed so results repeat
URL = "https://data.ny.gov/api/v3/views/5xaw-6ayf/export.csv?accessType=DOWNLOAD"
MAIN = ["n1", "n2", "n3", "n4", "n5"]


# Step 1: load and clean
def load_era(src=URL, start="2017-10-31", end="2025-04-04"):
    df = pd.read_csv(src)
    df["Draw Date"] = pd.to_datetime(df["Draw Date"])
    df = df.sort_values("Draw Date").reset_index(drop=True)
    balls = df["Winning Numbers"].str.split(expand=True).astype(int)
    balls.columns = MAIN
    df = pd.concat([df, balls], axis=1)
    df["Mega Ball"] = df["Mega Ball"].astype(int)
    df["total"] = balls.sum(axis=1)
    era = df[(df["Draw Date"] >= start) & (df["Draw Date"] <= end)].reset_index(drop=True)
   
    assert era[MAIN].to_numpy().min() >= 1 and era[MAIN].to_numpy().max() <= 70
    assert era["Mega Ball"].between(1, 25).all()
    assert era["Draw Date"].is_unique
    return era


# Q1: uniformity
def q1_uniformity(era, n_sims=2000):
    N = len(era)
    main_counts = np.bincount(era[MAIN].to_numpy().ravel(), minlength=71)[1:]
    mb_counts = np.bincount(era["Mega Ball"], minlength=26)[1:]

    chi_main, p_main = stats.chisquare(main_counts)  # equal expected counts by default
    chi_mb, p_mb = stats.chisquare(mb_counts)
    print(f"Q1 main numbers: chi2={chi_main:.1f} (df=69), p={p_main:.3f}")
    print(f"Q1 mega ball:    chi2={chi_mb:.1f} (df=24), p={p_mb:.3f}")

    # which numbers are furthest from expected?
    exp_main = 5 * N / 70
    z = (main_counts - exp_main) / np.sqrt(exp_main)
    worst = np.argsort(-np.abs(z))[:3] + 1
    print("Q1 most extreme main numbers:", worst, "z =", np.round(z[worst - 1], 2))

    # simulate fair draws (no repeats inside a draw) and see how big chi2 gets by luck
    sim = np.empty(n_sims)
    for i in range(n_sims):
        draws = rng.random((N, 70)).argsort(axis=1)[:, :5]  # 5 distinct numbers per row
        c = np.bincount(draws.ravel(), minlength=70)
        sim[i] = ((c - exp_main) ** 2 / exp_main).sum()
    p_sim = (1 + (sim >= chi_main).sum()) / (1 + n_sims)
    print(f"Q1 simulated p-value (main numbers): {p_sim:.3f}")

    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].bar(range(1, 71), main_counts)
    ax[0].axhline(exp_main, color="red", ls="--", label="expected")
    ax[0].set(title="Main number frequency", xlabel="Number", ylabel="Times drawn")
    ax[0].legend()
    ax[1].bar(range(1, 26), mb_counts)
    ax[1].axhline(N / 25, color="red", ls="--", label="expected")
    ax[1].set(title="Mega Ball frequency", xlabel="Mega Ball", ylabel="Times drawn")
    ax[1].legend()
    ax[2].hist(sim, bins=30)
    ax[2].axvline(chi_main, color="red", label="observed")
    ax[2].set(title="Chi-square from simulated fair draws",
              xlabel="Chi-square statistic", ylabel="Count")
    ax[2].legend()
    fig.tight_layout()


# Q2: distribution of the total
def q2_sum_distribution(era):
    s = era["total"].to_numpy(dtype=float)
    mu_th = 5 * 35.5
    sd_th = np.sqrt(5 * (70**2 - 1) / 12 * (70 - 5) / (70 - 1))
    print(f"Q2 data: mean={s.mean():.1f}, sd={s.std(ddof=1):.1f} | theory: {mu_th}, {sd_th:.1f}")
    print(f"Q2 skew={stats.skew(s):.2f}, excess kurtosis={stats.kurtosis(s):.2f}")
    print("Q2 Shapiro-Wilk:", stats.shapiro(s))
    print("Q2 KS vs theory:", stats.kstest(s, "norm", args=(mu_th, sd_th)))

    # fit a Gaussian curve to the histogram
    dens, edges = np.histogram(s, bins=30, density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    gauss = lambda x, mu, sd: stats.norm.pdf(x, mu, sd)
    popt, pcov = curve_fit(gauss, centers, dens, p0=[s.mean(), s.std()])
    perr = np.sqrt(np.diag(pcov))
    resid = dens - gauss(centers, *popt)
    r2 = 1 - (resid**2).sum() / ((dens - dens.mean()) ** 2).sum()
    print(f"Q2 fit: mu={popt[0]:.1f}+/-{perr[0]:.1f}, sd={popt[1]:.1f}+/-{perr[1]:.1f}, R2={r2:.3f}")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].hist(s, bins=30, density=True, alpha=0.6, label="data")
    x = np.linspace(s.min(), s.max(), 300)
    ax[0].plot(x, gauss(x, *popt), "r", label="fitted normal")
    ax[0].plot(x, gauss(x, mu_th, sd_th), "k--", label="theory")
    ax[0].set(title="Sum of the five main numbers", xlabel="Sum (dimensionless)",
              ylabel="Probability density")
    ax[0].legend()
    stats.probplot(s, dist="norm", plot=ax[1])
    ax[1].set_title("Q-Q plot of draw totals vs. normal")
    fig.tight_layout()


# Q3: hidden cycles
def q3_cycles(era, n_perm=2000, max_lag=30):
    s = era["total"].to_numpy(dtype=float)
    s = s - s.mean()  # remove the average so the FFT shows only the ups and downs
    N = len(s)

    def power(x):
        return (np.abs(np.fft.rfft(x)) ** 2 / len(x))[1:]  # drop the zero-frequency term

    freq = np.fft.rfftfreq(N, d=1)[1:]  # cycles per draw
    p = power(s)
    g_obs = p.max() / p.sum()  # Fisher's g: share of power in the tallest peak
    g_null = np.empty(n_perm)
    for i in range(n_perm):  # shuffle the order -> any real cycle is destroyed
        q = power(rng.permutation(s))
        g_null[i] = q.max() / q.sum()
    p_g = (1 + (g_null >= g_obs).sum()) / (1 + n_perm)
    print(f"Q3 tallest peak at {freq[p.argmax()]:.4f} cycles/draw "
          f"(period {1 / freq[p.argmax()]:.1f} draws), Fisher g={g_obs:.4f}, perm p={p_g:.3f}")

    r = acf(s, nlags=max_lag, fft=True)
    bound = 1.96 / np.sqrt(N)
    outside = int((np.abs(r[1:]) > bound).sum())
    print(f"Q3 autocorrelation: {outside} of {max_lag} lags outside +/-{bound:.3f} "
          f"(about {0.05 * max_lag:.1f} expected by chance)")
    print(acorr_ljungbox(s, lags=[10, 20]))

    f_w, pxx = signal.welch(s, fs=1.0, nperseg=128)

    fig, ax = plt.subplots(1, 3, figsize=(16, 4))
    ax[0].plot(freq, p)
    ax[0].set(title="Power spectrum of draw totals", xlabel="Frequency (cycles per draw)",
              ylabel="Power")
    ax[1].plot(f_w, pxx)
    ax[1].set(title="Smoothed spectrum (Welch)", xlabel="Frequency (cycles per draw)",
              ylabel="Power density")
    ax[2].stem(range(1, max_lag + 1), r[1:])
    ax[2].axhline(bound, color="red", ls="--")
    ax[2].axhline(-bound, color="red", ls="--")
    ax[2].set(title="Autocorrelation of draw totals", xlabel="Lag (draws)",
              ylabel="Autocorrelation")
    fig.tight_layout()


if __name__ == "__main__":
    era = load_era()
    print("draws in era:", len(era))
    q1_uniformity(era)
    q2_sum_distribution(era)
    q3_cycles(era)
    plt.show()
