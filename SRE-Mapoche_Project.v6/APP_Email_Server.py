from flask import Flask, Response
from prometheus_client import start_http_server, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random
import time
import threading

# -------------------------------
# OpenTelemetry imports
# -------------------------------
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Configure OpenTelemetry Tracer
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# -------------------------------
# Prometheus metrics
# -------------------------------
emails_sent = Gauge('emails_sent_total', 'Total de correos enviados')
emails_failed = Gauge('emails_failed_total', 'Total de correos fallidos')
apps_access = Gauge('apps_access_total', 'Total de accesos a aplicaciones')
apps_errors = Gauge('apps_errors_total', 'Total de errores en aplicaciones')
users_online = Gauge('users_online', 'Usuarios conectados en tiempo real')
cpu_usage = Gauge('server_cpu_usage_percent', 'Uso de CPU del servidor (%)')
memory_usage = Gauge('server_memory_usage_percent', 'Uso de memoria del servidor (%)')
disk_usage = Gauge('server_disk_usage_percent', 'Uso de disco del servidor (%)')
bandwidth_in = Gauge('bandwidth_in_mbps', 'Ancho de banda entrante (Mbps)')
bandwidth_out = Gauge('bandwidth_out_mbps', 'Ancho de banda saliente (Mbps)')

# -------------------------------
# Random metrics values generator
# -------------------------------
def update_metrics():
    while True:
        emails_sent.set(random.randint(1000, 5000))
        emails_failed.set(random.randint(0, 50))
        apps_access.set(random.randint(500, 2000))
        apps_errors.set(random.randint(0, 20))
        users_online.set(random.randint(10, 100))
        cpu_usage.set(round(random.uniform(10, 90), 2))
        memory_usage.set(round(random.uniform(20, 95), 2))
        disk_usage.set(round(random.uniform(30, 85), 2))
        bandwidth_in.set(round(random.uniform(50, 500), 2))
        bandwidth_out.set(round(random.uniform(50, 500), 2))
        time.sleep(5)

# -------------------------------
# Flask App
# -------------------------------
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/health")
def health():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("health-check"):
        return {"status": "OK"}, 200

@app.route("/metrics")
def metrics():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("metrics-endpoint"):
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# -------------------------------
# Main entry point
# -------------------------------
if __name__ == "__main__":
    # Start Prometheus native exporter on port 8000
    start_http_server(8000)

    # Start metrics update thread
    threading.Thread(target=update_metrics, daemon=True).start()

    # Start Flask server on port 8080
    app.run(host="0.0.0.0", port=8080)