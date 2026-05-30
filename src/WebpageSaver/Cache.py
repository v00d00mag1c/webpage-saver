from pathlib import Path
from peewee import *
from WebpageSaver import config
from WebpageSaver.Crawler.WebPage import WebPage
import logging
import json

db = SqliteDatabase(str(config.data.joinpath('cache.db')))

class BaseModel(Model):
    class Meta:
        database = db

class Page(BaseModel):
    title = TextField()
    path_to = TextField(unique=True)
    taken_at = FloatField()
    #url = TextField()
    #relative_url = TextField()
    data = TextField(null = False)

    @classmethod
    def fromModel(cls, model: WebPage, path_to: str):
        new = Page()
        new.title = model.title
        new.path_to = path_to
        new.taken_at = model.taken
        #new.url = model.url
        #new.relative_url = model.relative_url
        new.data = json.dumps(model.model_dump(exclude_none = True, exclude_defaults = True), ensure_ascii = False)

        return new

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        logging.info('indexated page {0}'.format(self.path_to))

    def toModel(self):
        return WebPage.fromPath(self.path_to)

class Cache:
    '''
    List of webpages from data/webpages
    '''

    def __init__(self):
        db.connect()
        db.create_tables([Page])

        self.indexate()

    def getPages(self):
        return Page.select().order_by(Page.taken_at.desc())

    def getList(self):
        _list = config.get('webpages.list')
        if _list == None:
            return []

        return _list

    def indexate(self):
        paths = list()
        for path in Path(config.webpages_dir).rglob('*'):
            if path.name == 'data.json':
                paths.append(str(path.relative_to(config.webpages_dir).parent))

        ps = Page.select().where(Page.path_to.in_(paths))
        exist_paths = list()

        for item in ps:
            exist_paths.append(item.path_to)

        for path in paths:
            if path not in exist_paths:
                try:
                    p = WebPage.fromPath(path)
                    m = Page.fromModel(p, path)
                    m.save()
                except Exception as e:
                    logging.exception(e)
