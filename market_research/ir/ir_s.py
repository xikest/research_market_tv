import os
from market_research.analysis import TextAnalysis


class SONY_IR():
    def __init__(self):
        self.tas = TextAnalysis()
        
        self.cleaning_words = [  #사전 필터링하는 단어
                            "half","fy2021","fy2020", "month","way", "input","earnings",
                            "forecast","please","terms","market","g","ns", "unit","assets",
                            "fy2022","levels","q","fy2023","numbers","result","units",
                            "factors","costs","ss","q1","part",'segment', 'quarter', 
                            'statements', 'business', 'question', 'yen', 'year', 'sony', 'results',
                            "end","q2","questioner",
                            "session","fy2024",
                            # "sale","plan","capacity","growth","demand",
                            "outlook","increase","investment",
                            "example","rate","flow","time","a2","a1","sfh","r","dtc", "statement",
                            "plan", "tax", "value", "term","capital", "growth","company","group", "service",
                            "risk","profit","minotrity"
                        ]     
        
        
        self.replacement_mapping = {  #사전에 교체하는 단어
                            "games": "game",
                            "plans": "plan",
                            "sensors": "sensor",
                            "changes": "change",
                            "risks": "risk",
                            "services": "service",
                            "margins": "margin",
                            "profits": "profit",
                            "wafers": "wafer",
                            "sizes": "size",
                            "customers": "customer",
                            "applications": "application",
                            "shortages": "shortage",
                            "expenses": "expense",
                            "sales":"sale",
                            "titles":"title",
                            "conditions":"condition",
                            "prices":"price",
                            "investments":"investment",
                            "rates":"rate",
                            "inventories":"inventory",
                            "uncertainties":"uncertainty",
                            "cameras":"camera",
                            "opportunities":"opportunity",
                            "volumes":"volume",
                            "costs":"cost",
                            "technologies":"technology",
                            "employees":"employee",
                            "companies":"company",
                            "creators":"creator",
                            "challenges":"challenge",
                            "businesses":"business",
                            "years":"year",
                            "electronics":"electronic",
                            "strategies":"strategy",
                            "electronics":"electronic",
                            "targets":"target",
                            "statements":"statement"
                        }
        pass
    
    
    


    def get_ir_script(self, direct_download=True) -> dict:
        
        urls = []
        filenames = []
        
        base_url = "https://www.sony.com/en/SonyInfo/IR/library/presen/er/pdf/"
        years = range(19, 25)
        quarters = range(1, 5)
        
        for year in years:
            for quarter in quarters:
                filename = f"{year}q{quarter}_qa.pdf"
                url = f"{base_url}{filename}"
                urls.append(url)
                filenames.append(filename)
        
        base_url = "https://www.sony.com/en/SonyInfo/IR/library/presen/strategy/pdf"
        years = range(2020, 2024)
        for year in years:
            for quarter in quarters:
                url = f"{base_url}/{year}/qa_E.pdf"
                urls.append(url)
                filenames.append(filename)
                
        if direct_download:        
            files_to_download = [url for url, filename in zip(urls, filenames) if filename not in filenames]     
        else: 
            files_path = self.tas.read_files_from_inputpath(docs_type="pdf")
            existing_files = {file_path.name for file_path in files_path}  # 존재하는 파일 이름 세트 생성
            files_to_download = [url for url, filename in zip(urls, filenames) if filename not in existing_files]

        if files_to_download:
            filepath_list = self.tas.download_pdfs(files_to_download)
            
        comments_dict = {}
        files_path_dict = {}
        for file_path in filepath_list:
            key = os.path.basename(file_path).replace(".pdf", "").replace("_qa", "").upper()
            comment = self.tas.pdf_to_text(file_path)
            for original, replacement in self.replacement_mapping.items():
                comment = comment.replace(original, replacement)
            comments_dict[key] = comment
            files_path_dict[key] = file_path
                    
        return comments_dict, files_path_dict
        
        