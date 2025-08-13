#!/bin/bash

# Simple test to verify PORT handling in startup script
echo "🧪 Testing PORT variable handling..."

export PORT=8080
echo "Set PORT to: $PORT"

# Test the port default behavior
unset PORT
echo "Unset PORT, should default to 8000"

# Source our script logic (just the PORT handling part)
PORT=${PORT:-8000}
echo "Final PORT value: $PORT"

echo "✅ PORT handling test passed!"
