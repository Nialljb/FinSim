# UK Pension Planner - Feature Documentation

## Overview

The UK Pension Planner is a comprehensive retirement planning tool integrated into FinSim. It helps users plan their retirement income from multiple UK pension sources:

- 🏛️ **State Pension** - UK government pension based on National Insurance contributions
- 🎓 **USS Pension** - Universities Superannuation Scheme for university employees
- 💰 **SIPP** - Self-Invested Personal Pension with tax relief
- 📈 **Retirement Income** - Combined income planning and sustainability analysis

---

## Features

### 1. State Pension Calculator

**What it calculates:**
- State Pension age based on date of birth
- Qualifying years needed (minimum 10, full pension at 35)
- Projected annual pension amount (£11,502.40 max for 2025/26)
- Monthly and weekly pension amounts
- Gaps in NI record and how to fill them

**How to use:**
1. Enter your date of birth
2. Input current NI qualifying years (check at gov.uk)
3. Select employment status
4. View projected pension at State Pension age

**Key Constants (2025/26):**
- Full State Pension: £11,502.40/year (£221.20/week)
- Minimum qualifying years: 10
- Years for full pension: 35
- Current State Pension age: 67 (varies by birth year)

---

### 2. USS Pension Calculator

**What it calculates:**
- Monthly contributions (employee + employer)
- Projected annual pension at retirement
- Tax-free lump sum available (3x annual pension)
- Growth based on salary increases
- Total years in scheme projection

**How it works:**
- Accrual rate: 1/85th of salary per year
- Example: 20 years × £50,000 = £11,765/year pension
- Plus £35,295 tax-free lump sum

**Contribution rates:**
- Employee: 8.6% (up to threshold) / 11.6% (above threshold)
- Employer: 21.6%
- Threshold: £43,143 (2024/25)

**How to use:**
1. Enter current annual salary
2. Input years in USS scheme
3. Set retirement age and salary growth expectations
4. View projected pension and lump sum

---

### 3. SIPP Calculator

**What it calculates:**
- Tax relief on contributions (20-45% depending on income)
- Projected pot value at retirement
- Tax-free lump sum (25% of pot)
- Remaining pot for income drawdown
- Sustainable withdrawal rates

**Tax Relief:**
- Basic rate (20%): Automatic via pension provider
- Higher rate (40%): Claim additional 20% via tax return
- Additional rate (45%): Claim additional 25%

**Example:**
- You pay: £8,000
- Tax relief: £2,000 (basic rate)
- Pension gets: £10,000
- Effective bonus: 25%

**How to use:**
1. Enter current SIPP value
2. Set annual contribution amount
3. Input your annual income (for tax relief calculation)
4. Set retirement age and growth expectations
5. View projected pot value and income

**Key Limits:**
- Annual allowance: £60,000 (2025/26)
- Min pension age: 55 (rising to 57 in 2028)
- Tax-free lump sum: 25% of pot
- Lifetime allowance: Abolished April 2024

---

### 4. Retirement Income Planner

**What it shows:**
- Combined income from all pension sources
- Income sustainability analysis
- Pension drawdown strategies
- Coverage vs desired retirement income

**Drawdown Strategies:**
1. **Safe Rate (4%)**: Traditional sustainable withdrawal rate
2. **Custom Amount**: Set your own annual withdrawal
3. **Make it Last**: Calculate rate to last exact period

**How to use:**
1. Complete State Pension, USS, and SIPP sections first
2. Choose drawdown strategy
3. Set desired retirement income
4. View coverage percentage and sustainability

---

## Database Schema

### pension_plans Table

Stores user pension planning data:

```sql
- id: Primary key
- user_id: Foreign key to users table
- name: Plan name
- date_of_birth: For State Pension age calculation
- target_retirement_age: Desired retirement age

-- State Pension fields
- state_pension_enabled: Boolean
- state_pension_ni_years: Current qualifying years
- state_pension_projected_years: Future years
- state_pension_annual_amount: Projected amount

-- USS Pension fields
- uss_enabled: Boolean
- uss_current_salary: Current salary
- uss_years_in_scheme: Years in USS
- uss_projected_annual_pension: Projected pension
- uss_projected_lump_sum: Lump sum available

-- SIPP fields
- sipp_enabled: Boolean
- sipp_current_value: Current pot value
- sipp_annual_contribution: Annual contribution
- sipp_projected_value: Projected value at retirement
- sipp_growth_rate: Expected growth rate

-- Planning fields
- desired_retirement_income: Target income
- expected_total_pension_income: Calculated total
- salary_growth_rate: Expected growth
- drawdown_rate: Withdrawal rate
```

---

## Integration with Monte Carlo Simulator

### Current Status
- ✅ Pension data saved to database
- ✅ Standalone pension planning tab
- 🔄 Integration with simulator (in progress)
- ⏳ Post-retirement simulation mode (planned)

### Planned Integration

The pension planner will integrate with the Monte Carlo simulator in two ways:

