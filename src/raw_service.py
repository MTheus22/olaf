import os
import re
import logging
import subprocess

class ExifMetadataExtractor:
    """
    Classe responsável por extrair metadados de arquivos RAW utilizando exiftools.
    """   

    def __init__(self, file_path: str):        
        """
        Inicializa com o caminho para o arquivo RAW.

        :param file_path: Caminho local do arquivo RAW.
        """

        self.file_path = file_path

    def extract_metadata(self, flag = None):
        """
        Abre o arquivo RAW e extrai os metadados EXIF usando exiftools via subprocess.

        :param flag: flag válida para exiftool.

        :return: string com os metadados extraídos.
        """
        # Verifica se o arquivo existe
        if not os.path.exists(self.file_path):
            logging.error(f"Arquivo não encontrado: {self.file_path}")
            return
        
        if flag is not None and not flag.startswith("-") :
            logging.error(f"Flag inválida: {flag}")

        # Extrai os metadados
        try:
           command = ["exiftool", self.file_path] if flag is None else ["exiftool", flag, self.file_path]
           result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
           exif_data = result.stdout.strip()
           if exif_data:
             logging.info("Metadados extraídos com sucesso.")
           else:
               logging.info("Nenhum metadado encontrado.")             
           return exif_data
        except Exception as e:
            logging.error(f"Erro ao extrair metadados: {e}")
            raise e

    def extract_date(self, flag = None):
        """
        Extrai a data de criação do arquivo RAW.

        :return: string com a data de criação.
        """
        exif_data = self.extract_metadata(flag)

        match = re.search(r"Create Date\s+: (.+)", exif_data)
        if match:
            return match.group(1)
        else:
            return None

    def display_metadata(self, flag = None):
        """
        Exibe os metadados extraídos.
        """
        exif_data = self.extract_metadata(flag)

        if exif_data:
            logging.info("Metadados extraídos:")
            logging.info(exif_data)
        else:
            logging.info("Nenhum metadado extraído.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Para testes, substitua 'file_path' pelo caminho real do arquivo baixado do Drive.
    file_path = "fotos/DSCF5231.RAF"
    extractor = ExifMetadataExtractor(file_path)
    extractor.display_metadata()         