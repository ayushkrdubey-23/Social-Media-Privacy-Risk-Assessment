# Social Media Privacy Risk Assessment Framework

A defensive, privacy-first educational framework that helps users understand social-media privacy exposure through a 50-question self-assessment, explainable risk scoring, findings, recommendations, synthetic-data analytics, and a local SQLite-backed dashboard.

> **Educational disclaimer:** This project is intended for cybersecurity education and privacy awareness. Risk weights, thresholds, and scoring rules are educational assumptions. They are not professional security guarantees, certifications, or definitive predictions of privacy harm.

## Project Highlights

- 50-question social-media privacy assessment
- 10 privacy-risk categories
- 0–100 weighted risk score
- LOW / MODERATE / HIGH / CRITICAL classification
- Explainable privacy findings
- Actionable recommendations
- Privacy awareness checklist
- 1,200 fictional synthetic assessment records
- Privacy-safe SQLite persistence
- Flask REST APIs
- Responsive HTML/CSS/JavaScript frontend
- Chart.js analytics dashboard
- Assessment retrieval and deletion
- Privacy-by-design architecture
- Defensive-only ethical scope

## Privacy-First Design

The framework does **not**:

- scrape social-media platforms,
- access private accounts,
- bypass privacy settings,
- enumerate social-media accounts,
- track real individuals,
- collect passwords,
- collect private messages,
- require names, phone numbers, email addresses, or exact locations.

The questionnaire asks about privacy posture, settings, and awareness rather than requiring actual sensitive values.

## Risk Categories

| Category | Weight |
|---|---:|
| Profile Visibility | 10% |
| Personal Information | 15% |
| Location Privacy | 15% |
| Posts and Content | 10% |
| Friends and Followers | 10% |
| Tagging and Mentions | 5% |
| Account Security | 15% |
| Third-Party Applications | 5% |
| Messaging and Social Engineering | 10% |
| Digital Footprint | 5% |
| **Total** | **100%** |

## Risk Levels

| Score | Classification |
|---:|---|
| 0–20 | LOW |
| 21–40 | MODERATE |
| 41–70 | HIGH |
| 71–100 | CRITICAL |

A higher score means higher educational privacy exposure under this model.

## Technology Stack

**Backend:** Python, Flask, Flask-CORS, SQLite, Pandas, NumPy

**Frontend:** HTML, CSS, Vanilla JavaScript, Chart.js

**Testing / Reporting Foundation:** Pytest, ReportLab, Pillow

## Architecture

```text
Self-reported questionnaire
          ↓
Response validation
          ↓
Privacy feature extraction
          ↓
Category risk scoring
          ↓
Weighted 0–100 overall score
          ↓
Risk classification
          ↓
Findings
          ↓
Recommendations
          ↓
Privacy-safe SQLite persistence
          ↓
Dashboard / reporting layer
```

## Project Structure

```text
Social-Media-Privacy-Risk-Assessment/
├── backend/
│   ├── routes/
│   ├── models/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── css/
│   └── js/
├── data/
├── reports/
├── screenshots/
├── tests/
├── docs/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Development Status

The project is intentionally stopped at **Step 22 of 30 (73.33%)**.

The completed checkpoint includes the questionnaire, synthetic dataset, feature extraction, weighted risk engine, findings/recommendations, SQLite persistence, core APIs, dashboard API, privacy checklist API, and the 50-question frontend assessment workflow.

Future development from Step 23 onward can add an improvement simulator, expanded reports, additional tests, security hardening, and final release documentation.

## Local Setup

### 1. Clone the repository

```powershell
git clone https://github.com/ayushkrdubey-23/Social-Media-Privacy-Risk-Assessment.git
cd Social-Media-Privacy-Risk-Assessment
```

### 2. Create and activate the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and use development-only values locally.

Do not commit `.env`.

### 5. Start Flask

```powershell
python -m backend.app
```

The backend runs locally at:

```text
http://127.0.0.1:5000
```

### 6. Start the frontend

Open `frontend/index.html` through VS Code Live Server.

The frontend is configured to communicate with:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Health and information

- `GET /api/health`
- `GET /api/info`

### Questionnaire

- `GET /api/questionnaire`
- `GET /api/questionnaire/summary`
- `GET /api/questionnaire/question/<question_id>`
- `GET /api/questionnaire/category/<category>`

### Assessment

- `POST /api/assessment`
- `GET /api/assessment/<assessment_id>`
- `GET /api/assessment/<assessment_id>/recommendations`
- `DELETE /api/assessment/<assessment_id>`

### Dashboard

- `GET /api/dashboard/stats`
- `GET /api/dashboard/summary`

### Privacy checklist

- `GET /api/privacy-checklist`
- `GET /api/privacy-checklist/summary`
- `GET /api/privacy-checklist/category/<category>`

## Synthetic Dataset

The project includes a reproducible generator for 1,200 fictional assessment records:

```powershell
python -m backend.services.synthetic_data
```

The generated file is:

```text
data/social_media_privacy_assessments.csv
```

It is ignored by Git intentionally and is meant for local development and analytics.

## Privacy-Safe Database

SQLite stores derived assessment information rather than raw questionnaire responses.

The system is designed to avoid storing direct identifiers and sensitive values such as:

- passwords,
- phone numbers,
- email addresses,
- usernames,
- exact locations,
- private messages.

## Screenshots

The current screenshot evidence is stored in `screenshots/`:

| Screenshot | Evidence |
|---|---|
| `02_backend_health_api.png` | Backend/API health verification |
| `03_questionnaire_home.png` | Questionnaire landing page |
| `04_questionnaire_50_questions.png` | 50-question assessment interface |
| `05_privacy_dashboard.png` | Privacy dashboard |
| `06_privacy_checklist.png` | Privacy checklist |
| `07_awareness_privacy.png` | Privacy-awareness content |

## Documentation

See the `docs/` folder for:

- [Architecture](docs/architecture.md)
- [Privacy by Design](docs/privacy-by-design.md)
- [API Reference](docs/api-reference.md)
- [Project Status](docs/project-status.md)
- [Screenshot Index](docs/screenshot-guide.md)

## Educational and Ethical Scope

This project is designed for defensive cybersecurity education and privacy awareness. It should not be used to inspect, profile, monitor, or track real individuals or to access information that users have not voluntarily provided.

The scoring system is an educational model based on self-reported behavior and configured assumptions. It does not independently verify a platform's privacy settings and does not guarantee that users will avoid privacy incidents.

## Author

**Ayush Kumar Dubey**

Student developer / cybersecurity learner

## Acknowledgement

Special thanks to **Mr. Umesh Yadav Sir, Founder of IIP**, for guidance and support through the collaboration with **eDC IIT Delhi**.

## License

Choose and add an appropriate open-source license before public release if required by your institution or intended project usage.
