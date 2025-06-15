#drive_service.py

import io
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class GoogleDriveClient:
    """
    Cliente para interagir com a API do Google Drive utilizando credenciais de conta de serviço.
    """

    def __init__(self, credentials_path: str, scopes: list = None): 
        """
        Inicializa o cliente do Google Drive.
        
        :param credentials_path: Caminho para o arquivo JSON de credenciais.
        :param scopes: Lista de escopos. Se None, utiliza o escopo padrão para acesso total ao Drive.
        """

        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/drive']
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=scopes)
        self.service = build('drive', 'v3', credentials=self.credentials)
        logging.info("Google Drive Cliente inicializado com sucesso.")

    def list_files(self, query: str = None, page_size: int = 10):
        """
        Lista arquivos de acordo com a query especificada.
        
        :param query: Query para filtrar os arquivos (exemplo: "'folder_id' in parents").
        :param page_size: Número máximo de arquivos a retornar.
        :return: Lista de dicionários representando os arquivos encontrados.
        """

        results = self.service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        files = results.get('files', [])
        return files
    
    def download_file(self, file_id: str, destination_path: str):
        """
        Realiza o download de um arquivo do Google Drive.
        
        :param file_id: ID do arquivo no Google Drive.
        :param destination_path: Caminho local onde o arquivo será salvo.
        """

        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info(f"Download {int(status.progress() * 100)}%.")
        logging.info(f"Download concluído. Arquivo salvo em {destination_path}.") 