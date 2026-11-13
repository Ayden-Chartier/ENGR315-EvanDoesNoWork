# Is Mega Millions Actually Random?

ENGR 315 Computational Methods, JMU

**Team:** Odd Bunch
**Contributors:** Ayden Chartier, Evan Riney

## Objective and Motivation

People think the lottery has hot numbers, cold numbers, or some kind of pattern. We wanted to see if that's actually true.

**Dataset:** [Lottery Mega Millions Winning Numbers: Beginning 2002](https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002) from the State of New York (data.ny.gov). It's a CSV with roughly 2,500 drawings and has four columns: draw date, the five winning numbers, the Mega Ball, and a multiplier. The game rules changed over the years, so we only use **Oct 2017 to Apr 2025** (main numbers 1-70, Mega Ball 1-25), which is about 770 drawings.

**Our three questions:**

1. **Are the numbers evenly distributed?** We expect no number to come up more than chance allows (p > 0.05).
2. **Does the total of the five numbers look like a bell curve?** Theory says the mean should be 177.5 and the standard deviation about 43.9.
3. **Is there a hidden cycle in the draws?** We expect a flat, noisy spectrum with no real peaks.

If the lottery is fair we expect to find nothing. That's still a useful result, because it shows that our tests worked.

## Details

**Prep:** load the CSV with pandas, split the winning numbers into five columns, add a column for the total, and filter to the Oct 2017 to Apr 2025 timeframe.

| Question | Method | Metrics | Tools | Plots |
|---|---|---|---|---|
| 1. Even distribution? | Chi-square goodness-of-fit test, checked with a simulation of fair draws | Counts per number, chi-square, p-value | numpy, scipy.stats | Bar chart of counts vs. expected |
| 2. Bell curve? | Fit a normal curve to the histogram of totals | Mean, standard deviation, R², Shapiro-Wilk p-value | scipy.stats, scipy.optimize.curve_fit | Histogram with fitted curve, Q-Q plot |
| 3. Hidden cycle? | FFT of the totals in date order. | Power spectrum, tallest peak vs. shuffled data, autocorrelation | numpy.fft, scipy.signal, statsmodels | Power spectrum, autocorrelation plot |

**Packages:** numpy, pandas, scipy, statsmodels, matplotlib.

**Code:** Q1 is in `Solution to Question 1.py`. Q2 and Q3 are still to come.

## Results

### Question 1: Are the numbers evenly distributed?

We counted how many times each main number (1-70) and each Mega Ball (1-25) was drawn in the 776 drawings from Oct 2017 to Apr 2025, then ran a chi-square goodness-of-fit test against a perfectly uniform draw. Since numbers can't repeat within a draw, we also simulated a bunch of fair draws to see what chi-square values pure luck gives, and checked where ours landed.

**Command-line output:**

draws in era: 776
Q1 main numbers: chi2=63.6 (df=69), p=0.661
Q1 mega ball:    chi2=22.9 (df=24), p=0.525
Q1 most extreme main numbers: [ 3 10 31] z = [2.23 2.09 1.96]
Q1 simulated p-value (main numbers): 0.525

**Figure:**

![Q1 results](figures/q1_frequency.png)

*Figure 1. Number of times each main number (1-70) and each Mega Ball (1-25) was drawn, Oct 2017 to Apr 2025. The red dashed line is the expected count for a perfectly uniform draw. The p-values come from a chi square goodness of fit test.*

### Question 2: Bell curve?

*Coming in the next phase.*

### Question 3: Hidden cycle?

*Coming in the next phase.*

## Conclusions

### Question 1: Are the numbers evenly distributed?

For the main numbers, the chi square test gave χ² = 63.6 (df = 69) and p = 0.661. For the Mega Ball it gave χ² = 22.9 (df = 24) and p = 0.525. Both are above 0.05, so we found no evidence that any number is drawn more or less than chance would predict. The simulation agrees (p = 0.525): our chi square sits right in the middle of what fair draws produce. Some numbers did show up more than others. Main number 3 was drawn the most, and 3, 10, and 31 had z-scores around 2. But with 70 numbers, a few landing around 2 is normal. So the data doesn't back up the idea of "hot" and "cold" numbers, the differences jus look like random variation.


## Actions That Need to Be Completed

- [x] Pick dataset and write proposal
- [x] Rough plots
- [x] Create GitHub repo and add both of us
- [x] Clean the data
- [x] Run Q1
- [ ] Run Q2 and Q3
- [ ] Save final figures
- [ ] Write results and conclusions for Q2 and Q3
- [ ] Report and presentation

## References

[1] State of New York, "Lottery Mega Millions Winning Numbers: Beginning 2002," data.ny.gov. [Online]. Available: https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002.