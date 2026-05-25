from App.Crawler.Webdrivers.WebdriversRepo import WebdriversRepo
from App.Crawler.WebPage import WebPage
from App import config

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
                       webdriver_id: int = None):
        # TODO: w selection
        payload = list()
        webdriver = self.w_repo.getDefault()
        await webdriver.start()

        page = WebPage(
            url = url
        )
        page.init(config.webpages_dir)
        browser_page = await webdriver.openPage(page)
        await browser_page.goto(page.url)
        await browser_page.integrate(page)
        payload.append(page.model_dump(exclude_none = True))

        return payload
