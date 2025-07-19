# File Transfer Project

This project implements simple file transfer utilities over both TCP and UDP protocols in Python. It includes server and client scripts for each protocol, along with Bash-based test scripts.

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/yourusername/file-transfer.git
cd file-transfer
```

### Install dependencies

This project uses the `uv` package manager. To install the required dependencies, run:

```bash
uv install
```

## Usage

### TCP Server

```bash
python src/tcp_server.py <file_to_serve>
```

### TCP Client

```bash
python src/tcp_client.py <filename> <destination_path>
```

### UDP Server

```bash
python src/udp_server.py <file_to_serve>
```

### UDP Client

```bash
python src/udp_client.py <filename> <destination_path>
```

## Running Tests

Test scripts for TCP and UDP transfers are provided as Bash scripts.

Make them executable (if not already):

```bash
chmod +x test/test_tcp_transfer.sh
chmod +x test/test_udp_transfer.sh
```

Run the tests with:

```bash
./test/test_tcp_transfer.sh
./test/test_udp_transfer.sh
```

Each script will start the server and client processes and verify file transfers.

## Configuration

Host and port are configured in `src/config.py`. The default host is `127.0.0.1`.
