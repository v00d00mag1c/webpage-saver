from WebpageSaver.Crawler.Webdrivers.WebdriversRepo import WebdriversRepo
from WebpageSaver.Crawler.WebPage import WebPage
from WebpageSaver.Crawler.Crawler import Crawler
from WebpageSaver import config
from WebpageSaver.Cache import Cache, Page

cache = Cache()

class API:
    '''
    API Service
    '''

    def __init__(self):
        self.w_repo = WebdriversRepo()

    def getWebdrivers(self) -> list:
        payload = list()
        for wd in self.w_repo.getAll():
            payload.append(wd.model_dump(exclude_none = True))

        return payload

    async def savePage(self, 
                       url: str, 
                       webdriver_id: int = None,
                       link_pages: list[WebPage] = None):
        # TODO: w selection
        crawler = Crawler()

        payload = list()
        webdriver = self.w_repo.getDefault()
        await webdriver.start()

        page = WebPage(
            url = url
        )
        page.init(config.webpages_dir)

        if link_pages:
            for p in link_pages:
                p.linked_pages.append(page.identify)
                p.saveData()

        browser_page = await webdriver.openPage(page)

        await crawler.register(page, browser_page)
        await browser_page.goto(page.url)
        await browser_page.integrate(page)
        await crawler.crawl(page, browser_page)

        # Saving to cache
        m = Page.fromModel(page, page.path_to)
        m.save()

        page.saveData()

        payload.append(page.model_dump(exclude_none = True))

        return payload

    def getPages(self):
        payload = list()
        for page in cache.getPages():
            payload.append(page.toModel().dump())

        return payload

    def getPagesById(self, ids: list[str], convert: bool = True) -> list[WebPage]:
        payload = list()
        for item in Page.select().where(Page.path_to.in_(ids)):
            if convert == True:
                payload.append(item.toModel().dump())
            else:
                payload.append(item.toModel())

        return payload

    def deletePagesById(self, id: str) -> None:
        for item in Page.select().where(Page.path_to == id):
            item.delete_instance()
