#!/bin/bash

# --- Script de Configuração para o Projeto OLAF ---
# Este script prepara o ambiente para a execução, instalando dependências
# de sistema e de Python.

# O comando 'set -e' garante que o script irá parar imediatamente se qualquer
# comando falhar, evitando erros inesperados mais tarde.
set -e

echo "--- Iniciando configuração do ambiente OLAF ---"

# --- 1. Instalação de Dependências de Sistema ---
# O OLAF depende do programa externo 'exiftool' para ler os metadados.
# Usamos 'sudo apt-get' assumindo um ambiente baseado em Debian/Ubuntu,
# que é o padrão para a maioria das plataformas de CI/CD.
echo "--> Atualizando listas de pacotes e instalando ExifTool..."
sudo apt-get update -y
sudo apt-get install -y libimage-exiftool-perl

# --- 2. Configuração do Ambiente Virtual Python ---
# É uma boa prática criar um ambiente virtual para isolar as dependências
# do projeto e evitar conflitos com pacotes do sistema.
echo "--> Criando ambiente virtual Python em ./venv..."
python3 -m venv venv

echo "--> Ativando o ambiente virtual..."
source venv/bin/activate

# --- 3. Instalação das Dependências Python ---
# Primeiro, atualizamos as ferramentas de empacotamento para evitar
# problemas comuns de instalação.
echo "--> Atualizando pip, setuptools e wheel..."
pip install --upgrade pip setuptools wheel

# Agora, instalamos todas as bibliotecas Python listadas no requirements.txt.
echo "--> Instalando dependências do projeto via pip..."
pip install -r requirements.txt

# --- 4. Verificação Final (Sanity Check) ---
# Executamos alguns comandos para garantir que tudo foi instalado corretamente.
echo "--> Verificando as instalações:"

# Verifica se o exiftool foi instalado e está no PATH
echo -n "Versão do ExifTool: "
exiftool -ver

# Verifica a versão do Python no ambiente virtual
echo -n "Versão do Python: "
python --version

# Mostra os pacotes Python instalados no ambiente
echo "Pacotes Python instalados:"
pip freeze

echo "--- Configuração do ambiente concluída com sucesso! ---"