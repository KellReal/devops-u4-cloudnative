from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

API_DADOS_URL = "http://api-dados-service:5000"

@app.route("/")
def home():
    return jsonify({"servico": "api-consumidor", "status": "ativo"})

@app.route("/produtos")
def produtos():
    try:
        resp = requests.get(f"{API_DADOS_URL}/dados", timeout=5)
        dados = resp.json()
        produtos = dados["produtos"]
        formatado = []
        for p in produtos:
            formatado.append(f"{p['nome']} - R${p['preco']:.2f}")
        return jsonify({
            "origem": "api-dados",
            "produtos_formatados": formatado,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)