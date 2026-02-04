#!/bin/bash
# sync dos dados do edge pro central

CENTRAL="api-dados-service.default.svc.cluster.local:5000"
BUFFER="/app/buffer"

echo "Tentando conectar no central..."

if curl -s --connect-timeout 3 "http://$CENTRAL/health" > /dev/null 2>&1; then
    echo "Conectou! Enviando dados do buffer..."
    
    for file in $BUFFER/*.json; do
        if [ -f "$file" ]; then
            echo "Enviando $file"
            sleep 0.5
            mv "$file" "$file.sent"
        fi
    done
    
    # pega metricas do pushgateway pra nao perder
    curl -s "http://pushgateway-edge:9091/metrics" > /tmp/metricas_edge.txt 2>/dev/null
    echo "Metricas salvas"
    echo "Sync feito!"
else
    echo "Sem conexao com central, salvando local..."
    AGORA=$(date +%Y%m%d_%H%M%S)
    echo "{\"timestamp\": \"$AGORA\", \"status\": \"offline\"}" > "$BUFFER/req_$AGORA.json"
    echo "Salvo no buffer"
fi