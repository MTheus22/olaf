# main.py
import argparse
import os
import re
import logging
from dotenv import load_dotenv
import utils

# Importa nossas novas fontes e serviços
from sources.base_source import BaseSource
from sources.local_source import LocalSource
from sources.drive_source import DriveSource
from data_frame_service import DataFrameService
from processing_service import (
    BaseProcessor, ExifProcessor, ManualCorrectionProcessor
)

def process_files(source: BaseSource, processor: BaseProcessor, args: argparse.Namespace):
    """
    Função de processamento de ponta a ponta que utiliza uma estratégia de
    processamento (Processor) para preparar os dados antes de renomear.

    Args:
        source: A fonte dos dados (LocalSource ou DriveSource).
        processor: A estratégia de processamento a ser usada (ExifProcessor ou ManualCorrectionProcessor).
        args: Os argumentos parseados da linha de comando.
    """
    logging.info(f"Iniciando busca de arquivos da fonte: {source.__class__.__name__}")
    files = source.get_files()

    if not files:
        logging.warning("Nenhum arquivo encontrado na fonte especificada.")
        return

    logging.info(f"Encontrados {len(files)} arquivos. Usando processador: {processor.__class__.__name__}")
    
    # Delegação da preparação dos dados para a estratégia escolhida
    photo_data = processor.prepare_data(files, args)

    if not photo_data:
        logging.warning("Nenhum arquivo novo para processar após a preparação dos dados.")
        if isinstance(source, DriveSource):
            source.cleanup()
        return

    logging.info(f"Dados preparados para {len(photo_data)} fotos.")
    
    df_service = DataFrameService(photo_data)
    df_sorted = df_service.prepare_and_sort()

    logging.info("Iniciando processo de renomeação...")
    for index, row in df_sorted.iterrows():
        # Constrói o nome base do arquivo
        final_name_base = row['new_name_date']
        if row.get('photographer'):
            sanitized_name = utils.sanitize_for_filename(row['photographer'])
            final_name_base = f"{final_name_base}_{sanitized_name}"
        
        original_local_path = row['original_path']
        _, extension = os.path.splitext(original_local_path)
        new_filename = f"{final_name_base}{extension.lower()}"

        # --- A LÓGICA DE RENOMEAÇÃO ESTRATÉGICA ---
        # Se remote_id existe, estamos lidando com o Google Drive
        if row['remote_id']:
            try:
                # Usa o cliente do Drive (acessado através da 'source') para renomear na nuvem
                source.drive_client.rename_file(
                    file_id=row['remote_id'],
                    new_name=new_filename
                )
            except Exception as e:
                logging.error(f"Não foi possível renomear o arquivo {row['remote_id']} no Drive. Erro: {e}")

        # Se não, é um arquivo local
        else:
            dir_path = os.path.dirname(original_local_path)
            new_path = os.path.join(dir_path, new_filename)

            # Lógica para evitar sobrescrever arquivos
            counter = 1
            while os.path.exists(new_path):
                new_filename_with_counter = f"{final_name_base}_{counter}{extension.lower()}"
                new_path = os.path.join(dir_path, new_filename_with_counter)
                counter += 1
            
            os.rename(original_local_path, new_path)
            logging.info(f"Renomeado localmente: {os.path.basename(original_local_path)} -> {os.path.basename(new_path)}")

    # Limpa os arquivos temporários DEPOIS que todo o processamento terminou
    if isinstance(source, DriveSource):
        source.cleanup()

