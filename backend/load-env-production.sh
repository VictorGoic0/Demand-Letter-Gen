#!/bin/bash

# Helper script to load .env.production and export variables for serverless deployment
# Usage: source load-env-production.sh (or . load-env-production.sh)

if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found"
    echo "   Please create backend/.env.production with production credentials"
    return 1 2>/dev/null || exit 1
fi

echo "📝 Loading environment variables from .env.production..."

# Export all variables from .env.production (excluding comments and empty lines)
export $(cat .env.production | grep -v '^#' | grep -v '^$' | xargs)

echo "✅ Environment variables loaded"
echo ""
echo "You can now run:"
echo "  serverless deploy --stage prod"
echo ""
echo "Or use the npm script:"
echo "  npm run deploy:prod"

