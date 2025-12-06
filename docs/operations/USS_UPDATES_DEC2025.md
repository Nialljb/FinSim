# USS Pension Updates - December 2025

## Summary of Changes

This update corrects the USS contribution rates and adds Additional Voluntary Contribution (AVC) functionality.

## 1. Updated USS Contribution Rates

### Previous (Incorrect) Rates:
- **Employer**: 21.6%
- **Employee**: 8.6% (up to £43,143) / 11.6% (above threshold)

### Current (Correct) Rates:
- **Employer**: 14.5%
- **Employee**: 6.1% (flat rate)

The contribution calculation has been simplified to use a flat 6.1% employee rate across all salary levels, matching the actual USS scheme rates.

## 2. Additional Voluntary Contributions (AVC)

### What are AVCs?
AVCs are extra contributions that USS members can make on top of their standard pension contributions. These go into the **USS Investment Builder**, which is a defined contribution investment fund separate from the main USS pension benefit.

### Key Features:
- **Flexible Contributions**: Choose any percentage of salary (0-20%)
- **Investment Builder**: AVCs are invested in fund options you select
- **Tax Relief**: Get tax relief on AVC contributions (20-45% depending on tax bracket)
- **Flexible Access**: Can be drawn down flexibly in retirement, unlike the main USS pension

### How It Works:
1. Set your AVC percentage (e.g., 5% of salary)
2. Contributions are automatically calculated based on your salary
3. AVCs go into USS Investment Builder investment funds
4. At retirement, you can:
   - Take 25% as tax-free lump sum
   - Draw down the rest as needed
   - Convert to annuity
   - Mix different options

### Example:
- **Salary**: £50,000
- **Standard USS Contributions**:
  - Employee: £3,050 (6.1%)
  - Employer: £7,250 (14.5%)
  - Total: £10,300
- **AVC**: 5% = £2,500
- **Total Monthly Deduction**: (£3,050 + £2,500) / 12 = £462.50

### Integration with FinSim
The AVC feature has been integrated into the pension planner:
- Track AVC contributions separately from main USS pension
- Calculate total retirement income including AVC pot
- See how AVCs boost your retirement income
- Plan AVC drawdown strategy alongside main pension

## 3. Database Changes

### New Fields Added:
- `uss_avc_enabled`: Boolean - whether user makes AVCs
- `uss_avc_annual_amount`: Float - annual AVC amount in £
- `uss_avc_percentage`: Float - AVC as percentage of salary

### Migration:
Run automatically when using the app. Can also run manually:
```bash
python migrations/add_uss_avc_fields.py
```

## 4. UI Changes

### USS Pension Calculator Tab:
- **New Section**: "Additional Voluntary Contributions (AVC)"
  - Checkbox to enable AVC tracking
  - Slider to set AVC percentage (0-20%)
  - Real-time calculation of AVC amounts
  - Monthly and annual AVC displays
  
- **Updated Contributions Display**:
  - Shows standard USS contributions (employee + employer)
  - Shows AVC contributions separately
  - Shows total including AVCs
  - Displays all rates as percentages

- **Info Box**: Explains what AVCs are and how they integrate with USS Investment Builder

## 5. Technical Changes

### Files Modified:
1. **pension_planner.py**:
   - Updated USS contribution constants
   - Modified `calculate_uss_contributions()` to accept `avc_amount` parameter
   - Returns AVC details in contribution dictionary

2. **pension_ui.py**:
   - Added AVC input section
   - Updated contribution display to show AVCs
   - Modified save/load functions to handle AVC data

3. **database.py**:
   - Added three new columns to `PensionPlan` model

4. **migrations/add_uss_avc_fields.py**:
   - New migration script for AVC fields

## 6. Future Enhancements

Potential future additions:
- [ ] USS Investment Builder fund selection
- [ ] AVC projection with different growth rates
- [ ] Comparison tool: AVC vs. SIPP
- [ ] Tax relief calculator for AVCs
- [ ] Integration with main simulator for retirement income modeling
- [ ] AVC contribution history tracking
- [ ] Optimal AVC percentage calculator

## 7. User Benefits

1. **Accurate USS Tracking**: Correct contribution rates (14.5%/6.1%)
2. **Comprehensive Planning**: See full picture including AVCs
3. **Flexibility**: Model different AVC scenarios
4. **Better Retirement Estimates**: Include all USS income sources
5. **Tax Planning**: Optimize AVC contributions for tax efficiency

## 8. References

- USS Official Website: https://www.uss.co.uk/
- USS Investment Builder: https://www.uss.co.uk/for-members/investment-builder
- USS Contribution Rates: https://www.uss.co.uk/for-members/contributions-and-benefits
- HMRC Pension Tax Relief: https://www.gov.uk/tax-on-your-private-pension/pension-tax-relief
