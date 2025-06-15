import os
from typing import List
from .base_source import BaseSource, FileReference

class LocalSource(BaseSource):
    """
    Implementação da fonte de dados para uma pasta local.
    """
    def __init__(self, path: str):
        if not os.path.isdir(path):
            raise FileNotFoundError(f"O diretório especificado não existe: {path}")
        self.path = path

    def get_files(self) -> List[FileReference]:
        files = []
        for filename in os.listdir(self.path):
            full_path = os.path.join(self.path, filename)
            if os.path.isfile(full_path):
                # Para arquivos locais, o 'id' é o próprio caminho completo.
                files.append(FileReference(id=full_path, name=filename))
        return files