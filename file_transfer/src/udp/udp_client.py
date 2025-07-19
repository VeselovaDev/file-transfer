import logging
import socket
import sys
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

SEQ_FORMAT = "!I"
ACK_MSG = b"ACK"


def send_ack(sock: socket.socket, addr: tuple, seq_num: int) -> None:
    """Send an ACK with the given sequence number."""
    ack_packet = ACK_MSG + struct.pack(SEQ_FORMAT, seq_num)
    sock.sendto(ack_packet, addr)


def receive_file(
    filename: str, destination: Path, sock: socket.socket, server_addr: tuple
) -> None:
    logger.info("Requesting file '%s' from server %s:%d", filename, *server_addr)
    sock.sendto(filename.encode(), server_addr)

    expected_seq = 0
    with destination.open("wb") as f:
        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                logger.error("Timeout waiting for packet %d", expected_seq)
                sys.exit(1)

            if addr != server_addr:
                logger.warning("Ignoring packet from unknown sender %s", addr)
                continue

            header_size = struct.calcsize(SEQ_FORMAT + "?")
            if len(data) < header_size:
                logger.warning("Received invalid packet (too small)")
                continue

            seq_num, eof = struct.unpack(SEQ_FORMAT + "?", data[:header_size])
            payload = data[header_size:]

            if seq_num == expected_seq:
                if payload:
                    f.write(payload)
                send_ack(sock, addr, seq_num)
                expected_seq += 1
                if eof:
                    logger.info("Received EOF, file transfer complete")
                    break
            else:
                # Duplicate or out-of-order packet; resend ACK for last received seq-1
                send_ack(sock, addr, expected_seq - 1)

    logger.info("File saved to %s", destination)


def main() -> None:
    if len(sys.argv) != 3:
        logger.error("Usage: python src/udp_client.py <filename> <destination_path>")
        sys.exit(1)

    filename = sys.argv[1]
    destination = Path(sys.argv[2])

    host = os.getenv("HOST", HOST)
    port = int(os.getenv("PORT", PORT))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)
        try:
            receive_file(filename, destination, sock, (host, port))
        except socket.timeout:
            logger.error("Timeout: no response from server")
            sys.exit(1)

    return


if __name__ == "__main__":
    main()
