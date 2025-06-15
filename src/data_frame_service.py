# data_frame_service.py (versão atualizada)
import pandas as pd

class DataFrameService:
    def __init__(self, data: list):
        self.df = pd.DataFrame(data)

    def prepare_and_sort(self):
        """
        Prepara o DataFrame, converte datas, ordena e gera a base para o novo nome.
        """
        if self.df.empty:
            return pd.DataFrame()

        # Converte a coluna de data para um objeto de data real
        self.df['capture_date_obj'] = pd.to_datetime(self.df['date'], format='%Y:%m:%d %H:%M:%S', errors='coerce')
        self.df.dropna(subset=['capture_date_obj'], inplace=True)

        # Ordena o DataFrame cronologicamente
        self.df.sort_values(by='capture_date_obj', inplace=True)
        
        # Gera a coluna com o novo nome (apenas a parte da data)
        self.df['new_name_date'] = self.df['capture_date_obj'].dt.strftime('%Y-%m-%d_%H-%M-%S')

        # Garante que a coluna 'photographer' exista, mesmo que vazia
        if 'photographer' not in self.df.columns:
            self.df['photographer'] = None
            
        # Renomeia 'path' para clareza
        self.df.rename(columns={'path': 'original_path'}, inplace=True)

        return self.df[['original_path', 'new_name_date', 'photographer']]