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
from raw_service import ExifMetadataExtractor
from data_frame_service import DataFrameService

def process_files(source: BaseSource, args: argparse.Namespace):
    """
    Função de processamento de ponta a ponta: busca arquivos, extrai metadados,
    ordena e os renomeia de acordo com a fonte (local ou remota).

    Args:
        source: Uma instância de uma classe que herda de BaseSource (LocalSource ou DriveSource).
        args: Os argumentos parseados da linha de comando.
    """
    logging.info(f"Iniciando busca de arquivos da fonte: {source.__class__.__name__}")
    files = source.get_files()

    RENAMED_FILE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}')

    if not files:
        logging.warning("Nenhum arquivo encontrado na fonte especificada.")
        return

    logging.info(f"Encontrados {len(files)} arquivos. Extraindo metadados...")
    
    photo_data = []
    processed_count = 0
    for file_ref in files:
        if RENAMED_FILE_PATTERN.match(file_ref.name):
            processed_count += 1
            continue 

        # O ExifMetadataExtractor agora usa o caminho local (mesmo que temporário)
        extractor = ExifMetadataExtractor(file_ref.local_path)
        create_date = extractor.extract_date("-CreateDate")
        
        if create_date:
            photographer = utils.parse_photographer_name(file_ref.name) if args.extract_name else None
            # Armazenamos todos os dados relevantes, incluindo o remote_id
            photo_data.append({
                'local_path': file_ref.local_path,
                'remote_id': file_ref.remote_id,
                'date': create_date,
                'photographer': photographer
            })

    if processed_count > 0:
        logging.info(f"Ignorados {processed_count} arquivos que já parecem ter sido renomeados.")

    if not photo_data:
        logging.warning("Nenhum arquivo novo para processar.")
        # Garante a limpeza de arquivos temporários do Drive mesmo que nada seja renomeado
        if isinstance(source, DriveSource):
            source.cleanup()
        return

    logging.info(f"Metadados extraídos de {len(photo_data)} novas fotos.")
    
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
    
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="OLAF - Otimizador de Logística de Arquivos de Fotografia."
    )
    subparsers = parser.add_subparsers(
        dest='command',
        required=True,
        help="Comando a ser executado"
    )

    # --- Comando para processar pasta local ---
    parser_local = subparsers.add_parser(
        'local',
        help='Processa fotos de uma pasta local.'
    )
    parser_local.add_argument(
        '--path',
        # Não é mais obrigatório na CLI
        help='Caminho para a pasta com as fotos. Pode ser definido via LOCAL_PHOTOS_PATH no .env'
    )
    parser_local.add_argument(
        '--extract-name',
        action='store_true',
        help='Ativa a extração do nome do fotógrafo a partir do nome do arquivo.'
    )

    # --- Comando para processar do Google Drive ---
    parser_drive = subparsers.add_parser(
        'drive',
        help='Processa fotos de uma pasta no Google Drive.'
    )
    parser_drive.add_argument(
        '--folder-id',
        # Não é mais obrigatório na CLI
        help='ID da pasta no Google Drive. Pode ser definido via GDRIVE_FOLDER_ID no .env'
    )
    parser_drive.add_argument(
        '--credentials',
        # Não é mais obrigatório na CLI
        help='Caminho para o credentials.json. Pode ser definido via GDRIVE_CREDENTIALS_PATH no .env'
    )

    parser_drive.add_argument(
        '--extract-name',
        action='store_true',
        help='Ativa a extração do nome do fotógrafo a partir do nome do arquivo.'
    )
    
    args = parser.parse_args()

    source = None
    if args.command == 'local':
        # Prioriza o argumento da CLI, senão busca no .env
        local_path = args.path or os.getenv('LOCAL_PHOTOS_PATH')
        if not local_path:
            logging.error("Erro: O caminho da pasta local não foi especificado. "
                          "Use --path ou defina LOCAL_PHOTOS_PATH no seu arquivo .env")
            return
        source = LocalSource(path=local_path)

    elif args.command == 'drive':
        # Prioriza os argumentos da CLI, senão busca no .env
        folder_id = args.folder_id or os.getenv('GDRIVE_FOLDER_ID')
        credentials_path = args.credentials or os.getenv('GDRIVE_CREDENTIALS_PATH')
        
        if not folder_id or not credentials_path:
            logging.error("Erro: Para o modo drive, é necessário especificar o ID da pasta e o caminho das credenciais. "
                          "Use --folder-id e --credentials ou defina GDRIVE_FOLDER_ID e GDRIVE_CREDENTIALS_PATH no seu arquivo .env")
            return
            
        source = DriveSource(
            credentials_path=credentials_path,
            folder_id=folder_id
        )

    if source:
        process_files(source, args)

if __name__ == '__main__':
    main()