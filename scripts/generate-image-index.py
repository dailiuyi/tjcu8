"""Generate the versioned image index consumed by pages/image-index.html."""

import json
from pathlib import Path

CONTRACT_VERSION = 1
SUPPORTED_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png"}

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
IMAGE_ROOT = REPOSITORY_ROOT / "image"
OUTPUT_PATH = REPOSITORY_ROOT / "pages" / "json" / "image_index.json"


def create_image_record(image_path):
    relative_path = image_path.relative_to(IMAGE_ROOT)
    image_id = relative_path.as_posix()
    album = relative_path.parts[0] if len(relative_path.parts) > 1 else "root"
    caption = image_path.name

    return {
        "id": image_id,
        "src": f"../image/{image_id}",
        "album": album,
        "caption": caption,
        "alt": f"{album}：{caption}",
    }


def generate_image_index():
    if not IMAGE_ROOT.is_dir():
        raise FileNotFoundError(f"Image directory does not exist: {IMAGE_ROOT}")

    image_paths = sorted(
        (
            path
            for path in IMAGE_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: (
            path.relative_to(IMAGE_ROOT).as_posix().casefold(),
            path.relative_to(IMAGE_ROOT).as_posix(),
        ),
    )
    payload = {
        "version": CONTRACT_VERSION,
        "images": [create_image_record(path) for path in image_paths],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as json_file:
        json.dump(payload, json_file, ensure_ascii=False, indent=4)
        json_file.write("\n")

    return len(payload["images"])


if __name__ == "__main__":
    image_count = generate_image_index()
    print(f"Generated {OUTPUT_PATH} with {image_count} images.")
