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

            # Garante que as colunas opcionais existam, mesmo que vazias
            if 'photographer' not in self.df.columns:
                self.df['photographer'] = None
            if 'remote_id' not in self.df.columns:
                self.df['remote_id'] = None
                
            # Renomeia 'local_path' para clareza
            self.df.rename(columns={'local_path': 'original_path'}, inplace=True)

            # Retorna todas as colunas necessárias para a etapa de renomeação
            return self.df[[
                'original_path', 'remote_id', 'new_name_date', 'photographer'
            ]]