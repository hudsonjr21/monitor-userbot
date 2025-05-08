import json
import os
import asyncio
import re
import unidecode  # Corrigido: Importar biblioteca para remover acentos
from telethon import TelegramClient, events
from telethon.errors.common import TypeNotFoundError
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

# ID do grupo para enviar notificações
DESTINATARIO_GRUPO = -1002649552991  # Substitua pelo ID do grupo Alertas-Promocao

# ID do usuário para notificações diretas (seu ID no Telegram)
DESTINATARIO_USUARIO = 6222930920  # Substitua pelo seu User ID

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

# Iniciar cliente do Telegram para Userbot (sem bot_token)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def main():
    # Conectar o cliente e verificar autenticação
    await client.connect()

    if not await client.is_user_authorized():
        print("Sessão não está autorizada. Por favor, faça a autenticação localmente.")
        await client.start()  # Pedirá o número de telefone e o código de verificação localmente

    print("Sessão autenticada com sucesso!")

    # Evento para lidar com comandos de texto
    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        mensagem = (
            "🤖 **Bem-vindo ao Userbot de Filtro de Palavras!**\n\n"
            "Use os comandos abaixo para gerenciar palavras-chave e filtrar mensagens:\n"
            "🟢 `/add palavra1, palavra2` - Adiciona novas palavras-chave.\n"
            "🟢 `/remover palavra1, palavra2` - Remove palavras-chave.\n"
            "🟢 `/ver` - Lista todas as palavras configuradas.\n\n"
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

    @client.on(events.NewMessage(pattern='/ver'))
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
    try:
        if not event.message.message:
            return

        # Remove acentos e transforma em minúsculas
        texto = unidecode.unidecode(event.message.message).lower()

        for palavra in palavras_chave:
            # Remove acentos da palavra-chave
            palavra_normalizada = unidecode.unidecode(palavra).lower()
            
            # Usar regex para encontrar a palavra isolada
            padrao = r'\b' + re.escape(palavra_normalizada) + r'\b'
            if re.search(padrao, texto):
                mensagem_alerta = (
                    f"⚠️ Palavra-chave detectada: '{palavra}'\n\n"
                    f"Mensagem: {event.message.message}\n\n"
                    f"De: {event.chat.title if event.chat else 'Mensagem direta'}"
                )
                # Envia para o grupo
                await client.send_message(DESTINATARIO_GRUPO, f"@Hudson_Jr21 {mensagem_alerta}")
                # Envia notificação direta para o usuário
                await client.send_message(DESTINATARIO_USUARIO, mensagem_alerta)
                break
    except TypeNotFoundError as e:
        print(f"Erro ao processar mensagem: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

    # Inicie o servidor HTTP para manter o bot ativo
    keep_alive()

    # Conecta-se e aguarda desconexões
    print("Monitorando mensagens... Pressione Ctrl+C para sair.")
    await client.run_until_disconnected()

# Executa o loop principal
asyncio.run(main())