
from pathlib import Path
from requests import get  # to make GET request
from zipfile import ZipFile, BadZipFile
from io import BytesIO
import pickle
import gzip
import pandas as pd
from tqdm import tqdm



class FilesF:

    # ===============================================
    # 파일 열기
    # ===============================================
    class FileIO:
        @staticmethod
        def open_file(files:str):
            return  Path.cwd().joinpath(files).open('r')

    # ===============================================
    # Zip 파일
    # ===============================================
    class Zipfiles:
        @staticmethod
        def unzip_file(zip_file):
            try:
                with ZipFile(BytesIO(zip_file)) as zip_file:
                    for file in zip_file.namelist():         
                        local_file = Path.cwd().joinpath(file)
                        if local_file.exists():           #파일 있으면 건너뜀
                            continue
                        with local_file.open('wb') as output:
                            for line in zip_file.open(file).readlines():
                                output.write(line)
            except BadZipFile:    
                return print(BadZipFile)   
    # ===============================================
    # 다운로드 파일
    # ===============================================
    class Web:
        @staticmethod
        def download_from_web(url:str, unzip:bool=False):
            if unzip is True: FilesF.Zipfiles.unzip_file(get(url).content)
            else:  return get(url).content
            
    # ===============================================
    # pickle 파일
    # ===============================================
    class Pickle:
        @staticmethod
        def save_to_pickle(data, file_name, data_path:Path=Path.cwd()):
            # print(data_path)
            # data_path/f'{file_name}.pickle'
            # print(f"{Path.cwd()}/{file_name}.pickle")
            with gzip.open(f"{data_path}/{file_name}.pickle", 'wb') as f:
                pickle.dump(data, f)
                
        @staticmethod  
        def load_from_pickle(file_name, data_path:Path=Path.cwd()):
            with gzip.open(f"{data_path}/{file_name}.pickle",'rb') as f:
                return pickle.load(f)
                
    
    # ===============================================
    #  parquet 파일
    # ===============================================
    class Parquet:
        @staticmethod
        def save_to_parquet(self, data_path:Path=Path.cwd()):  ## data_path :  변환할 파일이 있는 폴더
            parquet_paths = {} 
            for f in tqdm(sorted(list(data_path.glob('**/*.tsv')))):
                parquet_path= Path(f.parent, 'parquet')       
                parquet_paths[f'{f.parent.parts[-2]}{f.parent.parts[-1]}'] = parquet_path  # 저장소 경로 저장

                file_name = f.stem  + '.parquet'
                if not (parquet_path / file_name).exists():
                    try:
                        df = pd.read_csv(f, sep='\t', encoding='latin1', low_memory=False, error_bad_lines=False)
                        df.to_parquet(parquet_path / file_name)
                        print(parquet_path / file_name)
                    except Exception as e:
                        print(e, ' | ', f)
                print(parquet_paths)
                return self

    # ===============================================
    # CSV 파일
    # ===============================================
    class Csv:
        @staticmethod
        def read_csv(file_name, data_path:Path=Path.cwd()):
            return pd.read_csv(data_path/file_name, index_col=0, parse_dates=True)

    # ===============================================
    # excel 파일
    # ===============================================
    class Excel:
        @staticmethod
        def write_to_excel(df:pd.DataFrame, file_name, sheet_name,data_path:Path=Path.cwd()):
            df.to_excel(data_path/file_name, sheet_name)
            
        @staticmethod
        def read_from_excel(file_name, sheet_name,data_path:Path=Path.cwd()):
            return  pd.read_excel(data_path/file_name, sheet_name, index_col=0)

    # ===============================================
    # Json 파일
    # ===============================================
    class Json:
        @staticmethod
        def write_to_json(df:pd.DataFrame, file_name, data_path:Path=Path.cwd()):
            df.to_json(data_path/file_name)
            
        @staticmethod
        def read_from_json(file_name,  data_path:Path=Path.cwd()):
            return  pd.read_json(data_path/file_name)

    # ===============================================
    # HDFS 파일
    # ===============================================   
    class HDFS: 
        @staticmethod
        def save_to_HDFS(data, data_label, file_name, data_path:Path=Path.cwd()):
            with pd.HDFStore(f'{data_path}/{file_name}.h5') as store:
                store.put(data_label, data)
                print(store.info())
                
        @staticmethod        
        def load_HDFS(data_label, file_name, data_path:Path=Path.cwd()):
            with pd.HDFStore(f'{data_path}/{file_name}.h5') as store:
                return store[data_label]
        @staticmethod      
        def load_HDFS_keys(file_name, data_path:Path=Path.cwd()) -> dict:
            with pd.HDFStore(f'{data_path}/{file_name}.h5')as store:
                return store.keys()