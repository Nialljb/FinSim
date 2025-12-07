# Contributing to Monte Carlo Wealth Simulator

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, browser)

### Suggesting Features

Feature suggestions are welcome! Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- Any examples or mockups

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/wealth-simulator.git
cd wealth-simulator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run wealth_simulator.py
```

### Code Style

- Follow PEP 8 style guidelines
- Add comments for complex logic
- Update README.md if you add features
- Keep functions focused and modular

### Testing

Before submitting:
- Test with various input combinations
- Check edge cases (negative cash flow, zero values, etc.)
- Verify calculations are accurate
- Test on different screen sizes

### Priority Features

High-impact features we'd love help with:
- Multi-currency support
- PDF/Excel export functionality
- Advanced tax modeling
- Scenario comparison view
- Goal-based planning tools
- Database integration for saving scenarios

## Questions?

Feel free to open an issue for any questions about contributing!