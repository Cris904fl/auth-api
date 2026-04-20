# Auth API — FastAPI + JWT + Google OAuth2 + DynamoDB + AWS Lambda

REST API with JWT authentication, Google OAuth2 login, role-based access control, and DynamoDB persistence. Built to run locally with Docker and deployable to AWS Lambda with zero code changes.

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Auth | JWT (python-jose) + Google OAuth2 |
| Database | AWS DynamoDB (mocked locally with amazon/dynamodb-local) |
| Cloud | AWS Lambda + API Gateway (via Mangum adapter) |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## Architecture

```
Client → API Gateway → Lambda (Mangum) → FastAPI
                                         ├── /auth/register    (JWT)
                                         ├── /auth/login       (JWT)
                                         ├── /auth/google      (OAuth2)
                                         ├── /users/me         (protected)
                                         └── /users/           (admin only)
                                                    ↓
                                               DynamoDB
```

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | ❌ | Health check |
| POST | `/auth/register` | ❌ | Register with email + password |
| POST | `/auth/login` | ❌ | Login, returns JWT |
| GET | `/auth/google` | ❌ | Redirect to Google login |
| GET | `/auth/google/callback` | ❌ | Google OAuth2 callback |
| GET | `/users/me` | ✅ JWT | Get current user profile |
| GET | `/users/` | ✅ Admin | List all users |

## Run locally

```bash
# 1. Clone and configure
cp .env.example .env

# 2. Start API + DynamoDB local
docker compose -f docker/docker-compose.yml up

# 3. Open docs
open http://localhost:8000/docs
```

## Google OAuth2 setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → APIs & Services → Credentials → OAuth 2.0 Client ID
3. Add `http://localhost:8000/auth/google/callback` as authorized redirect URI
4. Copy Client ID and Secret to your `.env`

## AWS Deployment

```bash
# Package for Lambda
pip install -r requirements.txt -t package/
cd package && zip -r ../function.zip . && cd ..
zip function.zip -r src/

# Deploy via AWS CLI
aws lambda create-function \
  --function-name auth-api \
  --runtime python3.11 \
  --handler src.main.handler \
  --zip-file fileb://function.zip \
  --environment Variables="{JWT_SECRET_KEY=...,USERS_TABLE=users}"
```

## Run tests

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=src
```