#### 1. Pre-Retirement (Working Years)
- Pension contributions reduce available income
- USS contributions: Automatic payroll deduction
- SIPP contributions: Reduce disposable income
- Builds up pension pot value

#### 2. Post-Retirement (After retirement age)
- Employment income stops
- Pension income starts:
  - State Pension (fixed annual amount)
  - USS Pension (fixed annual amount)
  - SIPP Drawdown (variable, user-defined rate)
- Pension pot depletes over time with growth

### Example Simulation Flow

**Ages 30-67 (Working):**
- Income: £50,000/year (salary)
- Deductions: USS contributions (£4,300/year)
- SIPP: £5,000/year voluntary contribution
- Net income for living: £40,700/year

**Ages 67-90 (Retired):**
- Income: £30,000/year (pensions)
  - State Pension: £11,502/year
  - USS Pension: £12,000/year
  - SIPP Drawdown: £6,498/year (4% of £162,450)
- No salary, no pension contributions
- Pension pot: Starts at £162,450, depletes by £6,498/year

---

## File Structure

```
pension_planner.py      - Core calculations and models
pension_ui.py           - Streamlit UI components
database.py             - PensionPlan model added
migrations/             - Database migration scripts
  add_pension_plans_table.py
docs/                   - Documentation
  PENSION_PLANNER_README.md
```

---

## Usage Guide

### For Users

1. **Start with State Pension**
   - Most people qualify
   - Check your NI record at gov.uk
   - Enter qualifying years

2. **Add USS if applicable**
   - Only for university employees
   - Check payslip for contributions
   - Contact USS for years in scheme

3. **Plan SIPP contributions**
   - Tax-efficient way to save more
   - Consider employer match if available
   - Track current pot value

4. **Review retirement income**
   - Check total vs desired income
   - Adjust SIPP contributions if needed
   - Plan drawdown strategy

### For Developers

**Adding new pension types:**

1. Add calculation functions to `pension_planner.py`
2. Add UI components to `pension_ui.py`
3. Add database fields to `PensionPlan` model
4. Create migration script
5. Update this README

**Constants to update annually:**
- State Pension amounts
- NI thresholds
- USS contribution rates and thresholds
- SIPP annual allowance
- Tax relief rates

---

## Testing

### Manual Testing Checklist

- [ ] State Pension calculator shows correct age
- [ ] NI qualifying years calculate correctly
- [ ] USS contributions match payslip
- [ ] USS pension projection reasonable
- [ ] SIPP tax relief calculates correctly
- [ ] SIPP growth projection works
- [ ] Retirement income totals correctly
- [ ] Drawdown sustainability analysis works
- [ ] Data saves to database
- [ ] Data loads on page refresh

### Test Cases

**State Pension:**
```
Born: 1980-01-01
Expected Pension Age: 67
NI Years: 20
Expected Pension: £6,572/year (20/35 of full)
```

**USS:**
```
Salary: £50,000
Years: 10
Expected Pension: £5,882/year (10 × £50,000 / 85)
Lump Sum: £17,647 (3 × £5,882)
```

**SIPP:**
```
Current Value: £50,000
Annual Contribution: £5,000
Years to Retirement: 20
Growth Rate: 5%
Expected Value: £215,479
```

---

## Known Limitations

1. **State Pension**: Simplified calculation - actual rules more complex for contracting out, etc.
2. **USS**: Based on 2024/25 rates - subject to scheme changes
3. **SIPP**: Tax relief assumes standard rates - may vary
4. **Drawdown**: Assumes constant withdrawal - doesn't model dynamic strategies
5. **Inflation**: Not yet integrated with main simulator's inflation modeling

---

## Future Enhancements

### Phase 1 (Current)
- ✅ State Pension calculator
- ✅ USS calculator
- ✅ SIPP calculator
- ✅ Retirement income planner

### Phase 2 (Next)
- [ ] Integration with Monte Carlo simulator
- [ ] Post-retirement simulation mode
- [ ] Pension contributions as events
- [ ] Tax optimization suggestions

### Phase 3 (Future)
- [ ] Multiple SIPP accounts
- [ ] Other workplace pensions (DB, DC)
- [ ] Inheritance planning
- [ ] State Pension top-up calculator
- [ ] Annuity vs drawdown comparison
- [ ] International pension schemes

---

## References

- [GOV.UK - State Pension](https://www.gov.uk/new-state-pension)
- [GOV.UK - Check NI Record](https://www.gov.uk/check-national-insurance-record)
- [USS - Member Resources](https://www.uss.co.uk/for-members)
- [MoneyHelper - SIPP Guide](https://www.moneyhelper.org.uk/en/pensions-and-retirement/pensions-basics/self-invested-personal-pensions-sipps)

---

## Support

For issues or questions:
1. Check this README
2. Review calculation functions in `pension_planner.py`
3. Submit feedback via the app's Feedback button
4. Create issue on GitHub

---

**Last Updated:** December 2025
**Version:** 1.0.0
**Status:** Beta - Ready for testing
