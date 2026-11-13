"""Coolest Art Entry: Mending the Crescent Moon with Starlight.

SPDX-License-Identifier: MIT
Deterministic entry script that writes the 1024x1024 PNG artwork
to the configured output directory (/output/entry.png by default).
"""

import base64
import hashlib
import os
from pathlib import Path
import struct
from art_data import ART_PNG_B64

DEFAULT_OUTPUT_DIR = "/output"
ENTRY_FILENAME = "entry.png"
EXPECTED_SIZE = (1024, 1024)
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MiB limit
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def get_output_dir() -> Path:
    """Resolve and create the target output directory."""
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def verify_image_bytes(data: bytes) -> bytes:
    """Verify the generated entry image satisfies size bounds, has PNG header, and expected dimensions."""
    if len(data) > MAX_FILE_SIZE:
        raise ValueError(
            f"Image file size {len(data)} bytes exceeds maximum allowed limit of {MAX_FILE_SIZE} bytes (1 MiB)"
        )

    if not data.startswith(PNG_MAGIC):
        raise ValueError("Image data does not have a valid PNG signature header.")

    if len(data) < 24:
        raise ValueError("Image data is too small to contain valid PNG header and IHDR chunk.")

    if data[12:16] != b"IHDR":
        raise ValueError("First chunk is not IHDR.")

    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != EXPECTED_SIZE:
        raise ValueError(f"Unexpected image size {(width, height)}, expected {EXPECTED_SIZE}")

    return data


def export_entry(dst: Path) -> str:
    """Decode and deterministically write the entry image bytes to dst."""
    data = base64.b64decode(ART_PNG_B64.strip())
    verify_image_bytes(data)
    dst.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    out_dir = get_output_dir()
    dst = out_dir / ENTRY_FILENAME
    digest = export_entry(dst)
    print(f"Wrote {dst} (sha256={digest})")


if __name__ == "__main__":
    main()
