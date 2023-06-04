from typing import Any, Optional,List
from dataclasses  import dataclass

from .filesf import FilesF

@dataclass
class Context:
        label:Optional[str] = None
        url:Optional[str] = None
        price:Optional[str] = None
        content:List[Any] = None

        dtype:Optional[str] = None
        botChatId:Optional[str] = None
        summary:List[Any] = None
        enable_translate:bool = False
        tokenize:bool = False
        enable_summary:bool = False
        

class Contents(list): 
    """
    import feedparser
    def make_content(rss_url):
      yield [Content(feed.summary, feed.title, feed.link) for feed in feedparser.parse(rss_url).entries]
          
    
    rss_url = 'https://back.nber.org/rss/releases.xml'
    
    contents = Contents()
    contents.addFromList(make_content(rss_url))
    
    contents.saveContentsDict()
    
    contents.loadContentsDict()
    """
    def __init__(self, context:Context=None):
        super().__init__()
        self.append(context)

    def saveContents(self, context:Context, fileName:str='contents_list'):
        sent_list=list(self.loadContents(fileName=fileName))
        print("sent_list:", sent_list)
        sent_list.append(context)
        print("context:", context)
        print("after sent_list:", sent_list)
        # print("save")
        # print(sent_list)
        # if len(sent_list)> 10000 : sent_list.pop()  # 버퍼 10000개로 제한
        FilesF.Pickle.save_to_pickle(sent_list, f'{fileName}')

        # return print('saved backup')

    def loadContents(self, fileName:str='contents_list'):
        try:
            print('loaded files')
            yield from FilesF.Pickle.load_from_pickle(f'{fileName}')
        except:
            print('loaded fail')
            yield from []
        

    
     
            