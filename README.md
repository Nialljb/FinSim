# Monte Carlo Wealth Simulator

An interactive Monte Carlo financial planning tool built with Streamlit that helps you visualize and analyze your financial future over a 30-year horizon.

## ✨ Features

### Monte Carlo Simulation
- Run 100-5000 simulation paths to understand the range of possible outcomes
- Visualize uncertainty with percentile bands (10th, 25th, 50th, 75th, 90th)
- See individual sample paths to understand variability
- Real vs. nominal value toggle

### Comprehensive Financial Modeling
- **Income**: Gross income, taxes, pension contributions, salary inflation
- **Expenses**: Monthly living expenses with inflation tracking
- **Property**: Home equity, appreciation, mortgage amortization
- **Investments**: Portfolio returns with configurable volatility
- **Pension**: Separate pension wealth tracking with contributions

### Detailed Event System
Six event types to model major life changes:

1. **Property Purchase** - Buy additional properties with automatic mortgage calculation
2. **Property Sale** - Sell properties and capture proceeds
3. **One-Time Expense** - Vehicle purchases, renovations, relocations
4. **Expense Change** - Ongoing expense increases (kids, lifestyle) or decreases
5. **Rental Income** - Model rental property income or suite rentals
6. **Windfall** - Inheritances, bonuses, insurance payouts

### Advanced Visualizations
- **Net Worth Trajectory**: 30-year projection with confidence intervals
- **Wealth Composition**: Breakdown of liquid wealth, pension, and property equity
- **Cash Flow Projection**: Year-by-year detailed cash flow analysis
- **Distribution Histograms**: Wealth distributions at key milestone years
- **Percentile Tables**: Detailed statistical breakdowns

### Intelligent Cash Flow Analysis
- Automatic mortgage payment calculation based on amortization
- Separate salary inflation vs. general inflation
- Pre-simulation cash flow validation
- Warnings when liquid wealth goes negative
- Recommendations for maintaining positive cash flow

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wealth-simulator.git
cd wealth-simulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run wealth_simulator.py
```

The app will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Basic Setup

1. **Initial Position**
   - Enter your current liquid wealth (cash, investments)
   - Enter property value and mortgage balance
   - Set mortgage amortization period (years remaining)

2. **Income & Tax**
   - Set gross annual income
   - Configure effective tax rate
   - Set pension contribution rate (% of gross)

3. **Monthly Budget**
   - Enter monthly living expenses
   - Mortgage payment is auto-calculated from amortization

4. **Investment Assumptions**
   - Expected annual return (e.g., 7%)
   - Return volatility/standard deviation (e.g., 15%)

5. **Inflation**
   - General inflation rate (affects expenses)
   - Salary inflation rate (income growth)

### Adding Financial Events

Click "+ Add Event" and configure:

**Property Purchase Example:**
- Year: 5
- Description: "Dublin Home Purchase"
- Property Price: $675,000
- Down Payment: $135,000
- Mortgage Amount: $540,000
- Amortization: 25 years
- Payment auto-calculates based on interest rate

**Expense Change Example:**
- Year: 7
- Description: "First Child"
- Monthly Change: +$1,500
- Effect: Increases ongoing expenses by $1,500/month

**Rental Income Example:**
- Year: 4
- Description: "Basement Suite Rental"
- Monthly Rental: $2,000
- Effect: Adds $2,000/month ongoing income

### Running the Simulation

1. Review the pre-simulation cash flow summary
2. Verify your initial net worth
3. Check configured events
4. Click "Run Simulation"
5. Explore results:
   - Toggle between Real (inflation-adjusted) and Nominal values
   - Switch views: Total Net Worth, Liquid Wealth, Property Equity, Pension
   - Review cash flow projection table
   - Examine wealth distributions at key years

## 📊 Understanding the Results

### Key Metrics
- **Median Final Wealth**: 50th percentile outcome
- **Mean Final Wealth**: Average across all simulations
- **Probability of Growth**: Chance of exceeding initial wealth
- **Probability of 2x Growth**: Chance of doubling wealth

### Percentile Bands
- **10th-25th**: Worst-case scenarios (1 in 10 chance)
- **25th-50th**: Below-average outcomes
- **50th (Median)**: Most likely outcome
- **50th-75th**: Above-average outcomes
- **75th-90th**: Best-case scenarios (1 in 10 chance)

### Cash Flow Warnings
- 🔴 **Negative cash flow**: Expenses exceed income
- 🟡 **Liquid wealth goes negative**: You're depleting savings
- 🟢 **Positive trajectory**: Sustainable plan

## 🎓 Example Scenarios

### Scenario 1: Property Relocation
```
Year 4: Property Sale - $800k
Year 4: One-Time Expense (Moving) - $15k
Year 4: Property Purchase - $675k
Year 5: Expense Change (Higher COL) - +$500/month
```

### Scenario 2: Growing Family
```
Year 5: Expense Change (First Child) - +$1,500/month
Year 8: Expense Change (Second Child) - +$1,200/month
Year 15: Expense Change (Kids Independent) - -$2,700/month
```

### Scenario 3: Rental Property Portfolio
```
Year 3: Property Purchase (Rental) - $450k
Year 4: Rental Income (Rental Property) - +$2,200/month
Year 10: Property Purchase (Second Rental) - $500k
Year 11: Rental Income (Second Rental) - +$2,400/month
```

## 🔧 Technical Details

### Monte Carlo Methodology
- **Returns**: Geometric Brownian motion with configurable mean and volatility
- **Inflation**: Stochastic inflation with mean and standard deviation
- **Cash Flows**: Annual rebalancing with inflation adjustments
- **Mortgage**: Standard amortization formula with proper interest/principal split

### Assumptions
- Investment returns follow log-normal distribution
- Inflation follows normal distribution (bounded at -5%)
- Salary inflation is deterministic (not stochastic)
- Expenses inflate with general inflation
- Mortgage payments are fixed in nominal terms
- Property appreciation is constant (not stochastic)
- No taxes on investment gains (simplified)

### Limitations
- Does not model detailed tax calculations
- Property appreciation is constant, not variable
- No sequence of returns risk modeling
- Simplified pension model (no employer matching details)
- No consideration of currency exchange rate risk

## 📁 Project Structure

```
wealth-simulator/
├── wealth_simulator.py    # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## 💡 Educational Resources
- [Understanding Monte Carlo Simulation](Understanding%20Monte%20Carlo%20Simulation.md)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add currency selection (USD, CAD, EUR, GBP)
- [ ] More sophisticated tax modeling
- [ ] Variable property appreciation
- [ ] Sequence of returns risk analysis
- [ ] Export results to PDF/Excel
- [ ] Scenario comparison (side-by-side)
- [ ] Goal-based planning (retirement, education)
- [ ] Multi-currency support for international scenarios

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Interactive web app framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [NumPy](https://numpy.org/) - Numerical computing
- [Pandas](https://pandas.pydata.org/) - Data manipulation

## 📧 Contact

For questions, suggestions, or feedback, please open an issue on GitHub.

---

**Disclaimer**: This tool is for educational and planning purposes only. It is not financial advice. Consult with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results. All projections are hypothetical and subject to significant uncertainty. #FinSim
