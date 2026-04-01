# Code-to-Code Translator

[![GitHub license](https://img.shields.io/github/license/Dhanushree741/Code-to-Code-Translator)](https://github.com/Dhanushree741/Code-to-Code-Translator/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

## Overview

AI-powered **Code-to-Code Translator** that detects design patterns in Java/JavaScript code and translates between languages. Uses PMD static analysis + ML models for pattern detection, Flask API backend, React frontend.

## Features

- **Design Pattern Detection**: Singleton, Factory Method, Repository (Java/JS)
- **Code Translation**: Java ↔ JavaScript, Python to Java pattern equivalents
- **PMD Integration**: Custom rules for pattern matching
- **ML Pipeline**: Trained models in `module4_documentation/` for advanced detection
- **Fullstack App**: React UI + Flask API + Streamlit dashboard

## Project Structure

```
.
├── backend/                 # Flask API + PMD pattern detector
│   ├── pattern_detector.py
│   ├── flask_app.py
│   ├── pmd_rules/          # Custom PMD rules
│   └── config.py
├── frontend/               # React app
│   ├── src/App.js
│   └── public/
├── module4_documentation/  # ML training pipeline
│   ├── train_m4.py
│   ├── preprocess.py
│   └── app_backend.py
├── app.py                  # Streamlit dashboard
├── test_*.py              # Tests
├── pmd-bin-6.55.0/        # PMD binary
└── README.md
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt  # Create if needed
python flask_app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Streamlit
```bash
pip install streamlit
streamlit run app.py
```

### ML Models
```bash
cd module4_documentation
python preprocess.py
python train_m4.py
```

## API Endpoints

- `POST /detect_pattern` - Upload code, get patterns
- `POST /translate` - Translate pattern to target language

## Development

- Run tests: `python -m pytest test_*.py`
- PMD: `./pmd-bin-6.55.0/bin/pmd.bat check -d . -R backend/pmd_rules/`

## License

MIT
