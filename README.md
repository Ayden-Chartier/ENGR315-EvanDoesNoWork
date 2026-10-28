# Is Mega Millions Actually Random?

ENGR 315 Computational Methods, JMU

**Team:** Odd Bunch
**Contributors:** Ayden Chartier, Evan Riney

## Objective and Motivation

People think the lottery has hot numbers, cold numbers, or some kind of pattern. We wanted to see if that's actually true.

**Dataset:** [Lottery Mega Millions Winning Numbers: Beginning 2002](https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002) from the State of New York (data.ny.gov). It's a CSV with about 2,500 drawings and four columns: draw date, the five winning numbers, the Mega Ball, and a multiplier. The game rules changed over the years, so we only use **Oct 2017 to Apr 2025** (main numbers 1-70, Mega Ball 1-25), about 770 drawings.

**Our three questions:**

1. **Are the numbers evenly distributed?** We expect no number to come up more than chance allows (p > 0.05).
2. **Does the total of the five numbers look like a bell curve?** Theory says the mean should be 177.5 and the standard deviation about 43.9.
3. **Is there a hidden cycle in the draws?** We expect a flat, noisy spectrum with no real peaks.

If the lottery is fair we expect to find nothing. That's still a useful result, because it shows our tests work.

## Implementation Details

**Prep (all questions):** load the CSV with pandas, split the winning numbers into five columns, add a column for the total, and filter to the Oct 2017 to Apr 2025 era.

| Question | Method | Metrics | Tools | Plots |
|---|---|---|---|---|
| 1. Even distribution? | Chi-square goodness-of-fit test, checked with a simulation of fair draws | Counts per number, chi-square, p-value | numpy, scipy.stats | Bar chart of counts vs. expected |
| 2. Bell curve? | Fit a normal curve to the histogram of totals | Mean, standard deviation, R², Shapiro-Wilk p-value | scipy.stats, scipy.optimize.curve_fit | Histogram with fitted curve, Q-Q plot |
| 3. Hidden cycle? | FFT of the totals in date order, plus autocorrelation | Power spectrum, tallest peak vs. shuffled data, autocorrelation | numpy.fft, scipy.signal, statsmodels | Power spectrum, autocorrelation plot |

**Packages:** numpy, pandas, scipy, statsmodels, matplotlib. Code is in `analysis.py`.

**Rough plots from the proposal:**

![Figure 1](figures/fig1_frequency.png)
![Figure 2](figures/fig2_sum.png)
![Figure 3](figures/fig3_spectrum.png)

---

## Results

*Coming after we run the analysis.*

## Conclusions

*Coming later.*

---

## Actions That Need to Be Completed

- [x] Pick dataset and write proposal
- [x] Rough plots
- [ ] Create GitHub repo and add both of us
- [ ] Clean the data
- [ ] Run Q1, Q2, and Q3
- [ ] Save final figures
- [ ] Write results and conclusions
- [ ] Report and presentation

**Issues:** numbers in a draw can't repeat, which slightly breaks the chi-square assumptions, so we check it with a simulation. Spectrum peaks can show up by chance, so we compare the tallest one to shuffled data.

---

## References

[1] State of New York, "Lottery Mega Millions Winning Numbers: Beginning 2002," data.ny.gov. [Online]. Available: https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002. Accessed: Oct. 2026.

[2] USA Mega, "Mega Millions Statistics" (game versions and number ranges). [Online]. Available: https://www.usamega.com/mega-millions/statistics/7/3/1. Accessed: Oct. 2026.

[3] P. Virtanen et al., "SciPy 1.0: Fundamental algorithms for scientific computing in Python," *Nature Methods*, vol. 17, pp. 261-272, 2020.
