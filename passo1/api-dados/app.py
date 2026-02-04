from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"servico": "api-dados", "status": "ativo"})

@app.route("/dados")
def dados():
    return jsonify({
        "produtos": [
            {"id": 1, "nome": "Notebook", "preco": 3500},
            {"id": 2, "nome": "Mouse", "preco": 80},
            {"id": 3, "nome": "Teclado", "preco": 150}
        ],
        "timestamp": time.time()
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```
