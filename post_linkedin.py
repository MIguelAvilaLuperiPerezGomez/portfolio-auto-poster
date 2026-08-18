"""
post_linkedin.py

Publica um texto no LinkedIn (perfil pessoal) usando a API oficial (Posts API),
com o access_token obtido via oauth_setup.py.

Variáveis de ambiente esperadas:
- LINKEDIN_ACCESS_TOKEN: token obtido no oauth_setup.py
- POST_TEXT: texto do post a publicar
"""

import os
import sys

# Garante leitura/escrita em UTF-8, independente da code page do terminal
sys.stdout.reconfigure(encoding="utf-8")

import requests

ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
POST_TEXT = os.environ.get("POST_TEXT", "").strip()

USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
POSTS_URL = "https://api.linkedin.com/rest/posts"
LINKEDIN_VERSION = "202601"  # versão mensal exigida pela API — ajuste conforme necessário


def get_author_urn():
    """Busca o identificador (URN) do usuário autenticado a partir do token."""
    response = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    response.raise_for_status()
    data = response.json()
    subject_id = data["sub"]
    return f"urn:li:person:{subject_id}"


def publish_post(author_urn, text):
    payload = {
        "author": author_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": LINKEDIN_VERSION,
    }

    response = requests.post(POSTS_URL, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        print(f"❌ Erro ao publicar: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)

    post_id = response.headers.get("x-restli-id", "desconhecido")
    print(f"✅ Post publicado com sucesso! ID: {post_id}")


def main():
    if not ACCESS_TOKEN:
        print("ERRO: LINKEDIN_ACCESS_TOKEN não definido.", file=sys.stderr)
        sys.exit(1)

    if not POST_TEXT:
        print("ERRO: POST_TEXT vazio — nada para publicar.", file=sys.stderr)
        sys.exit(1)

    author_urn = get_author_urn()
    publish_post(author_urn, POST_TEXT)


if __name__ == "__main__":
    main()