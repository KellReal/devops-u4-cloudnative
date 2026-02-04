from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
import requests
import time

resource = Resource.create({"service.name": "api-consumidor"})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint="http://jaeger-service:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

API_DADOS_URL = "http://api-dados-service:5000"

REQUEST_COUNT = Counter("api_consumidor_requests_total", "Total de requisições", ["endpoint"])
REQUEST_LATENCY = Histogram("api_consumidor_request_latency_seconds", "Latência das requisições", ["endpoint"])

@app.route("/")
def home():
    REQUEST_COUNT.labels(endpoint="/").inc()
    return jsonify({"servico": "api-consumidor", "status": "ativo"})

@app.route("/produtos")
def produtos():
    start = time.time()
    REQUEST_COUNT.labels(endpoint="/produtos").inc()
    try:
        resp = requests.get(f"{API_DADOS_URL}/dados", timeout=5)
        dados = resp.json()
        produtos = dados["produtos"]
        formatado = []
        for p in produtos:
            formatado.append(f"{p['nome']} - R${p['preco']:.2f}")
        response = jsonify({
            "origem": "api-dados",
            "produtos_formatados": formatado,
            "timestamp": time.time()
        })
    except Exception as e:
        response = jsonify({"erro": str(e)}), 500
    REQUEST_LATENCY.labels(endpoint="/produtos").observe(time.time() - start)
    return response

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)