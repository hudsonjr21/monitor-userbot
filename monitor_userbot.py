import json
import os
import asyncio
import time
from telethon import TelegramClient, events
# A linha "from telethon.tl.custom import Button" foi removida pois não será usada
from telethon.errors.common import TypeNotFoundError
from keep_alive import keep_alive
from dotenv import load_dotenv
import re

# Carrega variáveis do arquivo .env
load_dotenv()

# Obtenha as credenciais da API do Telegram das variáveis de ambiente
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
print(f"API_ID: {API_ID}, API_HASH: {'*' * len(API_HASH)}")

# Nome da sessão do cliente
SESSION_NAME = 'monitorgrupos_userbot'

# Arquivo para salvar as palavras-chave
ARQUIVO_PALAVRAS = "palavras_userbot.json"

# ID do grupo para enviar notificações
DESTINATARIO_GRUPO = -1002649552991

# ID do usuário para notificações diretas (seu ID no Telegram)
DESTINATARIO_USUARIO = 6222930920

# Função para carregar palavras-chave
def carregar_palavras():
    try:
        if os.path.exists(ARQUIVO_PALAVRAS):
            with open(ARQUIVO_PALAVRAS, "r") as file:
                return json.load(file)
        else:
            return []
    except json.JSONDecodeError:
        print("Erro ao carregar o arquivo JSON. O arquivo será redefinido.")
        return []

# Função para salvar palavras-chave
def salvar_palavras(palavras):
    try:
        with open(ARQUIVO_PALAVRAS, "w") as file:
            json.dump(palavras, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar palavras no arquivo: {e}")

# Lista de palavras-chave
palavras_chave = carregar_palavras()

# Iniciar cliente do Telegram para Userbot
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def main():
    await client.connect()

    if not await client.is_user_authorized():
        print("Sessão não está autorizada. Por favor, faça a autenticação localmente.")
        await client.start()

    print("Sessão autenticada com sucesso!")

    # <--- MODIFICAÇÃO: Função /start volta a ser um menu de texto claro --->
    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        mensagem = (
            "🤖 **Bem-vindo ao Userbot de Filtro de Palavras!**\n\n"
            "Use os comandos abaixo para gerenciar o bot:\n\n"
            "🟢 `/add palavra1, palavra2`\n*Adiciona novas palavras-chave.*\n\n"
            "🟢 `/remover palavra1, palavra2`\n*Remove palavras-chave existentes.*\n\n"
            "🟢 `/ver`\n*Lista todas as palavras que estão sendo monitoradas.*\n\n"
            "📌 O bot monitora automaticamente todos os grupos e canais que você participa."
        )
        await event.respond(mensagem)

    # Função para /add continua igual
    @client.on(events.NewMessage(pattern='/add'))
    async def add_palavra(event):
        partes = event.message.message.strip().split(" ", 1)
        if len(partes) < 2 or not partes[1]:
            await event.respond(
                "⚠️ Por favor, forneça palavras para adicionar.\n"
                "💡 Uso: `/add palavra1, palavra2, palavra3`"
            )
            return
        novas_palavras = [p.strip().lower() for p in partes[1].split(",")]
        palavras_adicionadas = []
        for palavra in novas_palavras:
            if palavra and palavra not in palavras_chave:
                palavras_chave.append(palavra)
                palavras_adicionadas.append(palavra)
        salvar_palavras(palavras_chave)
        if palavras_adicionadas:
            await event.respond(f"✅ Palavras adicionadas com sucesso:\n{', '.join(palavras_adicionadas)}")
        else:
            await event.respond("⚠️ Nenhuma palavra nova foi adicionada.")

    # Função para /remover continua igual
    @client.on(events.NewMessage(pattern='/remover'))
    async def remover_palavra(event):
        partes = event.message.message.strip().split(" ", 1)
        if len(partes) < 2 or not partes[1]:
            await event.respond(
                "⚠️ Por favor, forneça palavras para remover.\n"
                "💡 Uso: `/remover palavra1, palavra2, palavra3`"
            )
            return
        palavras_para_remover = [p.strip().lower() for p in partes[1].split(",")]
        palavras_removidas = []
        for palavra in palavras_para_remover:
            if palavra in palavras_chave:
                palavras_chave.remove(palavra)
                palavras_removidas.append(palavra)
        salvar_palavras(palavras_chave)
        if palavras_removidas:
            await event.respond(f"✅ Palavras removidas com sucesso:\n{', '.join(palavras_removidas)}")
        else:
            await event.respond("⚠️ Nenhuma palavra foi encontrada para remover.")

    # Função para /ver continua igual
    @client.on(events.NewMessage(pattern='/ver'))
    async def verificar_palavras_comando(event):
        if not palavras_chave:
            await event.respond("🔍 Nenhuma palavra-chave foi configurada ainda.")
        else:
            lista_palavras = "🔑 **Palavras-chave configuradas:**\n\n- " + "\n- ".join(palavras_chave)
            await event.respond(lista_palavras)
            
    # O evento de CallbackQuery foi removido, pois não é mais necessário

    # Evento para monitorar mensagens (permanece igual)
    @client.on(events.NewMessage)
    async def monitorar_mensagens(event):
        try:
            if not event.message or not event.message.message:
                return
            texto = event.message.message.lower()
            for palavra in palavras_chave:
                padrao = r'\b' + re.escape(palavra) + r'\b'
                if re.search(padrao, texto):
                    mensagem_alerta = (
                        f"⚠️ Promoção de: '{palavra}'\n\n"
                        f"Mensagem: {event.message.message}\n\n"
                        f"Grupo: {event.chat.title if event.chat else 'Mensagem direta'}"
                    )
                    await client.send_message(DESTINATARIO_GRUPO, f"{mensagem_alerta} \n @Hudson_Jr21")
                    break
        except TypeNotFoundError as e:
            print(f"Erro ao processar mensagem: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")

    # Inicie o servidor HTTP
    keep_alive()

    # Conecta-se e aguarda desconexões
    print("Monitorando mensagens... Pressione Ctrl+C para sair.")
    await client.run_until_disconnected()

# Bloco de execução robusto (permanece igual)
if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Bot encerrado manualmente.")
            break
        except Exception as e:
            print(f"Ocorreu um erro inesperado que derrubou o bot: {e}")
            print("Tentando reiniciar em 30 segundos...")
            time.sleep(30)
