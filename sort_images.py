#!/usr/bin/env python3

import argparse
import re
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Move PNG screenshots into an images directory and update README.md references."
    )
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help="Path to the HTB machine directory"
    )

    args = parser.parse_args()

    machine_dir = Path(args.directory).resolve()

    if not machine_dir.is_dir():
        print(f"[!] Directory does not exist: {machine_dir}")
        return 1

    readme = machine_dir / "README.md"
    images_dir = machine_dir / "images"

    # Create images directory if it doesn't exist
    images_dir.mkdir(exist_ok=True)

    # Find PNG files directly inside the machine directory
    png_files = list(machine_dir.glob("*.png"))

    if not png_files:
        print("[*] No PNG files found.")
    else:
        print(f"[*] Found {len(png_files)} PNG file(s).")

    # Move PNG files into images/
    for png_file in png_files:
        destination = images_dir / png_file.name

        # Avoid accidentally overwriting an existing file
        if destination.exists():
            print(f"[!] Skipping {png_file.name}: destination already exists.")
            continue

        shutil.move(str(png_file), str(destination))
        print(f"[+] Moved: {png_file.name} -> images/{png_file.name}")

    # Update README.md
    if not readme.exists():
        print("[!] README.md not found. PNG files were still moved.")
        return 0

    content = readme.read_text(encoding="utf-8")

    # Replace:
    #   ![](image.png)
    #   ![](image-1.png)
    #   ![](image-2.png)
    #
    # with:
    #   ![](images/image.png)
    #   ![](images/image-1.png)
    #   ![](images/image-2.png)
    #
    # Only modify references that don't already contain a path.
    pattern = re.compile(
        r'(!\[\]\()((?:image(?:-\d+)?)\.png)(\))'
    )

    updated_content, replacements = pattern.subn(
        r'\1images/\2\3',
        content
    )

    if replacements:
        readme.write_text(updated_content, encoding="utf-8")
        print(f"[+] Updated {replacements} image reference(s) in README.md")
    else:
        print("[*] No image references needed updating.")

    print("[+] Done.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())