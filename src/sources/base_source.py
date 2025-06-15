from abc import ABC, abstractmethod
from typing import List, NamedTuple

# Definimos uma estrutura simples para representar um arquivo, independentemente da fonte
class FileReference(NamedTuple):
    id: str  # Pode ser o file_id do Drive ou o caminho completo local
    name: str # O nome do arquivo, ex: "imagem.jpg"

class BaseSource(ABC):
    """
    Classe base abstrata que define a interface para qualquer fonte de dados.
    """
    @abstractmethod
    def get_files(self) -> List[FileReference]:
        """
        Método que busca os arquivos da fonte e os retorna como uma lista de FileReference.
        """
        pass