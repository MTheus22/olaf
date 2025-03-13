import logging
from drive_service import GoogleDriveClient
from raw_service import RawMetadataExtractor

def main():
    # Configura o loggin para exibir mensagens de INFO.
    logging.basicConfig(level=logging.INFO)

    # Campinho para o arquivo JSON de credenciais da conta de serviço
    credentials_path = 'config/service_account_credentials.json'

    # Inicializa o cliente do Google Drive
    drive_client = GoogleDriveClient(credentials_path)

    # ID da pasta no Google Drive
    folder_id = '1ND3a_bGo2FM6BlMXkxkEpEkJpnM8HyQ0'
    query = f"'{folder_id}' in parents"

    # Lista arquivos presentes na pasta especificada
    files = drive_client.list_files(query=query, page_size=5)

    if not files:
        logging.info("Nenhum arquivo encontrado na pasta especificada.")
    else:
        logging.info("Arquivos encontrados:")
        for file in files:
            logging.info(f"{file['name']} (ID: {file['id']}) - MIME Type: {file['mimeType']}")

    # Para fins de teste, baixa o primeiro arquivo listado
    file_to_download = files[0]
    destination = f"download_{file_to_download['name']}"
    drive_client.download_file(file_to_download['id'], destination)
    logging.info("Download concluído com sucesso.")

if __name__ == '__main__':
    main()