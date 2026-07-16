# Implantação

## Desenvolvimento

```bash
pip install -e ".[dev,api,dashboard]"
neurojitsu demo
```

## Docker local

```bash
docker compose up --build
```

## Estação de pesquisa

Recomendado:

- Ubuntu LTS;
- Python 3.11;
- SSD criptografado;
- conta de sistema exclusiva;
- firewall bloqueando saída não necessária;
- câmera em rede local isolada ou USB;
- banco SQLCipher;
- backup criptografado;
- relógio sincronizado localmente;
- GPU apenas para MMPose/Qwen.

## Perfis de contêiner futuros

- `core-api`: CPU, sem câmera;
- `capture-worker`: acesso à câmera;
- `pose-gpu`: MMPose opcional;
- `dashboard`: somente métricas;
- `wifi-sensing`: RuView experimental;
- `report-llm`: Qwen local, sem acesso ao banco de identidade.
