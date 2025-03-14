import pandas as pd

class DataFrameService:
    
    def __init__(self, list_of_tuples):
        self.tuples = list_of_tuples

    def tuples_to_dataframe(self):
        df = pd.DataFrame(self.tuples)
        