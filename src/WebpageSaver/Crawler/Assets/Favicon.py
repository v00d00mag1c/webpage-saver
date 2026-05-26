from WebpageSaver.Crawler.Assets.Asset import Asset
from pydantic import Field
from typing import Optional

class Favicon(Asset):
    sizes: Optional[str] = Field(default = None)
