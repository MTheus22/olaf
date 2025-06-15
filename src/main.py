# main.py
import argparse
import os
import re
import logging
import utils

# Importa nossas novas fontes e serviços
from sources.base_source import BaseSource
from sources.local_source import LocalSource
from sources.drive_source import DriveSource
from raw_service import ExifMetadataExtractor
from data_frame_service import DataFrameService

def process_files(source: BaseSource, args: argparse.Namespace):
    """Função de processamento genérica que recebe qualquer fonte de dados."""
    logging.info("Iniciando busca de arquivos na fonte...")
    files = source.get_files()

    # Compilamos o padrão Regex uma vez para maior eficiência.
    RENAMED_FILE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}')

    if not files:
        logging.warning("Nenhum arquivo encontrado na fonte especificada.")
        return

    logging.info(f"Encontrados {len(files)} arquivos. Extraindo metadados...")
    
    photo_data = []
    processed_count = 0
    for file_ref in files:
        # Se o nome do arquivo corresponde ao padrão, pula para o próximo.
        if RENAMED_FILE_PATTERN.match(file_ref.name):
            processed_count += 1
            continue 

        # Extrai o nome do fotógrafo SOMENTE se o flag --extract-name for usado
        photographer = utils.parse_photographer_name(file_ref.name) if args.extract_name else None

        extractor = ExifMetadataExtractor(file_ref.id)
        # Usamos a flag -CreateDate, como no seu TuplesService
        create_date = extractor.extract_date("-CreateDate") 
        if create_date:
            photo_data.append({'path': file_ref.id, 'date': create_date,  'photographer': photographer})

    if processed_count > 0:
        logging.info(f"Ignorados {processed_count} arquivos que já foram processados anteriormente.")

    if not photo_data:
        logging.warning("Nenhum arquivo novo para processar.")
        return

    logging.info(f"Metadados extraídos. {len(photo_data)} fotos com data válida.")
    
    # Usa o DataFrameService para ordenar
    df_service = DataFrameService(photo_data)
    df_sorted = df_service.prepare_and_sort()

    logging.info("Iniciando renomeação...")
    for index, row in df_sorted.iterrows():
        original_path = row['original_path']
        new_name_base = row['new_name_date']
        photographer_name = row.get('photographer')

        final_name_base = new_name_base
        # Se o nome do fotógrafo foi extraído, adiciona ao nome base
        if photographer_name:
            sanitized_name = utils.sanitize_for_filename(photographer_name)
            final_name_base = f"{new_name_base}_{sanitized_name}"        

        # Mantém a extensão original
        _, extension = os.path.splitext(original_path)
        new_filename = f"{final_name_base}{extension.lower()}"
        
        dir_path = os.path.dirname(original_path)
        new_path = os.path.join(dir_path, new_filename)

        # Lógica para evitar sobrescrever arquivos
        counter = 1
        while os.path.exists(new_path):
            new_filename = f"{new_name_base}_{counter}{extension.lower()}"
            new_path = os.path.join(dir_path, new_filename)
            counter += 1
            
        os.rename(original_path, new_path)
        logging.info(f"Renomeado: {os.path.basename(original_path)} -> {new_filename}")

    # Limpa os arquivos temporários se a fonte for o Drive
    if isinstance(source, DriveSource):
        logging.info("Limpando arquivos temporários do Drive...")
        source.cleanup()

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = argparse.ArgumentParser(description="OLAF - Otimizador de Logística de Arquivos de Fotografia.")
    subparsers = parser.add_subparsers(dest='command', required=True, help="Comando a ser executado")

    # Comando para processar pasta local
    parser_local = subparsers.add_parser('local', help='Processa fotos de uma pasta local.')
    parser_local.add_argument('--path', required=True, help='Caminho para a pasta com as fotos.')
    parser_local.add_argument(
        '--extract-name', 
        action='store_true', 
        help='Ativa a extração do nome do fotógrafo a partir do nome do arquivo (formato: Nome_Sobrenome_arquivo.jpg).'
    )

    # Comando para processar do Google Drive
    parser_drive = subparsers.add_parser('drive', help='Processa fotos de uma pasta no Google Drive.')
    parser_drive.add_argument('--folder-id', required=True, help='ID da pasta no Google Drive.')
    parser_drive.add_argument('--credentials', required=True, help='Caminho para o arquivo de credenciais JSON.')

    args = parser.parse_args()

    source = None
    if args.command == 'local':
        source = LocalSource(path=args.path)
    elif args.command == 'drive':
        source = DriveSource(credentials_path=args.credentials, folder_id=args.folder_id)

    if source:
        process_files(source, args)

if __name__ == '__main__':
    main()