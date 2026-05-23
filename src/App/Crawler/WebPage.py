from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path

class WebPage(BaseModel):
    url: str = Field()
    title: str = Field(default = None)

    def create_dir(self, root_dir: Path):
        name = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%S-%f')}"
        new_dir = root_dir.joinpath(name)
        print(new_dir)
