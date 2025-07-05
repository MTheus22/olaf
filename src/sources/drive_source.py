from typing import List
from .base_source import BaseSource, FileReference
# Importa o drive_service de uma forma que o Python entenda no contexto do main.py
from drive_service import GoogleDriveClient
import tempfile
import os
import logging
import shutil
import re  # <-- ADICIONAR ESTA LINHA

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

        Arquivos que já estão no formato renomeado são ignorados e não são
        baixados.
        """
        query = f"'{self.folder_id}' in parents and trashed = false"
        all_drive_files = self.drive_client.list_files(query=query, page_size=1000)
        
        # --- LÓGICA DE FILTRAGEM ADICIONADA ---
        RENAMED_FILE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}')
        files_to_process = []
        skipped_count = 0

        for drive_file in all_drive_files:
            if RENAMED_FILE_PATTERN.match(drive_file['name']):
                skipped_count += 1
                continue
            files_to_process.append(drive_file)

        if skipped_count > 0:
            logging.info(f"Ignorados {skipped_count} arquivos que já parecem ter sido renomeados.")
        # --- FIM DA LÓGICA DE FILTRAGEM ---

        local_files = []
        # O loop agora itera sobre a lista já filtrada
        for drive_file in files_to_process:
            logging.info(f"Baixando '{drive_file['name']}' do Google Drive...")
            destination_path = os.path.join(self.temp_dir, drive_file['name'])
            
            self.drive_client.download_file(drive_file['id'], destination_path)
            
            local_files.append(
                FileReference(
                    local_path=destination_path,
                    name=drive_file['name'],
                    remote_id=drive_file['id']
                )
            )
            
        return local_files

    def cleanup(self):
        """
        Remove o diretório temporário e todo o seu conteúdo.
        """
        logging.info(f"Limpando diretório temporário: {self.temp_dir}")
        shutil.rmtree(self.temp_dir)