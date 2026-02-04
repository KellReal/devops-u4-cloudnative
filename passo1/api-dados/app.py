from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
import time

resource = Resource.create({"service.name": "api-dados"})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint="http://jaeger-service:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

REQUEST_COUNT = Counter("api_dados_requests_total", "Total de requisições", ["endpoint"])
REQUEST_LATENCY = Histogram("api_dados_request_latency_seconds", "Latência das requisições", ["endpoint"])

@app.route("/")
def home():
    REQUEST_COUNT.labels(endpoint="/").inc()
    return jsonify({"servico": "api-dados", "status": "ativo"})

@app.route("/dados")
def dados():
    start = time.time()
    REQUEST_COUNT.labels(endpoint="/dados").inc()
    response = jsonify({
        "produtos": [
            {"id": 1, "nome": "Notebook", "preco": 3500},
            {"id": 2, "nome": "Mouse", "preco": 80},
            {"id": 3, "nome": "Teclado", "preco": 150}
        ],
        "timestamp": time.time()
    })
    REQUEST_LATENCY.labels(endpoint="/dados").observe(time.time() - start)
    return response

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)