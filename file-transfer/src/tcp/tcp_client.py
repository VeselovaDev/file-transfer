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


def receive_file(dest_path: Path) -> None:
    """Receive a file from the server and save it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        with dest_path.open("wb") as f:
            while chunk := sock.recv(BUFFER_SIZE):
                if not chunk:
                    break
                f.write(chunk)


def main() -> NoReturn:
    if len(sys.argv) != 2:
        logger.error("Usage: python src/tcp_client.py <destination_file>")
        sys.exit(1)

    dest_path: Path = Path(sys.argv[1])
    logger.info("Downloading to %s", dest_path.resolve())
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    receive_file(dest_path)
    logger.info("Download complete.")


if __name__ == "__main__":
    main()
