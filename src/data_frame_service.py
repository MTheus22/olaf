# data_frame_service.py
import pandas as pd

class DataFrameService:
    def __init__(self, data: list):
        # Espera uma lista de dicionários ou tuplas nomeadas
        self.df = pd.DataFrame(data)

    def prepare_and_sort(self, date_column_name: str, path_column_name: str):
        """
        Converte a coluna de data, ordena o DataFrame e gera o novo nome.
        """
        if self.df.empty:
            return self.df

        # Renomeia colunas para um padrão fixo
        self.df.rename(columns={date_column_name: 'capture_date', path_column_name: 'original_path'}, inplace=True)

        # 1. Converte a string de data para um objeto de data real
        self.df['capture_date'] = pd.to_datetime(self.df['capture_date'], format='%Y:%m:%d %H:%M:%S', errors='coerce')

        # 2. Remove linhas que não puderam ser convertidas
        self.df.dropna(subset=['capture_date'], inplace=True)

        # 3. Ordena o DataFrame cronologicamente
        self.df.sort_values(by='capture_date', inplace=True)
        
        # 4. Gera o novo nome do arquivo
        self.df['new_name'] = self.df['capture_date'].dt.strftime('%Y-%m-%d_%H-%M-%S')
        
        return self.df