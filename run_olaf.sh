#!/bin/bash

# Garante que o script pare se qualquer comando falhar
set -e

# Encontra o diretório onde o script está localizado
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

# Define o caminho para a pasta de fotos no formato WSL
FOTOS_PATH="/mnt/c/Users/mathe/OneDrive - Instituto Brasileiro de Ensino, Desenvolvimento e Pesquisa (IDP)/Casamento A&W - Registro dos Convidados"

echo "--- Executando OLAF em $(date) ---" >> "$SCRIPT_DIR/olaf_runs.log"

# Ativa o ambiente virtual
source ~/.virtualenvs/olaf/bin/activate

# Executa o script OLAF e redireciona a saída e os erros para um arquivo de log
python "$SCRIPT_DIR/src/main.py" local --path "$FOTOS_PATH" --extract-name >> "$SCRIPT_DIR/olaf_runs.log" 2>&1