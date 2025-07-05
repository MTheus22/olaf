#!/bin/bash

# Garante que o script pare se qualquer comando falhar
set -e

# Encontra o diretório onde o script está localizado
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

# Log com a data de execução e o modo
echo "--- Executando OLAF (modo Drive) em $(date) ---" >> "$SCRIPT_DIR/olaf_runs.log"

# Ativa o ambiente virtual
# Lembre-se de que este caminho deve corresponder à localização do seu ambiente
source ~/.virtualenvs/olaf/bin/activate

# Executa o script OLAF no modo 'drive'.
# As configurações são lidas do arquivo .env, então não são necessários argumentos de caminho ou ID.
# A flag --extract-name foi mantida, mas é opcional.
# A saída e os erros são redirecionados para um arquivo de log.
python "$SCRIPT_DIR/src/main.py" drive --extract-name >> "$SCRIPT_DIR/olaf_runs.log" 2>&1