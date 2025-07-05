from typing import List
from .base_source import BaseSource, FileReference
# Importa o drive_service de uma forma que o Python entenda no contexto do main.py
from drive_service import GoogleDriveClient
import tempfile
import os
import logging
import shutil

class DriveSource(BaseSource):
    """
    Implementação da fonte de dados para o Google Drive.
    """
    def __init__(self, credentials_path: str, folder_id: str):
        self.drive_client = GoogleDriveClient(credentials_path)
        self.folder_id = folder_id
        # Cria um diretório temporário para baixar os arquivos
        self.temp_dir = tempfile.mkdtemp(prefix="olaf_drive_")
        logging.info(f"Diretório temporário para o Drive criado em: {self.temp_dir}")

    def get_files(self) -> List[FileReference]:
        """
        Baixa os arquivos do Drive para uma pasta local temporária e retorna
        as referências, preservando o ID original do Drive.
        """
        query = f"'{self.folder_id}' in parents and trashed = false"
        drive_files = self.drive_client.list_files(query=query, page_size=1000)
        
        local_files = []
        for drive_file in drive_files:
            logging.info(f"Baixando '{drive_file['name']}' do Google Drive...")
            destination_path = os.path.join(self.temp_dir, drive_file['name'])
            
            self.drive_client.download_file(drive_file['id'], destination_path)
            
            # Populamos a FileReference com toda a informação necessária.
            local_files.append(
                FileReference(
                    local_path=destination_path,
                    name=drive_file['name'],
                    remote_id=drive_file['id']  # <-- A INFORMAÇÃO CRÍTICA!
                )
            )
            
        return local_files

    def cleanup(self):
        """
        Remove o diretório temporário e todo o seu conteúdo.
        """
        logging.info(f"Limpando diretório temporário: {self.temp_dir}")
        shutil.rmtree(self.temp_dir)