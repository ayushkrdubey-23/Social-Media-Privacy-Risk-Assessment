
# System Architecture

## Project

Social Media Privacy Risk Assessment Framework

## 1. Architecture Overview

The application follows a modular architecture.

The frontend collects voluntarily provided questionnaire
responses and communicates with the Flask backend.

The backend validates responses, extracts privacy features,
calculates category risks, generates findings and provides
personalized recommendations.

## 2. System Workflow

User
  |
  v
Privacy Questionnaire
  |
  v
Input Validation
  |
  v
Privacy Feature Extraction
  |
  v
Category Risk Analysis
  |
  v
Risk Scoring Engine
  |
  v
Overall Privacy Risk Score
  |
  v
Risk Classification
  |
  v
Findings Engine
  |
  v
Recommendation Engine
  |
  v
Privacy Dashboard
  |
  v
Privacy Assessment Report

## 3. Backend Components

### Flask Application
Handles application initialization and REST API requests.

### Routes
Provides API endpoints for assessment, dashboard,
recommendations and reports.

### Models
Defines application data structures.

### Services
Contains the core assessment and risk-analysis logic.

### Utils
Contains database connectivity, configuration,
validation and reusable helper functions.

## 4. Frontend Components

### Homepage
Introduces the framework.

### Assessment
Collects privacy questionnaire responses.

### Dashboard
Displays overall risk and category scores.

### CSS
Provides application styling.

### JavaScript
Handles user interaction, API communication and charts.

## 5. Database Architecture

SQLite contains four primary tables:

- assessments
- category_scores
- findings
- recommendations

The database stores assessment metadata and risk results.

It does not store unnecessary personal information.

## 6. Privacy-First Processing

The framework uses:

- Synthetic assessment records.
- Voluntarily entered questionnaire responses.
- Data minimization.
- Purpose limitation.
- Privacy by default.
- Retention limitation.

Actual phone numbers, email addresses, passwords,
home addresses and private messages are not required.

## 7. Risk Calculation

The framework calculates category scores between 0 and 100.

Higher scores indicate higher assessed exposure.

The overall score uses configurable category weights.

## 8. Risk Classification

| Score | Risk Level |
|---|---|
| 0-20 | LOW |
| 21-40 | MODERATE |
| 41-70 | HIGH |
| 71-100 | CRITICAL |

## 9. Ethical Scope

This project is designed for defensive cybersecurity
and privacy education.

It does not scrape social-media profiles,
access private accounts, bypass privacy settings,
enumerate accounts or track real individuals.

## 10. Limitations

The assessment relies on self-reported information.

It cannot independently verify a platform's actual
privacy configuration.

Its scores are educational estimates rather than
guarantees of security.
