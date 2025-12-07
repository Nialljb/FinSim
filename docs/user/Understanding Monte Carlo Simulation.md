# Understanding Monte Carlo Simulation for Financial Planning

## What is Monte Carlo Simulation?

Monte Carlo simulation is a computational technique that uses random sampling to model uncertainty and predict a range of possible outcomes. Named after the famous Monte Carlo casino in Monaco, it acknowledges that financial planning involves probability and chance—just like casino games.

## Why Use Monte Carlo for Financial Planning?

### The Problem with Traditional Planning

Traditional financial planning often uses a single "expected return" (e.g., "assume 7% per year"). This gives you one trajectory:

```
Year 0: $100,000
Year 1: $107,000
Year 2: $114,490
...
Year 30: $761,226
```

**The problem:** This never happens in real life! Some years returns are +20%, others are -15%. The order matters too—losing money early is worse than losing money late.

### The Monte Carlo Solution

Instead of one path, Monte Carlo runs **thousands of simulations**, each with different random returns:

```
Simulation 1: +12%, -5%, +18%, +3%, -8%, ...
Simulation 2: -3%, +22%, +7%, -12%, +15%, ...
Simulation 3: +8%, +9%, -2%, +11%, +4%, ...
...
Simulation 1000: +5%, -7%, +19%, +2%, +13%, ...
```

This creates a **distribution of outcomes** that shows you:
- Best case scenario (90th percentile)
- Worst case scenario (10th percentile)  
- Most likely outcome (50th percentile/median)
- Probability of success for your goals

## How It Works: Step-by-Step

### Step 1: Define Your Starting Point
```
Initial wealth: $100,000
Annual income: $80,000
Annual expenses: $50,000
Annual savings: $30,000
```

### Step 2: Set Your Assumptions
```
Expected investment return: 7% per year
Return volatility (standard deviation): 15%
Expected inflation: 2.5% per year
Inflation volatility: 1%
```

### Step 3: Generate Random Returns

For each simulation, we randomly generate returns based on your assumptions. If you expect 7% with 15% volatility:

- 68% of years: returns between -8% and +22% (7% ± 15%)
- 95% of years: returns between -23% and +37% (7% ± 2×15%)
- Occasionally: extreme events outside this range

This follows a **log-normal distribution**—the same pattern seen in actual market returns.

### Step 4: Simulate Year by Year

For each of 1,000 simulations, we calculate every year:

```python
# Year 1 - Simulation #1
random_return_1 = 12.3%  # Randomly generated
inflation_1 = 2.7%       # Randomly generated

# Your wealth grows
wealth = $100,000 * (1 + 0.123) = $112,300

# Add savings (adjusted for inflation)
savings = $30,000 * (1 + 0.027) = $30,810
wealth = $112,300 + $30,810 = $143,110

# Year 2 - Simulation #1
random_return_2 = -5.2%  # Different random return
wealth = $143,110 * (1 - 0.052) = $135,668
... continue for 30 years
```

### Step 5: Repeat 1,000 Times

Each simulation uses different random returns, giving you 1,000 possible 30-year trajectories.

### Step 6: Analyze the Distribution

After running all simulations, we can answer questions like:

- **"What's my most likely net worth in 30 years?"**  
  Answer: The median (50th percentile) value

- **"What if things go poorly?"**  
  Answer: The 10th percentile shows outcomes worse than 90% of scenarios

- **"What's my chance of having over $2 million?"**  
  Answer: Count how many simulations exceed $2M, divide by 1,000

## Visual Example

Here's how 100 simulations might look:

```
$4M |                                            ╱─── 90th percentile
    |                                        ╱───
$3M |                                    ╱───
    |                                ╱───
$2M |                            ╱───────────── 50th percentile (median)
    |                        ╱───
$1M |                    ╱───
    |                ╱───────────────────────── 10th percentile
$0  |────────────────────────────────────────>
    0   5   10  15  20  25  30 years
```

The **spread** shows uncertainty. Wider spread = more uncertainty.

## Key Concepts

### 1. Percentiles Explained

- **10th percentile**: Only 10% of outcomes are worse (1 in 10 chance)
- **50th percentile (median)**: Half of outcomes are better, half worse (most likely)
- **90th percentile**: Only 10% of outcomes are better (optimistic scenario)

### 2. Why Returns Are Random

Markets are inherently unpredictable in the short term. While long-term averages are around 7-10%, any given year could be:
- 2008: -37% (financial crisis)
- 2013: +32% (bull market)
- 2018: -4% (market correction)
- 2019: +31% (recovery)

Monte Carlo captures this **volatility**.

### 3. Sequence of Returns Risk

The **order** of returns matters:

**Scenario A: Good returns early**
```
Year 1-5: +15%, +12%, +8%, +10%, +20%  (Average: 13%)
Year 6-10: -5%, +2%, +4%, -3%, +7%     (Average: 1%)
```

