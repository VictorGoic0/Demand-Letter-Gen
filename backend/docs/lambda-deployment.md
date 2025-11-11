# Lambda Deployment Guide

This guide covers the Lambda-optimized application structure, local testing, and deployment procedures.

## Overview

The backend is structured for AWS Lambda deployment using the Serverless Framework. Each service endpoint is deployed as a separate Lambda function, sharing common dependencies through Lambda layers.

## Architecture

### Lambda Functions
- Each service (documents, templates, letters) has its own Lambda function
- Functions share a common dependencies layer to reduce package size
- API Gateway routes HTTP requests to appropriate Lambda functions

### Lambda Layers
- **Common Dependencies Layer**: Contains shared Python packages (FastAPI, SQLAlchemy, boto3, etc.)
- Reduces individual function package sizes
- Faster deployments and updates

## Prerequisites

1. **Node.js 18+** (for Serverless Framework)
2. **Python 3.11** (matching Lambda runtime)
3. **Docker** (for building Lambda packages with native dependencies)
4. **AWS CLI** configured with appropriate credentials
5. **Serverless Framework** installed globally or via npm

## Installation

### Install Serverless Framework and Plugins

```bash
cd backend
npm install
```

This installs:
- `serverless` - Serverless Framework CLI
- `serverless-offline` - Local Lambda/API Gateway emulation
- `serverless-python-requirements` - Python dependency management for Lambda

### Global Installation (Optional)

```bash
npm install -g serverless
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory with all required variables (see `.env.example` for reference).

The `serverless.yml` automatically reads these environment variables and injects them into Lambda functions.

### Serverless Configuration

The `serverless.yml` file contains:
- Service name and provider settings
- Environment variable mappings
- IAM role permissions
- Package exclusions
- Lambda layer configuration
- Function definitions (to be added as services are implemented)

## Local Development with serverless-offline

### Start Local Server

```bash
cd backend
npm run offline
# or
serverless offline
```

This starts a local server at `http://localhost:3000` that emulates:
- API Gateway routing
- Lambda function execution
- Request/response transformation

### Testing Endpoints

Once the server is running, you can test endpoints:

```bash
# Health check
curl http://localhost:3000/dev/health

# Example document endpoint (when implemented)
curl http://localhost:3000/dev/documents
```

### Configuration

The `serverless-offline` plugin is configured in `serverless.yml`:

```yaml
custom:
  serverless-offline:
    httpPort: 3000
    lambdaPort: 3002
    host: 0.0.0.0
    prefix: 'dev'
```

## Lambda Package Optimization

### Package Exclusions

The `serverless.yml` excludes unnecessary files from Lambda packages:

- Test files and directories
- Documentation
- Development tools
- Docker files
- Migration files
- Cache directories

### Dependency Optimization

The `serverless-python-requirements` plugin:

1. **Docker-based builds**: Uses Docker to build native dependencies (e.g., psycopg2-binary)
2. **Slim packages**: Strips unnecessary files from packages
3. **Layer support**: Creates a common dependencies layer
4. **Zip optimization**: Compresses packages for faster uploads

### Layer Configuration

Common dependencies are packaged into a Lambda layer:

```yaml
layers:
  commonDependencies:
    path: layer
    name: ${self:provider.stage}-common-dependencies
    compatibleRuntimes:
      - python3.11
```

Functions reference this layer to reduce package size:

```yaml
functions:
  myFunction:
    layers:
      - { Ref: CommonDependenciesLambdaLayer }
```

## Deployment

### Deploy to Development

```bash
cd backend
npm run deploy:dev
# or
serverless deploy --stage dev
```

### Deploy to Production

```bash
cd backend
npm run deploy:prod
# or
serverless deploy --stage prod --region us-east-2
```

### Deploy Specific Function

```bash
serverless deploy function -f functionName --stage dev
```

### Deploy Layer Only

```bash
serverless deploy layer --stage dev
```

## Handler Structure

Each Lambda function uses a handler pattern:

1. **Service Router**: FastAPI router with endpoint definitions
2. **Lambda Handler**: Wraps router using Mangum adapter
3. **Handler Export**: Exported function for serverless.yml

See `handlers/README.md` for detailed handler patterns.

## Function Configuration

### Memory and Timeout

Default settings in `serverless.yml`:
- Memory: 512MB
- Timeout: 30 seconds

Override for specific functions:

```yaml
functions:
  letterGenerate:
    memorySize: 1024  # 1GB for AI operations
    timeout: 60       # 60 seconds for AI generation
```

### Environment-Specific Settings

Use stage variables to configure different settings per environment:

```yaml
provider:
  stage: ${opt:stage, 'dev'}
  environment:
    ENVIRONMENT: ${self:provider.stage}
```

## Monitoring and Logging

### CloudWatch Logs

All Lambda functions automatically log to CloudWatch:
- Log group: `/aws/lambda/demand-letter-generator-{stage}-{functionName}`
- Log retention: Configured per environment

### View Logs

```bash
# Tail logs for a function
serverless logs -f functionName --tail --stage dev

# View recent logs
serverless logs -f functionName --stage dev
```

## Troubleshooting

### Common Issues

1. **Docker not running**: Required for building Python packages with native dependencies
   - Solution: Start Docker Desktop or Docker daemon

2. **Permission errors**: AWS credentials not configured
   - Solution: Run `aws configure` or set environment variables

3. **Layer not found**: Layer not deployed before functions
   - Solution: Deploy layer first: `serverless deploy layer`

4. **Timeout errors**: Function execution exceeds timeout
   - Solution: Increase timeout in function configuration

5. **Memory errors**: Function runs out of memory
   - Solution: Increase memory allocation

### Debugging Locally

1. Use `serverless-offline` with verbose logging:
   ```bash
   SLS_DEBUG=* serverless offline
   ```

2. Check Lambda logs in CloudWatch after deployment

3. Test individual functions:
   ```bash
   serverless invoke local -f functionName --path event.json
   ```

## Best Practices

1. **Use Layers**: Share common dependencies via layers to reduce package size
2. **Optimize Packages**: Exclude unnecessary files and use slim packages
3. **Environment Variables**: Use stage-specific variables for different environments
4. **Error Handling**: Implement proper error handling in handlers
5. **Logging**: Use structured logging for better debugging
6. **Timeouts**: Set appropriate timeouts based on operation complexity
7. **Memory**: Allocate sufficient memory for operations (especially AI generation)

## Package Structure for Lambda

```
backend/
├── handlers/          # Lambda handlers
├── services/          # Service implementations
├── shared/            # Shared code and utilities
├── serverless.yml     # Serverless configuration
├── requirements.txt   # Python dependencies
└── package.json       # Node.js dependencies (for Serverless)
```

## Next Steps

1. Implement service routers in `services/` directories
2. Update handlers to import actual routers
3. Add function definitions to `serverless.yml`
4. Test locally with `serverless offline`
5. Deploy to development environment
6. Configure API Gateway custom domain (optional)
7. Set up CI/CD pipeline for automated deployments

