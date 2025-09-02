# Serverless Real Estate Backend (AWS SAM + Python)

This project scaffolds a secure serverless backend using AWS SAM, API Gateway (REST), Lambda (Python 3.12), and DynamoDB. It includes a reusable Lambda Layer with common utilities and a GitHub Actions pipeline for CI/CD.

## Architecture
- API Gateway (REST) with API Key and Usage Plan
- Lambda functions (Python 3.12)
  - `GET /properties` → list items
  - `GET /properties/{id}` → get item by id
  - `POST /internal/sync/realtor` → placeholder for Realtor ingestion
  - `POST /internal/sync/zillow` → placeholder for Zillow ingestion
- DynamoDB table for property storage
- Lambda Layer for shared utilities (`requests`, simple DynamoDB helpers)

## Repo Layout
- `template.yaml` — SAM template with API, Lambdas, DynamoDB, API key, usage plan
- `src/functions/*/app.py` — Lambda handlers
- `src/layers/common` — Shared Python libs + requirements
- `.github/workflows/deploy.yml` — CI/CD with SAM build/deploy

## Prerequisites
- AWS account with permissions to deploy CloudFormation, API Gateway, Lambda, DynamoDB, and S3.
- Option A (local): Install AWS CLI, SAM CLI, and Docker (for `--use-container` builds).
- Option B (CI-only): Use the provided GitHub Actions workflow with OIDC role.

## Bootstrapping (One-time)
1. Create an IAM role for GitHub OIDC (recommended) or use access keys locally.
   - OIDC role must allow `cloudformation:*`, `s3:*` (on deploy bucket), `lambda:*`, `apigateway:*`, `dynamodb:*`.
2. Create GitHub repo secrets:
   - `AWS_DEPLOY_ROLE_ARN` — OIDC role ARN to assume.
   - `AWS_REGION` — e.g., `us-east-1`.
   - `STACK_NAME` — e.g., `airtime-app`.
   - `ENVIRONMENT_NAME` — e.g., `dev`.
   - `API_KEY_VALUE` — secure random API key value used in API Gateway. Keep secret.

## Local Build & Deploy
```
sam build --use-container
sam deploy \
  --stack-name airtime-app \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides EnvironmentName=dev ApiKeyValue=<YOUR_SECURE_API_KEY>
```

Outputs include `ApiUrl`. Call the API with header `X-Api-Key: <API_KEY_VALUE>`.

## Example Calls
```
# List properties
curl -H "X-Api-Key: $API_KEY_VALUE" "$API_URL/properties"

# Get property
curl -H "X-Api-Key: $API_KEY_VALUE" "$API_URL/properties/zi-1"

# Trigger Realtor sync (placeholder)
curl -X POST -H "X-Api-Key: $API_KEY_VALUE" "$API_URL/internal/sync/realtor"
```

## Extending: Realtor and Zillow integrations
- Implement real HTTP calls in:
  - `src/functions/sync_realtor/app.py`
  - `src/functions/sync_zillow/app.py`
- Add auth keys via environment variables or AWS Secrets Manager/SSM. Grant the function `ssm:GetParameter` / `secretsmanager:GetSecretValue` policy and fetch at runtime.

## Security Notes
- API Key restricts access + allows throttling, but is not identity/auth by itself. For stronger auth:
  - Switch to HTTP API (`AWS::Serverless::HttpApi`) with a JWT authorizer (Cognito) and drop API keys, or
  - Add a Lambda authorizer to the current REST API for custom tokens.
- Set fine-grained IAM for DynamoDB if different functions need different access.

## Next Steps
- Replace placeholder sync logic with real API interactions.
- Add pagination and query filters to `/properties`.
- Add input validation and error handling.
- Add tests (pytest) and a staging environment.

## Clean Up
```
aws cloudformation delete-stack --stack-name airtime-app
```

