import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, unquote
from urllib.request import Request, urlopen
from html.parser import HTMLParser


class LinkParser(HTMLParser):
    """Extract links from an HTML directory listing."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.links.append(value)


def get_png_files(server_url):
    """Fetch the directory listing and return PNG file URLs."""
    request = Request(
        server_url,
        headers={"User-Agent": "PNG-Downloader/1.0"}
    )

    try:
        with urlopen(request, timeout=10) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"ERROR: Could not connect to {server_url}")
        print(f"       {e}")
        sys.exit(1)

    parser = LinkParser()
    parser.feed(html)

    png_files = []

    for link in parser.links:
        # Ignore parent-directory links and directories.
        if link.endswith("/"):
            continue

        filename = unquote(link.split("?")[0].split("#")[0])

        # Only accept .png files, case-insensitively.
        if filename.lower().endswith(".png"):
            png_files.append(urljoin(server_url, link))

    return png_files


def download_file(url, destination):
    """Download a single file."""
    filename = unquote(url.split("/")[-1].split("?")[0])
    output_path = destination / filename

    request = Request(
        url,
        headers={"User-Agent": "PNG-Downloader/1.0"}
    )

    try:
        with urlopen(request, timeout=30) as response:
            total_size = response.headers.get("Content-Length")

            if total_size is not None:
                total_size = int(total_size)

            downloaded = 0

            with open(output_path, "wb") as file:
                while True:
                    chunk = response.read(1024 * 1024)

                    if not chunk:
                        break

                    file.write(chunk)
                    downloaded += len(chunk)

                    if total_size:
                        percent = downloaded * 100 / total_size
                        print(
                            f"\r    {filename}: "
                            f"{percent:6.2f}% "
                            f"({downloaded / 1024 / 1024:.2f} MB)",
                            end="",
                            flush=True
                        )
                    else:
                        print(
                            f"\r    {filename}: "
                            f"{downloaded / 1024 / 1024:.2f} MB",
                            end="",
                            flush=True
                        )

            print()

        return True

    except Exception as e:
        print(f"\n    ERROR downloading {filename}: {e}")

        # Remove partially downloaded file.
        if output_path.exists():
            try:
                output_path.unlink()
            except OSError:
                pass

        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download all PNG files from a Python HTTP server."
    )

    parser.add_argument(
        "--directory",
        required=True,
        help="Local directory where PNG files should be saved."
    )

    parser.add_argument(
        "--ip",
        required=True,
        help="IP address of the virtual machine."
    )

    parser.add_argument(
        "--port",
        required=True,
        type=int,
        help="Port of the Python HTTP server."
    )

    args = parser.parse_args()

    destination = Path(args.directory).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)

    server_url = f"http://{args.ip}:{args.port}/"

    print(f"Server:     {server_url}")
    print(f"Destination: {destination}")
    print()
    print("Finding PNG files...")

    png_files = get_png_files(server_url)

    if not png_files:
        print("No PNG files were found.")
        return

    print(f"Found {len(png_files)} PNG file(s).")
    print()

    successful = 0
    failed = 0

    for i, url in enumerate(png_files, start=1):
        filename = unquote(url.split("/")[-1].split("?")[0])

        print(f"[{i}/{len(png_files)}] Downloading {filename}")

        if download_file(url, destination):
            successful += 1
        else:
            failed += 1

    print()
    print("Download complete.")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Saved to:   {destination}")


if __name__ == "__main__":
    main()