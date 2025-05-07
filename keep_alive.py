from flask import Flask
from threading import Thread
import os
import asyncio
from monitor_userbot import main  # Importa o loop principal do bot

app = Flask('')

@app.route('/')
def home():
    return "Bot está ativo 24/7!"

def run():
    # Use a variável de ambiente PORT ou 8080 como padrão
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # Inicia o servidor Flask
    t = Thread(target=run)
    t.start()

# Inicia o bot do Telethon
if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())  # Executa o loop principal do bot