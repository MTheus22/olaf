from typing import List
from .base_source import BaseSource, FileReference
from drive_service import GoogleDriveClient # Reutiliza sua classe original!
import tempfile
import os

class DriveSource(BaseSource):
    """
    Implementação da fonte de dados para o Google Drive.
    """
    def __init__(self, credentials_path: str, folder_id: str):
        self.drive_client = GoogleDriveClient(credentials_path)
        self.folder_id = folder_id
        # Cria um diretório temporário para baixar os arquivos
        self.temp_dir = tempfile.mkdtemp(prefix="olaf_drive_")

    def get_files(self) -> List[FileReference]:
        query = f"'{self.folder_id}' in parents"
        drive_files = self.drive_client.list_files(query=query, page_size=1000) # Aumentar o limite
        
        local_files = []
        for drive_file in drive_files:
            print(f"Baixando {drive_file['name']}...")
            destination_path = os.path.join(self.temp_dir, drive_file['name'])
            self.drive_client.download_file(drive_file['id'], destination_path)
            local_files.append(FileReference(id=destination_path, name=drive_file['name']))
            
        return local_files

    def cleanup(self):
        # Método para limpar os arquivos temporários após o uso
        import shutil
        shutil.rmtree(self.temp_dir)