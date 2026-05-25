from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import logging

class WebPage(BaseModel):
    # Page data

    title: str = Field(default = None)
    taken: float = Field(default = None)

    # URLs

    url: str = Field()
    base_url: str = Field(default = None)
    relative_url: str = Field(default = None)

    # Mental disorders
    identify: str = Field(default = None)
    root_directory: str = Field(default = None, exclude = True)
    root_file: str = Field(default = 'index.html')
    assets_directory: str = Field(default = 'assets')
    encoding: str = Field(default = 'utf-8')
    assets_links: dict = Field(default = {})

    def init(self, path: Path):
        self.setDate()
        self._create(path)

    def setEncoding(self, val: str):
        '''
        Sets the encoding.
        '''
        #print('set encoding to {0}'.format(val))

        self.encoding = val

    def setDate(self) -> str:
        '''
        Creates ID.
        '''
        _now = datetime.now()
        self.identify = f"{_now.strftime('%Y-%m-%d-%H-%M-%S-%S-%f')}"
        self.taken = _now.timestamp()

        return self.identify

    def getDir(self) -> Path:
        '''
        Returns directory of the page in storage.
        '''
        return self.root_directory.joinpath(self.identify)

    def getRootFile(self) -> Path:
        '''
        Returns "index.html" path.
        '''
        return self.getDir().joinpath(self.root_file)

    def getAssetsDir(self) -> Path:
        '''
        Returns assets dir.
        '''
        return self.getDir().joinpath(self.assets_directory)

    def _create(self, root_dir: Path):
        '''
        Creates dir in storage, index.html and assets.
        '''
        self.root_directory = root_dir

        new_dir = self.getDir()
        new_dir.mkdir(exist_ok=True)

        index_file = open(str(self.getRootFile()), 'w', encoding = self.encoding)
        index_file.close()
        self.getAssetsDir().mkdir(exist_ok=True)

    def write(self, html: str):
        '''
        Writes changes to index.html
        '''
        #_detect = chardet.detect(html.encode('utf-8', errors='ignore'))

        #self.setEncoding(_detect.get('encoding'))

        try:
            with open(self.getRootFile(), 'w', encoding = self.encoding) as file:
                file.write(html)
        except Exception as e:
            logging.log("Error when writing file, encoding is {0}, trying UTF-8. ".format(self.encoding))
            logging.exception(e)

            with open(self.getRootFile(), 'w', encoding = 'utf-8') as file:
                file.write(html)

    def getAssetByUrl(self, url: str):
        '''
        Unwraps asset by its URL
        '''
        asset = None
        for attempt in range(0, 4):
            __link = None
            match (attempt):
                case 0:
                    __link = Asset.encode_url(url)
                case 1:
                    __link = Asset.encode_url(url.strip())
                case 2:
                    __link = url.replace('https', 'http', 1)
                case 3:
                    __link = Asset.encode_url(url.replace('http', 'https', 1))

            if self.assets_links.get(__link) != None:
                return self.assets_links.get(__link)

        return asset
