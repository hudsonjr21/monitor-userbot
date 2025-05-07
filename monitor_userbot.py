import json
import os
from telethon import TelegramClient, events
from keep_alive import keep_alive 

# Obtenha as credenciais da API do Telegram das variáveis de ambiente
API_ID = int(os.getenv("API_ID"))  # Certifique-se de que o API_ID seja um número inteiro
API_HASH = os.getenv("API_HASH")

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

# Evento para lidar com comandos de texto
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    mensagem = (
        "🤖 **Bem-vindo ao Userbot de Filtro de Palavras!**\n\n"
        "Use os comandos abaixo para gerenciar palavras-chave e filtrar mensagens:\n"
        "🟢 `/add palavra1, palavra2` - Adiciona novas palavras-chave.\n"
        "🟢 `/remover palavra1, palavra2` - Remove palavras-chave.\n"
        "🟢 `/verificarpalavras` - Lista todas as palavras configuradas.\n\n"
        "📌 O bot monitora mensagens automaticamente em todos os grupos e canais que você participa."
    )
    await event.respond(mensagem)

@client.on(events.NewMessage(pattern='/add'))
async def add_palavra(event):
    if not event.message.message.strip().split(" ", 1)[-1]:
        await event.respond(
            "⚠️ Por favor, forneça palavras para adicionar.\n"
            "💡 Uso: `/add palavra1, palavra2, palavra3`"
        )
        return

    novas_palavras = [
        p.strip().lower()
        for p in event.message.message.split(" ", 1)[-1].split(",")
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

@client.on(events.NewMessage(pattern='/remover'))
async def remover_palavra(event):
    if not event.message.message.strip().split(" ", 1)[-1]:
        await event.respond(
            "⚠️ Por favor, forneça palavras para remover.\n"
            "💡 Uso: `/remover palavra1, palavra2, palavra3`"
        )
        return

    palavras_para_remover = [
        p.strip().lower()
        for p in event.message.message.split(" ", 1)[-1].split(",")
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

@client.on(events.NewMessage(pattern='/verificarpalavras'))
async def verificar_palavras(event):
    if not palavras_chave:
        await event.respond("🔍 Nenhuma palavra-chave foi configurada ainda.")
    else:
        await event.respond(
            "🔑 Palavras-chave configuradas:\n" + "\n".join(palavras_chave)
        )

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

# Conectar e iniciar o cliente
print("Monitorando mensagens... Pressione Ctrl+C para sair.")
client.start()
client.run_until_disconnected()