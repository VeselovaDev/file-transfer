import logging
import socket
import sys
from pathlib import Path
from typing import NoReturn

from src.config import BUFFER_SIZE, HOST, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def send_file(filepath: Path, conn: socket.socket) -> None:
    """Send the file to the client over the given connection."""
    with filepath.open("rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            conn.sendall(chunk)


def main() -> NoReturn:
    if len(sys.argv) != 2:
        logger.error("Usage: python src/tcp_server.py <file_to_serve>")
        sys.exit(1)

    filepath: Path = Path(sys.argv[1])
    if not filepath.exists():
        logger.error("File does not exist: %s", filepath)
        sys.exit(1)

    logger.info("Serving %s", filepath.resolve())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        logger.info("Listening on %s:%d...", HOST, PORT)

        conn, addr = server_sock.accept()
        with conn:
            logger.info("Connection from %s:%d", *addr)
            send_file(filepath, conn)
            logger.info("Finished sending to %s:%d", *addr)


if __name__ == "__main__":
    main()
