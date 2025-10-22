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
- **Database**: PostgreSQL with SQLAlchemy ORM (falls back to in-memory if not configured)
- **API**: RESTful endpoints for questions, assessments, and leads
- **Validation**: Pydantic models for data validation

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 16
- **Dev Containers**: VS Code dev container support

## Project Structure

```
Startup_Health_Chec/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application and routes
│   │   ├── models.py            # Pydantic models
│   │   ├── questions_data.py    # Assessment questions
│   │   ├── assessment_service.py # Scoring and recommendation logic
│   │   └── database.py          # Database layer (PostgreSQL/in-memory)
│   ├── pyproject.toml           # Python dependencies
│   ├── Dockerfile               # Backend Docker image
│   └── .env.example             # Backend environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main application component
│   │   ├── types.ts             # TypeScript type definitions
│   │   ├── api.ts               # API client functions
│   │   └── components/          # UI components
│   ├── package.json             # Node dependencies
│   ├── Dockerfile               # Frontend Docker image
│   └── .env.example             # Frontend environment variables template
├── .devcontainer/
│   └── devcontainer.json        # VS Code dev container configuration
├── docker-compose.yml           # Docker Compose orchestration
├── .env.example                 # Root environment variables template
└── README.md
```

## Getting Started

### Option 1: Docker Compose (Recommended)

This is the easiest way to get started with all services running together.

#### Prerequisites
- Docker
- Docker Compose

#### Setup Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Startup_Health_Chec
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure your settings (optional for local development, defaults work out of the box).

3. Start all services:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Backend API on port 8000
   - Frontend app on port 5173

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. View logs:
   ```bash
   docker-compose logs -f
   ```

6. Stop services:
   ```bash
   docker-compose down
   ```

7. Stop services and remove data:
   ```bash
   docker-compose down -v
   ```

### Option 2: Local Development (Without Docker)

#### Prerequisites
- Python 3.12+
- Node.js 18+
- Poetry (Python package manager)
- PostgreSQL 16+ (optional, will use in-memory storage if not configured)

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. (Optional) Configure PostgreSQL:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your `DATABASE_URL`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/startup_health_check
   ```
   
   If you don't configure this, the app will use in-memory storage.

4. Start the development server:
   ```bash
   poetry run fastapi dev app/main.py
   ```

   The backend will be available at `http://localhost:8000`

5. View API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   
   The default configuration points to `http://localhost:8000` which should work if you're running the backend locally.

4. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Option 3: VS Code Dev Containers

If you use VS Code, you can develop inside a container with all dependencies pre-configured.

#### Prerequisites
- Docker
- VS Code
- Remote - Containers extension

#### Setup Steps

1. Open the project in VS Code
2. Press `F1` and select "Remote-Containers: Reopen in Container"
3. Wait for the container to build and start
4. The backend will be available at `http://localhost:8000`
5. Open a new terminal and navigate to frontend to start it separately if needed

## Environment Variables

### Root `.env` (for Docker Compose)

```bash
# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=startup_health_check
POSTGRES_PORT=5432

# Backend Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/startup_health_check

# SMTP Configuration (for email notifications)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@example.com

# AWS SES Configuration (alternative to SMTP)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
SES_FROM_EMAIL=noreply@example.com

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

### Backend `.env`

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/startup_health_check

# SMTP Configuration (for email notifications)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@example.com

# AWS SES Configuration (alternative to SMTP)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
SES_FROM_EMAIL=noreply@example.com
```

### Frontend `.env`

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

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

## Database

The application supports both PostgreSQL and in-memory storage:

- **PostgreSQL**: When `DATABASE_URL` environment variable is set, the application uses PostgreSQL with SQLAlchemy ORM for persistent storage.
- **In-Memory**: If `DATABASE_URL` is not configured, the application falls back to in-memory storage. Data will be lost when the backend server restarts.

For production use, always configure PostgreSQL for data persistence.

## Docker Commands

### Build and Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Services
```bash
docker-compose up -d --build
```

### Access Database
```bash
docker-compose exec postgres psql -U postgres -d startup_health_check
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d
```

## Deployment

For comprehensive deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### PR Preview Deployments

Every pull request automatically gets its own preview environment deployed to AWS! This allows you to test changes before merging.

**How it works:**
- Open a PR → Preview environment automatically deploys
- Push commits → Preview updates automatically
- Close PR → Resources cleaned up automatically

**Preview URLs:**
- Frontend: `http://pr-{number}.deploymirror.com`
- Backend API: `http://pr-{number}-api.deploymirror.com`

See [PREVIEW_DEPLOYMENTS.md](./PREVIEW_DEPLOYMENTS.md) for detailed information about:
- How preview deployments work
- Setup requirements
- Monitoring and troubleshooting
- Cost optimization

### Quick Start - AWS Deployment

The application is designed to be deployed on AWS using ECS Fargate with the following architecture:

- **ECS Fargate**: Container orchestration for backend and frontend
- **Application Load Balancer**: Traffic distribution and SSL termination
- **RDS PostgreSQL**: Managed database service
- **CloudWatch**: Structured logging and monitoring
- **AWS SES**: Email notifications with DKIM/SPF
- **Secrets Manager**: Secure credential storage

**Deploy to AWS**:
```bash
cd aws
export DATABASE_PASSWORD="your-secure-password"
export NOTIFICATION_EMAIL="service@offrd.co"
export SENDER_EMAIL="noreply@offrd.co"
./deploy.sh
```

**Set up monitoring**:
```bash
./setup-monitoring.sh
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions including:
- Infrastructure setup
- SSL/TLS configuration
- Email configuration (SES with DKIM/SPF)
- Monitoring and alerting
- Uptime monitoring (Pingdom)
- Troubleshooting guide
- Cost optimization
- Security best practices

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
