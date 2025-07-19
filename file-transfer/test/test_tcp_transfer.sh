#!/bin/bash

set -e

HOST="127.0.0.1"
PORT="8080"

GENERATED_FILE="test/generated_tcp_file.bin"
RECEIVED_FILE="test/received_tcp_file.bin"

# Kill any process using the port to avoid "Address already in use"
fuser -k $PORT/tcp || true

# Generate a test file with random content
dd if=/dev/urandom of=$GENERATED_FILE bs=1024 count=10 status=none

# Start TCP server in background
PYTHONPATH=$(pwd) HOST=$HOST PORT=$PORT python3 src/tcp/tcp_server.py $GENERATED_FILE &
SERVER_PID=$!
sleep 1  # wait for server to start

# Run TCP client to receive file
PYTHONPATH=$(pwd) HOST=$HOST PORT=$PORT python3 src/tcp/tcp_client.py $RECEIVED_FILE

# Stop the server (ignore error if process already exited)
kill $SERVER_PID 2>/dev/null || true

# Compare files and print result
if cmp -s "$GENERATED_FILE" "$RECEIVED_FILE"; then
    echo "✅ TCP test passed: files match"
else
    echo "❌ TCP test failed: files differ"
    exit 1
fi
