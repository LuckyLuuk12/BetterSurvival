from pathlib import Path
import argparse
import json
from PIL import Image


def is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


def find_textures_folder(start: Path) -> Path | None:
    for path in start.rglob("textures"):
        if path.is_dir():
            return path
    return None


def load_mcmeta(path: Path):
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        return {"__error__": str(e)}


def analyze_texture(texture: Path, check_interpolate: bool):
    try:
        with Image.open(texture) as img:
            width, height = img.size
    except Exception as e:
        print(f"Failed reading {texture}: {e}")
        return

    mcmeta = load_mcmeta(texture.with_suffix(texture.suffix + ".mcmeta"))

    animation = None
    interpolate = False
    frametime = None

    if isinstance(mcmeta, dict):
        animation = mcmeta.get("animation")

        if isinstance(animation, dict):
            interpolate = animation.get("interpolate", False)
            frametime = animation.get("frametime", 1)

    has_animation = isinstance(animation, dict)

    suspicious_reasons = []

    if width <= 1 or height <= 1:
        suspicious_reasons.append(
            f"dimensions {width}x{height} are too small (<=1)"
        )

    if has_animation:
        # Animated textures are usually vertical strips.
        if height % width != 0:
            suspicious_reasons.append(
                f"animated texture height {height} is not divisible by width {width}"
            )
        elif not is_power_of_two(width):
            suspicious_reasons.append(
                f"animation frame size {width}x{width} is not power-of-two"
            )
    else:
        if not (is_power_of_two(width) and is_power_of_two(height)):
            suspicious_reasons.append(
                f"dimensions {width}x{height} are not power-of-two"
            )

    if check_interpolate and interpolate:
        suspicious_reasons.append(
            f"animation interpolation enabled (frametime={frametime})"
        )

    if suspicious_reasons:
        print()
        print(texture)
        print(f"  Size: {width}x{height}")

        if mcmeta:
            print(f"  mcmeta: {mcmeta}")

        if has_animation:
            frame_count = height // width if height % width == 0 else "unknown"
            print(f"  Animation frames: {frame_count}")
            print(f"  Frame size: {width}x{width}")

        print("  Reasons:")
        for reason in suspicious_reasons:
            print(f"    - {reason}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-interpolate",
        action="store_true",
        help="Report textures with animation.interpolate=true",
    )
    args = parser.parse_args()

    root = Path(__file__).parent

    textures = find_textures_folder(root)

    if textures is None:
        print("Could not find textures folder.")
        return

    print(f"Scanning: {textures}")

    for folder_name in ("block", "item"):
        folder = textures / folder_name

        if not folder.exists():
            continue

        for texture in folder.rglob("*.png"):
            analyze_texture(texture, args.check_interpolate)


if __name__ == "__main__":
    main()