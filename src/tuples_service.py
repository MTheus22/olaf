#tuples_service.py

import re
import os
import logging
import subprocess
from raw_service import ExifMetadataExtractor

class TuplesService:
    """
    Serviço para gerar e exibir uma lista de tuplas contendo o nome do arquivo e a data de criação,
    extraída dos metadados dos arquivos RAW presentes em um diretório.
    """

    def __init__(self, dir_path: str):
        """
        Inicializa o serviço com o caminho do diretório contendo os arquivos RAW.

        Args:
            dir_path (str): Caminho para o diretório.
        """
        self.dir_path = dir_path
        # Gera a lista de caminhos completos dos arquivos no diretório
        self.file_paths = self.file_paths_to_list()

    def file_paths_to_list(self):
        """
        Cria uma lista de caminhos completos para os arquivos presentes no diretório.

        Returns:
            list: Lista de strings contendo os caminhos dos arquivos encontrados.
        """
        file_paths = []
        if os.path.isdir(self.dir_path):
            # Lista os nomes dos arquivos no diretório
            files = os.listdir(self.dir_path)
            for file in files:
                # Constrói o caminho completo para cada arquivo
                file_path = os.path.join(self.dir_path, file)
                file_paths.append(file_path)
        return file_paths

    def name_date_to_tuples(self, paths_list=None):
        """
        Gera uma lista de tuplas, onde cada tupla contém:
          - O nome do arquivo (sem a extensão)
          - A data de criação extraída dos metadados usando ExifTool.

        Args:
            paths_list (list, optional): Lista de caminhos dos arquivos para processar.
                                         Se None, utiliza self.file_paths.

        Returns:
            list: Lista de tuplas no formato (nome_do_arquivo, data_de_criacao).
        """
        if paths_list is None:
            paths_list = self.file_paths

        list_of_tuples = []
        # Itera sobre cada caminho na lista
        for path in paths_list:
            # Obtém o nome do arquivo com a extensão
            file_name_with_extension = os.path.basename(path)
            # Separa o nome do arquivo da extensão
            file_name, _ = os.path.splitext(file_name_with_extension)
            # Inicializa o extractor para o arquivo RAW
            extractor = ExifMetadataExtractor(path)
            # Extrai a data de criação utilizando a flag "-CreateDate"
            file_date = extractor.extract_date("-CreateDate")
            # Adiciona uma tupla com o nome e a data à lista
            list_of_tuples.append((file_name, file_date))
        return list_of_tuples

    def display_tuples(self):
        """
        Exibe a lista de tuplas contendo o nome do arquivo e a data de criação.
        """
        tuples_list = self.name_date_to_tuples()
        logging.info(f"Tuples list: {tuples_list}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Define o diretório contendo os arquivos RAW
    dir_path = "./fotos"
    tuples_service = TuplesService(dir_path)
    # Exibe as tuplas com os nomes dos arquivos e suas datas de criação
    tuples_service.display_tuples()
