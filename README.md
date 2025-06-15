Segue o conteúdo convertido para **Markdown**, pronto para uso no `README.md`:

# OLAF - Otimizador de Logística de Arquivos de Fotografia

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Visão Geral

OLAF é um sistema desenvolvido em Python para automatizar e otimizar o fluxo de trabalho com arquivos fotográficos. Projetado com uma arquitetura modular, ele centraliza e organiza cronologicamente fotos de múltiplas fontes, garantindo que o resultado final seja uma sequência de imagens coesa e pronta para edição ou arquivamento.

Atualmente, o OLAF suporta o processamento de arquivos de duas fontes distintas:
1. **Pastas Locais:** Ideal para organizar arquivos que já estão no computador ou sincronizados via serviços como OneDrive, Dropbox, etc.
2. **Pastas do Google Drive:** Mantém a funcionalidade original de se conectar à API do Google Drive para baixar e processar arquivos diretamente da nuvem.

## Funcionalidades Principais

- **Processamento de Múltiplas Fontes:** Graças a uma arquitetura de "fontes" desacoplada, o sistema pode facilmente processar arquivos de um diretório local ou de uma pasta do Google Drive.
- **Organização Cronológica Precisa:** Utiliza a poderosa ferramenta externa **ExifTool** para extrair a data e hora exatas da captura de cada foto, garantindo uma ordenação cronológica perfeita.
- **Interface de Linha de Comando (CLI):** Uma interface de comando robusta e intuitiva, construída com `argparse`, permite ao usuário escolher facilmente o modo de operação (local ou Drive) e fornecer os parâmetros necessários.
- **Arquitetura Modular e Extensível:** O código é dividido em "serviços" com responsabilidades claras (extração de dados, manipulação de tabelas, fontes de dados), facilitando a manutenção e a adição de novas funcionalidades no futuro.

## Pré-requisitos

Antes de executar o OLAF, garanta que os seguintes requisitos estão atendidos no seu sistema:

1. **Python 3.12+**
2. **Ambiente Virtual (`venv`):** Altamente recomendado para isolar as dependências do projeto.
3. **ExifTool:** O OLAF depende deste programa externo para ler os metadados das fotos. Ele **precisa** ser instalado no seu sistema operacional.
   - **Windows:** Siga as instruções em [ExifTool Website](https://exiftool.org/install.html#Windows)
   - **Linux (Debian/Ubuntu/WSL):** `sudo apt update && sudo apt install libimage-exiftool-perl`
   - **macOS:** `brew install exiftool`

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone <url_do_seu_repositorio>
   cd olaf
   ```

2. **Crie e ative um ambiente virtual:**

   ```bash
   # Cria o ambiente
   python -m venv venv

   # Ativa o ambiente
   # No Windows (PowerShell):
   .\venv\Scripts\activate
   # No Linux/macOS/WSL:
   source venv/bin/activate
   ```

3. **Instale as dependências Python:**

   ```bash
   pip install -r requirements.txt
   ```

## Como Usar

O OLAF é operado através do `main.py` com diferentes sub-comandos.

---

### **Modo Local**

Use este modo para organizar fotos de uma pasta no seu computador (ex: uma pasta sincronizada do OneDrive).

**Comando:**

```bash
python src/main.py local --path "caminho/para/sua/pasta"
```

---

### **Modo Google Drive**

Use este modo para executar a funcionalidade original de baixar e processar arquivos de uma pasta do Google Drive.
*Nota: Requer que as bibliotecas do Google (`google-api-python-client`, etc.) estejam no `requirements.txt`.*

**Comando:**

```bash
python src/main.py drive --folder-id "ID_DA_PASTA_NO_DRIVE" --credentials "caminho/para/credentials.json"
```

## Arquitetura do Projeto

* `src/main.py`: Ponto de entrada da aplicação, responsável pela interface de linha de comando (CLI) e por orquestrar os serviços.
* `src/sources/`: Contém a abstração de "fontes de dados". Cada arquivo aqui é um "plug" para uma fonte diferente (local, Drive, etc.).
* `src/raw_service.py`: Serviço responsável por interagir com o ExifTool e extrair metadados brutos de um arquivo.
* `src/data_frame_service.py`: Serviço que utiliza a biblioteca Pandas para receber os dados extraídos, ordená-los cronologicamente e preparar para a renomeação.
* `src/drive_service.py`: Cliente original de baixo nível para a API do Google Drive, utilizado pelo `drive_source`.
