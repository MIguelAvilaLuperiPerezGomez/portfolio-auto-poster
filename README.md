# Portfolio Auto Poster

Ao mergear um Pull Request na branch `main`, este projeto:
1. Coleta informações do PR (título, descrição, arquivos alterados)
2. Gera um texto de post usando a API do Gemini (Google)
3. Publica automaticamente no seu perfil pessoal do LinkedIn

## Setup (fazer uma única vez)

### 1. Instalar dependências localmente

```bash
pip install -r requirements.txt
```

### 2. Obter o access token do LinkedIn

```bash
export LINKEDIN_CLIENT_ID=seu_client_id
export LINKEDIN_CLIENT_SECRET=seu_client_secret
python oauth_setup.py
```

Isso vai abrir o navegador, pedir pra você autorizar o app, e no final imprimir
o `access_token` no terminal. Copie esse valor.

> ⚠️ O token expira em ~60 dias. Quando expirar, rode `oauth_setup.py` de novo
> e atualize o secret no GitHub.

### 3. Configurar os Secrets no GitHub

No repositório: **Settings → Secrets and variables → Actions → New repository secret**

Adicione:
- `GEMINI_API_KEY` — sua chave da API do Gemini (obtida em https://aistudio.google.com/apikey)
- `LINKEDIN_ACCESS_TOKEN` — o token obtido no passo 2

### 4. Pronto

A partir de agora, todo merge de PR na `main` vai gerar e publicar um post
automaticamente. O workflow está em `.github/workflows/post-on-merge.yml`.

## Estrutura do projeto

```
.
├── oauth_setup.py              # roda 1x localmente, obtém o access token
├── generate_post.py            # gera o texto via API do Claude
├── post_linkedin.py            # publica no LinkedIn
├── requirements.txt
└── .github/workflows/
    └── post-on-merge.yml       # workflow que orquestra tudo
```

## Testando localmente antes de automatizar

```bash
export GEMINI_API_KEY=sua_chave
export REPO_NAME="usuario/repo"
export REPO_URL="https://github.com/usuario/repo"
export PR_TITLE="Adiciona sistema de autenticação JWT"
export PR_BODY="Implementa login com JWT e refresh token"
export COMMIT_MESSAGES="feat: add JWT auth"
export CHANGED_FILES="auth.py, models.py"

python generate_post.py
```

Isso imprime o texto gerado sem publicar nada — bom para calibrar o prompt
em `generate_post.py` antes de deixar automático.