def main():
    """Ponto de entrada principal da aplicação."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    load_dotenv()

    parser = argparse.ArgumentParser(description="OLAF - Otimizador de Logística de Arquivos de Fotografia.")
    action_subparsers = parser.add_subparsers(dest='action', required=True, help="Ação a ser executada")

    # --- Ação 1: Processamento Padrão ---
    parser_process = action_subparsers.add_parser('process', help='Renomeia arquivos com base na data EXIF original.')
    source_process_subparsers = parser_process.add_subparsers(dest='source', required=True, help="Fonte dos arquivos")
    
    # Processamento > Fonte Local
    parser_process_local = source_process_subparsers.add_parser('local', help='Fonte: pasta local.')
    parser_process_local.add_argument('--path', help='Caminho para a pasta. Usa LOCAL_PHOTOS_PATH do .env se não for especificado.')
    parser_process_local.add_argument('--extract-name', action='store_true', help='Extrai o nome do fotógrafo do nome do arquivo.')

    # Processamento > Fonte Drive
    parser_process_drive = source_process_subparsers.add_parser('drive', help='Fonte: Google Drive.')
    parser_process_drive.add_argument('--folder-id', help='ID da pasta. Usa GDRIVE_FOLDER_ID do .env.')
    parser_process_drive.add_argument('--credentials', help='Caminho para credentials.json. Usa GDRIVE_CREDENTIALS_PATH do .env.')
    parser_process_drive.add_argument('--extract-name', action='store_true', help='Extrai o nome do fotógrafo do nome do arquivo.')

    # --- Ação 2: Correção Manual de Data ---
    parser_fixdate = action_subparsers.add_parser('fixdate', help='Renomeia arquivos usando uma data base e um offset de horário.')
    source_fixdate_subparsers = parser_fixdate.add_subparsers(dest='source', required=True, help="Fonte dos arquivos")
    
    # Fixdate > Fonte Local
    parser_fixdate_local = source_fixdate_subparsers.add_parser('local', help='Fonte: pasta local.')
    parser_fixdate_local.add_argument('--path', help='Caminho para a pasta.')
    parser_fixdate_local.add_argument('--date', required=True, help='Data base no formato AAAA-MM-DD.')
    parser_fixdate_local.add_argument('--offset', required=True, help='Offset de horário (ex: "+2h", "-1h30m").')
    parser_fixdate_local.add_argument('--extract-name', action='store_true', help='Extrai o nome do fotógrafo.')
    
    # Fixdate > Fonte Drive
    parser_fixdate_drive = source_fixdate_subparsers.add_parser('drive', help='Fonte: Google Drive.')
    parser_fixdate_drive.add_argument('--folder-id', help='ID da pasta do Drive.')
    parser_fixdate_drive.add_argument('--credentials', help='Caminho para as credenciais.')
    parser_fixdate_drive.add_argument('--date', required=True, help='Data base no formato AAAA-MM-DD.')
    parser_fixdate_drive.add_argument('--offset', required=True, help='Offset de horário (ex: "+2h", "-1h30m").')
    parser_fixdate_drive.add_argument('--extract-name', action='store_true', help='Extrai o nome do fotógrafo.')

    args = parser.parse_args()

    # --- Seleção da Estratégia e da Fonte ---
    source = None
    processor = None

    if args.source == 'local':
        local_path = args.path or os.getenv('LOCAL_PHOTOS_PATH')
        if not local_path:
            logging.error("Erro: Especifique o caminho com --path ou defina LOCAL_PHOTOS_PATH no .env")
            return
        source = LocalSource(path=local_path)
    elif args.source == 'drive':
        folder_id = args.folder_id or os.getenv('GDRIVE_FOLDER_ID')
        credentials_path = args.credentials or os.getenv('GDRIVE_CREDENTIALS_PATH')
        if not folder_id or not credentials_path:
            logging.error("Erro: Especifique --folder-id e --credentials ou defina as variáveis no .env")
            return
        source = DriveSource(credentials_path=credentials_path, folder_id=folder_id)

    if args.action == 'process':
        processor = ExifProcessor()
    elif args.action == 'fixdate':
        processor = ManualCorrectionProcessor(base_date_str=args.date, offset_str=args.offset)

    if source and processor:
        process_files(source, processor, args)

if __name__ == '__main__':
    main()