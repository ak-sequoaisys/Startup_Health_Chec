# Startup Compliance Health Check Tool

An interactive compliance self-assessment tool designed to help startups evaluate their HR & labour compliance and generate qualified leads.

## Overview

This application provides a comprehensive 15-question assessment covering key compliance areas including:
- Employment Contracts
- Workplace Safety
- Payroll & Tax
- Employee Benefits
- Workplace Policies
- Record Keeping
- Termination Procedures

## Features

- **Interactive Assessment**: User-friendly multi-step assessment flow with progress tracking
- **Instant Results**: Real-time scoring and risk level analysis
- **Category Breakdown**: Detailed analysis by compliance category
- **Personalized Recommendations**: Actionable advice based on assessment results
- **Lead Generation**: Automatic capture and storage of assessment submissions
- **Professional UI**: Modern, responsive design with gradient backgrounds and intuitive navigation

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: In-memory storage (proof of concept)
- **API**: RESTful endpoints for questions, assessments, and leads
- **Validation**: Pydantic models for data validation

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React

## Project Structure

```
Startup_Health_Chec/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application and routes
│   │   ├── models.py            # Pydantic models
│   │   ├── questions_data.py    # Assessment questions
│   │   ├── assessment_service.py # Scoring and recommendation logic
│   │   └── database.py          # In-memory database
│   ├── pyproject.toml           # Python dependencies
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main application component
│   │   ├── types.ts             # TypeScript type definitions
│   │   ├── api.ts               # API client functions
│   │   └── components/          # UI components
│   ├── package.json             # Node dependencies
│   └── .env                     # Environment variables
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry (Python package manager)
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Start the development server:
   ```bash
   poetry run fastapi dev app/main.py
   ```

   The backend will be available at `http://localhost:8000`

4. View API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   Create a `.env` file with:
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## API Endpoints

### Questions
- `GET /api/questions` - Get all assessment questions
- `GET /api/questions/{question_id}` - Get a specific question

### Assessments
- `POST /api/assessments` - Submit a new assessment
- `GET /api/assessments` - Get all assessments
- `GET /api/assessments/{assessment_id}` - Get a specific assessment

### Leads
- `GET /api/leads` - Get all leads
- `GET /api/leads/{lead_id}` - Get a specific lead

### Health Check
- `GET /healthz` - Health check endpoint

## Assessment Flow

1. **Introduction**: Welcome screen with feature highlights
2. **Contact Information**: User provides company and contact details
3. **Assessment**: 15 questions with multiple-choice answers
4. **Results**: Comprehensive report with:
   - Overall compliance score and risk level
   - Priority actions
   - Category-by-category breakdown
   - Specific issues and recommendations
   - Call-to-action for consultation

## Scoring System

- Each question has weighted scoring (1-3 points)
- Answers are scored from 0-10 based on compliance level
- Risk levels are calculated based on percentage scores:
  - **Low**: 80%+
  - **Medium**: 60-79%
  - **High**: 40-59%
  - **Critical**: <40%

## Database Note

This proof of concept uses an in-memory database. Data will be lost when the backend server restarts. For production use, integrate with PostgreSQL or another persistent database.

## Deployment

### Backend Deployment
The backend can be deployed to Fly.io using the deploy command:
```bash
# From project root
deploy backend --dir backend
```

### Frontend Deployment
The frontend can be deployed as a static site:
```bash
# Build the frontend
cd frontend
npm run build

# Deploy the dist folder
deploy frontend --dir frontend/dist
```

Make sure to update the `VITE_API_URL` in the frontend `.env` file to point to the deployed backend URL before building.

## Future Enhancements

- Email notifications with assessment results
- PDF report generation
- Admin dashboard for viewing leads
- PostgreSQL database integration
- User authentication and saved assessments
- Multi-language support
- Industry-specific question sets
- Integration with CRM systems

## License

Copyright © 2025. All rights reserved.

## Contact

For questions or support, please contact the development team.
