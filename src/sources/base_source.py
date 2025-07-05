from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

# Convertemos para dataclass para maior flexibilidade.
@dataclass
class FileReference:
    """
    Representa uma referência a um arquivo de qualquer fonte.

    Attributes:
        local_path: O caminho absoluto para o arquivo no sistema local.
                    Para o Drive, este é o caminho do arquivo temporário.
        name: O nome original do arquivo (ex: "imagem.jpg").
        remote_id: O ID do arquivo na fonte remota (ex: Google Drive file_id).
                   É None para fontes locais.
    """
    local_path: str
    name: str
    remote_id: Optional[str] = None


class BaseSource(ABC):
    """
    Classe base abstrata que define a interface para qualquer fonte de dados.
    """
    @abstractmethod
    def get_files(self) -> List[FileReference]:
        """
        Método que busca os arquivos da fonte e os retorna como uma lista
        de objetos FileReference.
        """
        pass