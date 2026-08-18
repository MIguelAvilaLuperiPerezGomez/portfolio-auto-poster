"""
generate_post.py

Chama a API do Gemini (Google) para gerar o texto de um post de LinkedIn
a partir das informações de um Pull Request/commit do GitHub.

Recebe os dados via variáveis de ambiente (injetadas pelo workflow do GitHub Actions)
e imprime o texto gerado no stdout, para ser usado pelo próximo passo do workflow.
"""

import os
import sys

# Força UTF-8 na saída padrão, independente da code page do terminal
# (evita corrupção de acentos ao capturar a saída no PowerShell no Windows)
sys.stdout.reconfigure(encoding="utf-8")

from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

REPO_NAME = os.environ.get("REPO_NAME", "")
PR_TITLE = os.environ.get("PR_TITLE", "")
PR_BODY = os.environ.get("PR_BODY", "")
COMMIT_MESSAGES = os.environ.get("COMMIT_MESSAGES", "")
CHANGED_FILES = os.environ.get("CHANGED_FILES", "")
REPO_URL = os.environ.get("REPO_URL", "")

SYSTEM_PROMPT = """\
Você escreve posts de LinkedIn para um estudante de Análise e Desenvolvimento \
de Sistemas que está construindo portfólio e buscando vaga de estágio em \
desenvolvimento de software.

Regras do post:
- Tom profissional, direto, em primeira pessoa, em português do Brasil.
- Sem emojis.
- Sem hashtags em excesso (no máximo 3, relevantes).
- Não invente funcionalidades ou tecnologias que não estão nas informações fornecidas.
- Foque no que foi aprendido/resolvido, não só "o que é o código".
- Tamanho: entre 500 e 1200 caracteres.
- Não use markdown (é texto puro para colar direto no LinkedIn).
- Termine com uma linha convidando para ver o repositório (sem inventar link se não for fornecido).
- Escreva tambem sobre oque foi aprendido no codigo.
- Nao fale  focando na melhoria do arquivo README.md. ou coisas relacionadas.
"""

USER_PROMPT = f"""\
Gere um post de LinkedIn anunciando esta atualização de projeto:

Repositório: {REPO_NAME}
URL: {REPO_URL}
Título do Pull Request: {PR_TITLE}
Descrição do PR: {PR_BODY}
Mensagens de commit incluídas:
{COMMIT_MESSAGES}
Arquivos alterados (resumo):
{CHANGED_FILES}
"""


def main():
    if not GEMINI_API_KEY:
        print("ERRO: variável GEMINI_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=USER_PROMPT,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2000,
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )

    post_text = response.text.strip()

    # Imprime só o texto puro no stdout, para o workflow capturar
    print(post_text)


if __name__ == "__main__":
    main()
