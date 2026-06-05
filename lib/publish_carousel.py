"""
publish_carousel.py — Publica um carrossel no Instagram via Meta Graph API.
Hospedagem das imagens: URLs raw.githubusercontent.com (reliable, free).
Credenciais: GitHub Secrets (INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ID, META_API_VERSION).
"""
import argparse, os, sys, time, requests
from pathlib import Path

IG_ID      = os.environ["INSTAGRAM_BUSINESS_ID"]
PAGE_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
API_V      = os.environ.get("META_API_VERSION", "v19.0")
BASE_URL   = f"https://graph.facebook.com/{API_V}"

# Repo URL base — usa GITHUB_REPOSITORY do ambiente Actions
REPO       = os.environ.get("GITHUB_REPOSITORY")  # ex.: lucastordino/juliska-instagram-bot
REF        = os.environ.get("GITHUB_REF_NAME", "main")
RAW_BASE   = f"https://raw.githubusercontent.com/{REPO}/{REF}" if REPO else None


def github_image_url(local_path: str) -> str:
    """Converte path local em URL raw.githubusercontent."""
    if not RAW_BASE:
        raise RuntimeError("GITHUB_REPOSITORY env não está set")
    # Normaliza: remove ./ inicial se houver
    rel = local_path.lstrip("./")
    return f"{RAW_BASE}/{rel}"


def wait_ready(container_id: str) -> bool:
    for i in range(24):
        resp = requests.get(f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": PAGE_TOKEN}, timeout=15)
        status = resp.json().get("status_code", "")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"Container ERROR: {resp.json()}")
        print(f"  [{i*5}s] status={status}")
        time.sleep(5)
    return False


def publish_carousel(image_paths: list, caption: str) -> str:
    print(f"\n→ Subindo {len(image_paths)} containers (children)...")
    media_ids = []
    for p in image_paths:
        url = github_image_url(p)
        print(f"  {p}  ←  {url}")
        resp = requests.post(f"{BASE_URL}/{IG_ID}/media", data={
            "access_token": PAGE_TOKEN,
            "image_url": url,
            "is_carousel_item": "true",
        }, timeout=60).json()
        if "id" not in resp:
            raise RuntimeError(f"Erro container: {resp}")
        media_ids.append(resp["id"])

    print("\n→ Montando carrossel...")
    carousel = requests.post(f"{BASE_URL}/{IG_ID}/media", data={
        "access_token": PAGE_TOKEN,
        "media_type": "CAROUSEL",
        "children": ",".join(media_ids),
        "caption": caption,
    }, timeout=30).json()
    if "id" not in carousel:
        raise RuntimeError(f"Erro carousel: {carousel}")

    print("\n→ Aguardando processamento...")
    if not wait_ready(carousel["id"]):
        raise RuntimeError("Timeout no processamento")

    print("\n→ Publicando...")
    pub = requests.post(f"{BASE_URL}/{IG_ID}/media_publish", data={
        "access_token": PAGE_TOKEN,
        "creation_id": carousel["id"],
    }, timeout=30).json()
    if "id" not in pub:
        raise RuntimeError(f"Erro publish: {pub}")
    return pub["id"]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--folder", required=True, help="ex.: posts/vila_mariana")
    p.add_argument("--caption-file", required=True, help="ex.: posts/vila_mariana/caption.txt")
    args = p.parse_args()

    folder = Path(args.folder)
    slides = sorted(folder.glob("slide_*.png"))
    if not slides:
        print(f"ERRO: nenhum slide_*.png em {folder}")
        sys.exit(1)
    if len(slides) > 10:
        print("ERRO: max 10 slides por carrossel.")
        sys.exit(1)

    caption = Path(args.caption_file).read_text(encoding="utf-8").strip()

    print(f"Carrossel: {len(slides)} slides · caption {len(caption)} chars")
    pid = publish_carousel([str(s) for s in slides], caption)
    print(f"\nOK · Post ID: {pid}")
