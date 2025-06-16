from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "🔒 Bot online via HTTPS! | Criado por Kazinho"

def run():
    app.run(host='0.0.0.0', port=8080)  # OBRIGATÓRIO usar porta 8080 no Replit!

def keep_alive():
    t = Thread(target=run)
    t.start()