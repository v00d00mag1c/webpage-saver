from pydantic import Field, BaseModel
from typing import Any
from WebpageSaver import app
import urllib

class Asset(BaseModel):
    url: str = Field(default = None)
    bs_node: Any = Field(default = None, exclude = True)

    # we know that contents are downloaded so it will available in the displayment
    def replace(self):
        _node = self.get_node()

        if _node != None and (_node.get('href') or _node.get('src')):
            _node['data-__to_orig'] = self.url
            _key = 'href'

            if _node.get('src') != None and _node.get('src') != '':
                _key = 'src'

            _node['data-__to_orig_key'] = _key
            _node[_key] = ''

    def decompose(self):
        self.bs_node.decompose()

    def set_url(self, href: str):
        if not href.startswith('http'):
            if href.startswith('data:') == True:
                return

        self.url = href

    def get_url(self):
        return self.url

    def has_url(self):
        return self.url != None

    async def download(self, dir: str):
        await self.download_function(dir)

    async def download_function(self, dir, name: str = None):
        if name == None:
            name = self.get_encoded_url()

        if self.url == None:
            print('no url...')
            return

        _item = app.DownloadManager.addURL(self.url, dir, str(name))
        await _item.start()

    def getEncodedURL(self):
        return urllib.parse.quote(self.url).replace('/', '%')

    @staticmethod
    def getDecodedURL(url):
        return urllib.parse.unquote(url).replace('%', '/')

    @staticmethod
    def encodeURL(url):
        return urllib.parse.quote(url).replace('/', '%')

    def set_node(self, bs_node):
        self.bs_node = bs_node

    def get_node(self):
        return self.bs_node
