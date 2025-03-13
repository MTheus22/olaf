import rawpy
import logging

class RawMetadataExtractor:
    """
    Classe responsável por extrair metadados de arquivos RAW utilizando rawpy.
    """   

    def __init__(self, file_path: str):        
        """
        Inicializa com o caminho para o arquivo RAW.
        
        :param file_path: Caminho local do arquivo RAW.
        """

        self.file_path = file_path
        self.exif_data = None

    def extract_metadata(self):
        """
        Abre o arquivo RAW e extrai os metadados EXIF.
        """
        try:
            with rawpy.imread(self.file_path) as raw:
                # raw.exif_data é um dicionário (ou None) com os metadados EXIF
                self.exif_data = raw.exif_data 
                logging.info("Metadados extraídos com sucesso.")  
        except Exception as e:
            logging.error(f"Erro ao extrair metadados: {e}")
            raise e

    def display_metadata(self):
        """
        Exibe os metadados extraídos.
        """
        if self.exif_data:
            logging.info("Metadados extraídos:")
            for tag, value in self.exif_data.items():
                logging.info(f"{tag}: {value}")
        else:
            logging.info("Nenhum metadado extraído.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Para testes, substitua 'file_path' pelo caminho real do arquivo baixado do Drive.
    file_path = "download_DSCF5231"
    extractor = RawMetadataExtractor(file_path)
    extractor.extract_metadata()
    extractor.display          