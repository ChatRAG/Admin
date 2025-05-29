import os
import shutil
import zipfile
import boto3
from pathlib import Path

LAYER_NAME = "admin"
SOURCE_LIB_PATHS = [Path("venv/lib"), Path("cors")]
TEMP_LAYER_DIR = Path("python")
ZIP_PATH = "layer.zip"
RUNTIME = ["python3.9"]
DESCRIPTION = "Auto-updated Lambda Layer"


def prepare_layer_directory():
    if TEMP_LAYER_DIR.exists():
        shutil.rmtree(TEMP_LAYER_DIR)
    TEMP_LAYER_DIR.mkdir(parents=True)

    for SOURCE_LIB_PATH in SOURCE_LIB_PATHS:
        if not SOURCE_LIB_PATH.exists():
            raise FileNotFoundError(f"[!] Source directory '{SOURCE_LIB_PATH}' does not exist.")

        print("[*] Copying layer content...")
        shutil.copytree(SOURCE_LIB_PATH, TEMP_LAYER_DIR / SOURCE_LIB_PATH.name)


def zip_layer():
    if Path(ZIP_PATH).exists():
        os.remove(ZIP_PATH)

    print("[*] Zipping layer content...")
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(TEMP_LAYER_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ".")
                zipf.write(full_path, arcname=rel_path)
    print(f"[+] Created zip file: {ZIP_PATH}")


def publish_layer():
    client = boto3.client("lambda")
    with open(ZIP_PATH, "rb") as f:
        response = client.publish_layer_version(
            LayerName=LAYER_NAME,
            Description=DESCRIPTION,
            Content={"ZipFile": f.read()},
            CompatibleRuntimes=RUNTIME
        )
    print(f"[+] Published new version: {response['Version']}")
    print(f"[+] ARN: {response['LayerVersionArn']}")
    return response['Version']


def cleanup():
    print("[*] Cleaning up temporary files...")
    if TEMP_LAYER_DIR.exists():
        shutil.rmtree(TEMP_LAYER_DIR)
    if Path(ZIP_PATH).exists():
        os.remove(ZIP_PATH)
    print("[✓] Cleanup complete.")


def main():
    try:
        print("[*] Preparing layer directory...")
        prepare_layer_directory()

        print("[*] Zipping layer...")
        zip_layer()

        print("[*] Publishing new layer version...")
        version = publish_layer()

        print("[✓] Done. Published layer version:", version)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
