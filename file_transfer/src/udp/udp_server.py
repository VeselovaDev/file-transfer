import logging
import socket
import sys
import time
from pathlib import Path
from typing import NoReturn
import os
import struct

from src.config import BUFFER_SIZE, HOST, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SEQ_FORMAT = "!I"  # 4-byte unsigned int for sequence number
ACK_MSG = b"ACK"

PACKET_TIMEOUT = 0.5  # seconds
MAX_RETRIES = 5


def make_packet(seq_num: int, data: bytes, eof: bool = False) -> bytes:
    """Create a packet with sequence number, EOF flag, and data."""
    header = struct.pack(SEQ_FORMAT + "?", seq_num, eof)
    return header + data


def parse_packet(packet: bytes) -> tuple[int, bool, bytes]:
    """Extract sequence number, EOF flag, and data from packet."""
    header_size = struct.calcsize(SEQ_FORMAT + "?")
    seq_num, eof = struct.unpack(SEQ_FORMAT + "?", packet[:header_size])
    data = packet[header_size:]
    return seq_num, eof, data


def send_file(filepath: Path, addr: tuple, sock: socket.socket) -> None:
    logger.info("Sending file %s to %s:%d", filepath, *addr)
    with filepath.open("rb") as f:
        seq_num = 0
        while True:
            chunk = f.read(BUFFER_SIZE - struct.calcsize(SEQ_FORMAT + "?"))
            eof = False
            if not chunk:
                eof = True
                packet = make_packet(seq_num, b"", eof)
            else:
                packet = make_packet(seq_num, chunk, eof)

            retries = 0
            while retries < MAX_RETRIES:
                sock.sendto(packet, addr)
                try:
                    sock.settimeout(PACKET_TIMEOUT)
                    data, sender = sock.recvfrom(1024)
                    if data == ACK_MSG + struct.pack(SEQ_FORMAT, seq_num):
                        # Correct ACK received
                        break
                except socket.timeout:
                    retries += 1
                    logger.debug(f"Timeout waiting for ACK {seq_num}, retry {retries}")
            else:
                logger.error(
                    f"Failed to receive ACK for packet {seq_num} after {MAX_RETRIES} retries"
                )
                return

            if eof:
                break
            seq_num += 1
    logger.info("Finished sending to %s:%d", *addr)


def main() -> NoReturn:
    host = os.getenv("HOST", HOST)
    port = int(os.getenv("PORT", PORT))

    if len(sys.argv) != 2:
        logger.error("Usage: python src/udp_server.py <file_to_serve>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        logger.error("File does not exist: %s", filepath)
        sys.exit(1)

    logger.info("Serving %s on UDP %s:%d", filepath.resolve(), host, port)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if data == b"ping":
                sock.sendto(b"pong", addr)
                continue

            requested_file = data.decode()
            logger.info("Request for file '%s' from %s:%d", requested_file, *addr)
            if requested_file == filepath.name:
                send_file(filepath, addr, sock)
            else:
                logger.warning("Requested unknown file '%s'", requested_file)


if __name__ == "__main__":
    main()
