# Lambda Handlers

This directory contains Lambda handlers for serverless deployment. Each handler wraps a FastAPI router using Mangum to make it compatible with AWS Lambda and API Gateway.

## Handler Pattern

Each service should have its own handler file that follows this pattern:

```python
from fastapi import APIRouter
from handlers.base import LambdaHandler

# Create or import your service router
router = APIRouter(prefix="/your-prefix", tags=["your-tag"])

# Define your endpoints
@router.get("/")
async def list_items():
    return {"data": []}

# Create the Lambda handler instance
handler_instance = LambdaHandler(
    router=router,
    title="Your Service API",
    description="API endpoints for your service",
)

# Export the handler function for serverless.yml
handler = handler_instance
```

## Using Existing Service Routers

When your service routers are implemented, you can import them instead of creating placeholder routers:

```python
from services.document_service.router import router as document_router
from handlers.base import LambdaHandler

handler_instance = LambdaHandler(
    router=document_router,
    title="Document Service API",
    description="API endpoints for document management",
)

handler = handler_instance
```

## Handler Configuration

The `LambdaHandler` class accepts the following parameters:

- `router`: FastAPI router to wrap (required)
- `title`: Application title (default: "Demand Letter Generator API")
- `description`: Application description (default: "API endpoint for Demand Letter Generator")
- `version`: Application version (default: "1.0.0")
- `cors_origins`: List of allowed CORS origins (default: ["*"] for Lambda)

## Base Handler Utility

The `handlers/base.py` module provides:

1. **`create_lambda_app()`**: Creates a FastAPI application configured for Lambda with CORS middleware
2. **`create_handler()`**: Creates a Mangum handler instance
3. **`LambdaHandler` class**: Convenient wrapper that combines both

## Error Handling

The base handler includes error handling that:
- Logs errors with full stack traces
- Returns appropriate HTTP 500 responses
- Includes CORS headers in error responses

## Example: Document Handler

See `document_handler.py` for a complete example of a handler implementation.

## Adding New Handlers

1. Create a new file in `handlers/` directory (e.g., `handlers/your_service_handler.py`)
2. Import or create your FastAPI router
3. Create a `LambdaHandler` instance
4. Export the handler function
5. Add the function to `serverless.yml`:

```yaml
functions:
  yourService:
    handler: handlers.your_service_handler.handler
    events:
      - http:
          path: your-service/{proxy+}
          method: ANY
          cors: true
    layers:
      - { Ref: CommonDependenciesLambdaLayer }
```

## Testing Handlers Locally

Use `serverless-offline` to test handlers locally:

```bash
cd backend
serverless offline
```

This will start a local server that mimics API Gateway and Lambda behavior.

