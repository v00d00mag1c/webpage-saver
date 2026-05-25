from WebpageSaver import config
from typing import Generator
from WebpageSaver.Crawler.Webdrivers.Webdriver import Webdriver

class WebdriversRepo:
    _list: list

    def __init__(self):
        self._list = self.getAll()

    def _getWebdriversList(self):
        return self._list

    def _getCurrentWebdriverIndex(self):
        return config.get('webdrivers.current', 0)

    def _setCurrentWebdriverIndex(self, id: int):
        config.set('webdrivers.current', id)

    def getAll(self) -> Generator[Webdriver]:
        _list = config.get('webdrivers')
        if _list == None or type(_list) != list:
            return []

        for i in _list:
            yield Webdriver.model_validate(i)

    def getDefault(self) -> Webdriver:
        return list(self.getAll())[self._getCurrentWebdriverIndex()]

    def add(self, webdriver: Webdriver):
        similar = None
        _list = list(self.getAll())
        for w in _list:
            if w.executable_path == webdriver.executable_path:
                similar = w

            break

        if similar == None:
            _list.append(webdriver.model_dump(exclude_none = True))
            config.set('webdrivers', _list)
            self._setCurrentWebdriverIndex(len(_list) - 1)
        else:
            self._setCurrentWebdriverIndex(_list.index(w))
