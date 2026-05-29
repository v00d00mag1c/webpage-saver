from WebpageSaver.Crawler.Assets.Asset import Asset
from pydantic import BaseModel, Field
from typing import Any
import logging

class GotRequest(BaseModel):
    url: str = Field(default = None)
    asset: Asset = Field(default = None)
    request: Any = Field(default = None, exclude = True)
    response: Any = Field(default = None, exclude = True)
    done: bool = Field(default = False)

    def url_matches(self, url: str):
        _s = self.url.replace('https://', '').replace('http://', '')
        _f = ''

        try:
            _f = url.replace('https://', '').replace('http://', '')
        except Exception as e:
            logging.exception(e)

        return _s == _f
