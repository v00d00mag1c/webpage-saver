from pydantic import Field, BaseModel
from WebpageSaver import config
from playwright.async_api import Playwright, async_playwright
from WebpageSaver.Crawler.Components.UserAgent import UserAgent
from WebpageSaver.Crawler.WebPage import WebPage
from WebpageSaver.Crawler.Webdrivers.WebdriverPage import WebdriverPage
import platform
import logging

class Webdriver(BaseModel):
    was_started: bool = Field(default = False)
    path: str = Field(default = None)
    platform: str = Field(default = 'win')
    executable_path: str = Field(default = None)
    webdriver_path: str = Field(default = None)
    user_data: str = Field(default = None)
    user_agent: str = Field(default = None)

    async def start(self):
        if self.was_started == True:
            return None

        size = None
        #if i.get('webdriver.sizes') != None:
        #    size = i.get('webdriver.sizes').split(',')

        self._playwright = await async_playwright().start()

        logging.log(logging.INFO, 'launching browser')

        try:
            if size != None:
                self.viewport = {"width": int(size[0]), "height": int(size[1])}
        except Exception as e:
            logging.log(logging.ERROR, e)

        self._browser = await self._launch_browser()
        self._context = await self._browser.new_context(
            #viewport = self.viewport,
            user_agent = self.getUserAgentString(),
        )

    async def _launch_browser(self):
        #i.get('webdriver.headless')
        is_headless = False
        args = [
            '--start-maximized',
            '--start-fullscreen',
            '--headless',
            '--no-sandbox',
            '--user-agent={0}'.format(self.getUserAgentString())
        ]

        if self.user_data != None:
            args.append('--user_data=' + self.user_data)

        #for argument in i.get('webdriver.args'):
        #    args.append(argument)

        executable_path = self.executable_path
        if executable_path == None:
            executable_path = str(self.get_shell())

        return await self._playwright.chromium.launch(
            executable_path = executable_path,
            args = args,
            headless = is_headless
        )

    def getUserAgentString(self) -> str:
        '''
        Returns UserAgent string.
        '''
        _passed = config.get('web.crawler.user_agent')
        if _passed == None:
            return UserAgent.generate().string

        return _passed.string

    async def stop(self):
        '''
        Stops browser emulator.
        '''
        for i in ['_context', '_browser', '_playwright']:
            if hasattr(self, i):
                if i == '_playwright':
                    getattr(self, i).close()
                setattr(self, i, None)

        self._playwright = None

    async def openPage(self, page: WebPage):
        new_page = WebdriverPage()
        new_page._page = await self._context.new_page()

        logging.info('opened page {0}'.format(page.url))
        #await page.setViewport(self.viewport)

        return new_page

    def getShell(self):
        return self.executable_path.joinpath('chrome').joinpath('chrome-headless-shell.exe')

    def getWebdriver(self):
        return self.webdriver_path.joinpath('chromedriver.exe')

    @staticmethod
    def _get_platform():
        version = ['', '']
        system_type = platform.system().lower()
        architecture = platform.machine().lower() 

        if architecture in ['x86_64', 'amd64']:
            version[1] = '64'
        elif architecture in ['i386', 'i686', 'x86']:
            version[1] = '32'
        elif architecture in ['arm64', 'aarch64']:
            version[1] = 'arm64'
        else:
            version[1] = architecture

        match system_type:
            case "darwin":
                if architecture in ['arm64', 'aarch64']:
                    version[1] = "arm64"
                else:
                    version[1] = "x64"

                version[0] = 'mac-'
            case "windows":
                version[0] = 'win'
            case _:
                version[0] = 'win'

        return ''.join(version)