**Scenario B: Bad returns early**
```
Year 1-5: -5%, +2%, +4%, -3%, +7%      (Average: 1%)
Year 6-10: +15%, +12%, +8%, +10%, +20% (Average: 13%)
```

Even though the **average is the same**, Scenario A ends with significantly more wealth because:
- Early gains compound for longer
- You're adding savings when prices are lower in Scenario B

Monte Carlo naturally captures this by simulating different sequences.

## What This Tool Adds

Beyond basic Monte Carlo, this simulator includes:

### 1. Inflation Modeling
Not just investment returns—expenses and income grow with inflation too.

```
Year 1 expenses: $50,000
Year 10 expenses: $50,000 × (1.025)^10 = $64,004
```

### 2. Life Events
Real life isn't smooth! The simulator handles:
- Buying/selling properties
- Job changes (salary adjustments)
- Kids (expense increases)
- Rental income
- One-time expenses

### 3. Component Tracking
Your net worth isn't just one number:
- **Liquid wealth**: Accessible cash and investments
- **Property equity**: Home value minus mortgage
- **Pension**: Retirement accounts

Each grows differently and has different risk profiles.

### 4. Cash Flow Analysis
The most important question: **"Can I afford my plan?"**

The tool checks every year if your cash flow goes negative:
```
Income - Taxes - Pension - Expenses - Mortgage = Available Savings

If negative → Warning! You're depleting savings
```

## Limitations to Understand

Monte Carlo is powerful but not perfect:

### 1. Garbage In, Garbage Out
If your assumptions are wrong (e.g., expecting 12% returns), results will be misleading.

### 2. No Black Swans
Monte Carlo assumes returns follow normal patterns. It doesn't predict:
- Global pandemics
- Major policy changes
- Personal crises (job loss, health issues)

### 3. Correlations
In reality, when stocks crash, real estate often follows. Basic Monte Carlo treats them independently.

### 4. Simplifications
- No detailed tax modeling
- No healthcare costs
- No unexpected windfalls/disasters
- Constant property appreciation

## How to Use Results

### ❌ Don't Say:
"Monte Carlo says I'll have exactly $2.5M in 30 years"

### ✅ Do Say:
"Monte Carlo shows:
- 50% chance I'll have at least $2.5M
- 10% chance I'll have less than $1.8M
- 10% chance I'll have more than $3.4M

Therefore, I'm comfortable with this risk level."

## Practical Tips

### 1. Focus on Medians, Not Averages
The **median** (50th percentile) is more meaningful than the mean because extreme outliers skew averages.

### 2. Plan for the 25th Percentile
If your plan only works in the median or better scenario, you have a 50% chance of failure. Aim for success even in the 25th percentile.

### 3. Stress Test Your Plan
- What if returns are 2% lower?
- What if inflation is 1% higher?
- What if expenses increase unexpectedly?

### 4. Update Regularly
As you progress, update your starting wealth and re-run. The first 10 years matter most—uncertainty compounds.

## Example Interpretation

Let's say you run 1,000 simulations for retirement planning:

**Results at Year 30:**
```
10th percentile: $1.2M
25th percentile: $1.8M
50th percentile: $2.5M
75th percentile: $3.4M
90th percentile: $4.5M
```

**Your goal:** $2M for comfortable retirement

**Interpretation:**
- ✅ **75% probability of success** (25th percentile > $1.8M, median > $2.5M)
- 🟡 **25% chance of falling short** (10th-25th percentile below goal)
- ✅ **Median case exceeds goal by 25%** (cushion for unexpected costs)

**Decision:** This is a reasonably robust plan. Consider:
- Increasing savings slightly to reduce downside risk
- Having a Plan B if you're in the lower 25% at Year 15
- Adjusting spending if early returns are poor

## Further Reading

### Books
- *A Random Walk Down Wall Street* by Burton Malkiel
- *The Intelligent Asset Allocator* by William Bernstein

### Academic Papers
- Bengen, William (1994). "Determining Withdrawal Rates Using Historical Data"
- Pfau, Wade (2011). "Can We Predict the Sustainable Withdrawal Rate for New Retirees?"

---

## Summary

Monte Carlo simulation is a powerful tool that:
- ✅ Shows a **range of outcomes**, not just one path
- ✅ Captures **real-world volatility and uncertainty**
- ✅ Helps you **understand and plan for risk**
- ✅ Answers "what if" questions about your financial future

But remember:
- ⚠️ It's a **planning tool**, not a crystal ball
- ⚠️ Results depend heavily on your **assumptions**
- ⚠️ Update regularly as **life changes**
- ⚠️ Always **consult a financial advisor** for major decisions

**The goal isn't to predict the future—it's to prepare for multiple possible futures.**