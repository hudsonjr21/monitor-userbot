import json
import os
import asyncio
from telethon import TelegramClient, events, Button
from keep_alive import keep_alive
from dotenv import load_dotenv  # Para carregar variáveis do .env

# Carrega variáveis do arquivo .env
load_dotenv()

# Obtenha as credenciais da API do Telegram das variáveis de ambiente
API_ID = int(os.getenv("API_ID"))  # Certifique-se de que o API_ID seja um número inteiro
API_HASH = os.getenv("API_HASH")
print(f"API_ID: {API_ID}, API_HASH: {API_HASH}")
# Nome da sessão do cliente
SESSION_NAME = 'monitorgrupos_userbot'

# Arquivo para salvar as palavras-chave
ARQUIVO_PALAVRAS = "palavras_userbot.json"

# Função para carregar palavras-chave
def carregar_palavras():
    try:
        with open(ARQUIVO_PALAVRAS, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Função para salvar palavras-chave
def salvar_palavras(palavras):
    with open(ARQUIVO_PALAVRAS, "w") as file:
        json.dump(palavras, file, ensure_ascii=False, indent=4)

# Lista de palavras-chave
palavras_chave = carregar_palavras()

# Iniciar cliente do Telegram para Userbot (sem bot_token)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def main():
    # Conectar o cliente e verificar autenticação
    await client.connect()

    if not await client.is_user_authorized():
        print("Sessão não está autorizada. Por favor, faça a autenticação localmente.")
        await client.start()  # Pedirá o número de telefone e o código de verificação localmente

    print("Sessão autenticada com sucesso!")

    # Menu principal
    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        buttons = [
            [Button.inline("➕ Adicionar Palavras", b"add_palavras")],
            [Button.inline("❌ Remover Palavras", b"remover_palavras")],
            [Button.inline("🔍 Ver Palavras Configuradas", b"ver_palavras")],
        ]
        mensagem = (
            "🤖 **Bem-vindo ao Userbot de Filtro de Palavras!**\n\n"
            "Escolha uma das opções abaixo para gerenciar suas palavras-chave:"
        )
        await event.respond(mensagem, buttons=buttons)

    # Lidando com botões inline
    @client.on(events.CallbackQuery)
    async def callback(event):
        if event.data == b"add_palavras":
            await event.respond(
                "Envie as palavras que deseja adicionar, separadas por vírgula.\n\n💡 Exemplo: `palavra1, palavra2, palavra3`"
            )
        elif event.data == b"remover_palavras":
            await event.respond(
                "Envie as palavras que deseja remover, separadas por vírgula.\n\n💡 Exemplo: `palavra1, palavra2, palavra3`"
            )
        elif event.data == b"ver_palavras":
            if not palavras_chave:
                await event.respond("🔍 Nenhuma palavra-chave foi configurada ainda.")
            else:
                await event.respond(
                    "🔑 Palavras-chave configuradas:\n" + "\n".join(palavras_chave)
                )

    # Evento para adicionar palavras
    @client.on(events.NewMessage)
    async def add_palavra(event):
        if event.text.startswith("/add "):
            novas_palavras = [
                p.strip().lower()
                for p in event.text.split(" ", 1)[-1].split(",")
            ]
            palavras_adicionadas = []
            for palavra in novas_palavras:
                if palavra and palavra not in palavras_chave:
                    palavras_chave.append(palavra)
                    palavras_adicionadas.append(palavra)

            salvar_palavras(palavras_chave)

            if palavras_adicionadas:
                await event.respond(
                    f"✅ Palavras adicionadas com sucesso:\n{', '.join(palavras_adicionadas)}"
                )
            else:
                await event.respond("⚠️ Nenhuma palavra nova foi adicionada.")

    # Evento para remover palavras
    @client.on(events.NewMessage)
    async def remover_palavra(event):
        if event.text.startswith("/remover "):
            palavras_para_remover = [
                p.strip().lower()
                for p in event.text.split(" ", 1)[-1].split(",")
            ]
            palavras_removidas = []
            for palavra in palavras_para_remover:
                if palavra in palavras_chave:
                    palavras_chave.remove(palavra)
                    palavras_removidas.append(palavra)

            salvar_palavras(palavras_chave)

            if palavras_removidas:
                await event.respond(
                    f"✅ Palavras removidas com sucesso:\n{', '.join(palavras_removidas)}"
                )
            else:
                await event.respond("⚠️ Nenhuma palavra foi encontrada para remover.")

    # Evento para monitorar mensagens
    @client.on(events.NewMessage)
    async def monitorar_mensagens(event):
        if not event.message.message:
            return

        texto = event.message.message.lower()
        for palavra in palavras_chave:
            if palavra in texto:
                await client.send_message(
                    'me',
                    f"⚠️ Palavra-chave detectada: '{palavra}'\n\nMensagem: {event.message.message}\n\nDe: {event.chat.title if event.chat else 'Mensagem direta'}"
                )
                break

    # Inicie o servidor HTTP para manter o bot ativo
    keep_alive()

    # Conecta-se e aguarda desconexões
    print("Monitorando mensagens... Pressione Ctrl+C para sair.")
    await client.run_until_disconnected()

# Executa o loop principal
asyncio.run(main())