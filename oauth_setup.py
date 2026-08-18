"""
oauth_setup.py

Rode este script UMA VEZ, na sua máquina local, para autorizar o app
e obter o access_token do LinkedIn.

Como usar:
1. Preencha CLIENT_ID e CLIENT_SECRET abaixo (ou exporte como variáveis de ambiente)
2. Rode: python oauth_setup.py
3. Vai abrir o navegador pedindo pra você autorizar o app
4. Após autorizar, o token vai aparecer no terminal
5. Copie o access_token e salve como secret no GitHub (LINKEDIN_ACCESS_TOKEN)

O token dura ~60 dias (veja "Token time to live duration" no painel do LinkedIn).
Quando expirar, basta rodar este script de novo.
"""

import os
import webbrowser
import http.server
import urllib.parse
import requests

CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "COLE_SEU_CLIENT_ID_AQUI")
CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "COLE_SEU_CLIENT_SECRET_AQUI")
REDIRECT_URI = "http://localhost:8080/callback"
PORT = 8080

# Escopos necessários: openid+profile para identificar o usuário,
# w_member_social para poder publicar posts em nome dele.
SCOPES = "openid profile w_member_social"

AUTH_URL = (
    "https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={urllib.parse.quote(SCOPES)}"
)

TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

authorization_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            authorization_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<h2>Autorizado com sucesso! Pode fechar esta aba e voltar ao terminal.</h2>".encode("utf-8")
            )
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>Erro: código de autorização não encontrado.</h2>".encode("utf-8"))

    def log_message(self, format, *args):
        pass  # silencia logs padrão do servidor


def main():
    if "COLE_SEU" in CLIENT_ID or "COLE_SEU" in CLIENT_SECRET:
        print("⚠️  Preencha CLIENT_ID e CLIENT_SECRET no topo do arquivo, ou exporte:")
        print("    export LINKEDIN_CLIENT_ID=xxxx")
        print("    export LINKEDIN_CLIENT_SECRET=xxxx")
        return

    print("Abrindo o navegador para autorizar o app no LinkedIn...")
    webbrowser.open(AUTH_URL)

    server = http.server.HTTPServer(("localhost", PORT), CallbackHandler)
    print(f"Aguardando autorização em http://localhost:{PORT}/callback ...")
    server.handle_request()  # processa uma única requisição e para

    if not authorization_code:
        print("❌ Não recebemos o código de autorização. Tente novamente.")
        return

    print("✅ Código de autorização recebido. Trocando por access_token...")

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        print(f"❌ Erro ao obter token: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    access_token = data.get("access_token")
    expires_in = data.get("expires_in")

    print("\n" + "=" * 60)
    print("✅ ACCESS TOKEN OBTIDO COM SUCESSO")
    print("=" * 60)
    print(f"\nToken: {access_token}")
    print(f"Expira em: {expires_in} segundos (~{expires_in // 86400} dias)")
    print("\n📌 Próximo passo:")
    print("   Vá no seu repositório GitHub > Settings > Secrets and variables")
    print("   > Actions > New repository secret")
    print("   Nome: LINKEDIN_ACCESS_TOKEN")
    print(f"   Valor: {access_token}")
    print("=" * 60)


if __name__ == "__main__":
    main()
