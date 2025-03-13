# OLAF - Sistema de Otimização de Logística de Arquivos de Fotografia

## Visão Geral

OLAF é um sistema desenvolvido em Python para automatizar e otimizar o fluxo de cobertura de eventos fotográficos. O sistema integra com a API do Google Drive para gerenciar a organização dos arquivos, permitindo que fotógrafos façam o upload de suas fotos RAW em pastas individuais. Posteriormente, os arquivos são consolidados, ordenados cronologicamente e renomeados de forma sequencial, incluindo o nome do fotógrafo como sufixo.

## Funcionalidades

- **Integração com Google Drive API:** Autenticação, listagem e download de arquivos.
- **Extração de Metadados RAW:** Utiliza a biblioteca rawpy para extrair dados EXIF e técnicos dos arquivos RAW.
- **Organização e Consolidação:** Reúne os arquivos de diferentes fotógrafos em uma única pasta e os renomeia conforme a ordem cronológica.
- **Suporte a Múltiplos Formatos RAW:** Compatível com diversos formatos (CR2, NEF, ARW, RAF, etc.).

## Pré-Requisitos

- **Python 3.8+**
- **Conta de Serviço no Google Cloud:** Com a Google Drive API habilitada.
- **Arquivo de Credenciais JSON:** Gerado via Cloud Console
- (Opcional) Docker para containerização (não utilizado neste momento).

