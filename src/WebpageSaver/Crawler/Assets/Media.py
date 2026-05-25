from WebpageSaver.Crawler.Assets.Asset import Asset
from pydantic import Field
from typing import Optional

class Media(Asset):
    tagName: str = Field(default = None)
    alt: str = Field(default = None)
