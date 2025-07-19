#!/bin/bash

# UDP test script

set -e

HOST="127.0.0.1"
PORT=8081
TEST_DIR="test"
FILE_TO_SERVE="$TEST_DIR/generated_udp_file.bin"
RECEIVED_FILE="$TEST_DIR/received_udp_file.bin"

# Generate a test file
echo "Creating test file..."
mkdir -p "$TEST_DIR"
head -c 1M </dev/urandom > "$FILE_TO_SERVE"

# Start UDP server in background
echo "Starting UDP server..."
HOST=$HOST PORT=$PORT PYTHONPATH=$(pwd) python3 src/udp/udp_server.py "$FILE_TO_SERVE" &
SERVER_PID=$!
sleep 1

# Run UDP client
echo "Running UDP client..."
HOST=$HOST PORT=$PORT PYTHONPATH=$(pwd) python3 src/udp/udp_client.py "$(basename "$FILE_TO_SERVE")" "$RECEIVED_FILE"

# Kill the server
kill $SERVER_PID

# Compare files
if cmp -s "$FILE_TO_SERVE" "$RECEIVED_FILE"; then
  echo "✅ UDP test passed"
  exit 0
else
  echo "❌ UDP test failed: files differ"
  exit 1
fi
