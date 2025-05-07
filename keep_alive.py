from flask import Flask
from threading import Thread
import os  # Adicionar esta linha

app = Flask('')

@app.route('/')
def home():
    return "Bot está ativo 24/7!"

def run():
    # Use a variável de ambiente PORT ou 8080 como padrão
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()