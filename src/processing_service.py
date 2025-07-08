# src/processing_service.py

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional

# Importações de outros módulos do nosso projeto
from sources.base_source import FileReference
from raw_service import ExifMetadataExtractor
import utils
import time_service  # Nosso novo serviço de tempo

class BaseProcessor(ABC):
    """
    Classe base abstrata para todas as estratégias de processamento de dados.
    Define a interface que todos os processadores devem implementar.
    """
    @abstractmethod
    def prepare_data(self, files: List[FileReference], args: Any) -> List[Dict[str, Any]]:
        """
        Processa uma lista de referências de arquivo e retorna os dados
        prontos para serem ordenados e renomeados.

        Args:
            files: A lista de FileReference a ser processada.
            args: Os argumentos da linha de comando, para acesso a flags como --extract-name.

        Returns:
            Uma lista de dicionários, onde cada dicionário representa os
            dados de uma foto.
        """
        pass


class ExifProcessor(BaseProcessor):
    """
    Estratégia de processamento padrão: extrai a data de criação
    diretamente dos metadados EXIF.
    """
    def prepare_data(self, files: List[FileReference], args: Any) -> List[Dict[str, Any]]:
        photo_data = []
        logging.info("Usando estratégia ExifProcessor: extraindo data original do EXIF.")

        for file_ref in files:
            extractor = ExifMetadataExtractor(file_ref.local_path)
            create_date = extractor.extract_date("-CreateDate")
            
            if create_date:
                photographer = utils.parse_photographer_name(file_ref.name) if args.extract_name else None
                photo_data.append({
                    'local_path': file_ref.local_path,
                    'remote_id': file_ref.remote_id,
                    'date': create_date,
                    'photographer': photographer
                })
        return photo_data


class ManualCorrectionProcessor(BaseProcessor):
    """
    Estratégia de correção manual: usa uma data base fornecida pelo usuário
    e aplica um offset de horário extraído do EXIF.
    """
    def __init__(self, base_date_str: str, offset_str: str):
        """
        Inicializa o processador com a data base e o offset.

        Args:
            base_date_str: A data no formato "AAAA-MM-DD".
            offset_str: O offset de horário (ex: "-2h30m").
        """
        self.base_date_str = base_date_str
        self.offset_str = offset_str
        self.time_offset = time_service.parse_offset_to_timedelta(offset_str)

    def prepare_data(self, files: List[FileReference], args: Any) -> List[Dict[str, Any]]:
        if self.time_offset is None:
            logging.error(f"Formato de offset inválido: '{self.offset_str}'. Use um formato como '+1h', '-30m', ou '-2h15m30s'.")
            return []

        try:
            base_date = datetime.strptime(self.base_date_str, "%Y-%m-%d")
        except ValueError:
            logging.error(f"Formato de data inválido: '{self.base_date_str}'. Use o formato AAAA-MM-DD.")
            return []

        photo_data = []
        logging.info(f"Usando estratégia ManualCorrectionProcessor com data base '{self.base_date_str}' e offset '{self.offset_str}'.")

        for file_ref in files:
            extractor = ExifMetadataExtractor(file_ref.local_path)
            # Extraímos a data completa para obter o objeto datetime
            create_date_str = extractor.extract_date("-CreateDate")
            
            if create_date_str:
                try:
                    # Convertendo a string de data do EXIF para um objeto datetime
                    exif_datetime = datetime.strptime(create_date_str, "%Y:%m:%d %H:%M:%S")
                    
                    # Aplicando o offset ao horário original
                    corrected_time = exif_datetime + self.time_offset
                    
                    # Combinando a data base manual com o novo horário corrigido
                    final_datetime = corrected_time.replace(
                        year=base_date.year,
                        month=base_date.month,
                        day=base_date.day
                    )

                    # Convertendo de volta para o formato de string que o DataFrameService espera
                    final_date_str = final_datetime.strftime("%Y:%m:%d %H:%M:%S")

                    photographer = utils.parse_photographer_name(file_ref.name) if args.extract_name else None
                    photo_data.append({
                        'local_path': file_ref.local_path,
                        'remote_id': file_ref.remote_id,
                        'date': final_date_str,
                        'photographer': photographer
                    })
                except ValueError as e:
                    logging.warning(f"Não foi possível processar a data '{create_date_str}' para o arquivo {file_ref.name}. Erro: {e}")

        return photo_data