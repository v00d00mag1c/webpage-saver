from WebpageSaver.Crawler.Components.GotRequest import GotRequest
from WebpageSaver.Crawler.WebPage import WebPage
from WebpageSaver.Crawler.Webdrivers.WebdriverPage import WebdriverPage
from WebpageSaver.Crawler.Components.PageHTML import PageHTML
from WebpageSaver.Crawler.Screenshot import Screenshot
import asyncio

class Crawler:
    async def register(self, page: WebPage, webdriver_page):
        #_roles = ['crawler.asset.download']
        #self.i = Increment()

        #self.log('registing page')
        _orig_dir = page.getAssetsDir()

        async def _request(request):
            webdriver_page.got_assets.append(GotRequest(
                url = request.url,
                request = request,
                done = False
            ))

        async def _response(response):
            request = None
            for item in webdriver_page.got_assets:
                if item.url_matches(response.url):
                    request = item

            if request == None:
                return

            #self.log('request {0}, method {1}'.format(response.url, request.request.method))

            if request.request.method == 'GET':
                try:
                    _url = response.url
                    if request.request.redirected_from:
                        self.log('assets: redirected from {0}'.format(_url), role = _roles)
                        _url_r = request.request.redirected_from.url
                        for _item in page._page.got_assets:
                            if _item.url_matches(_url_r):
                                request = _item

                    request.asset = Asset(url=_url)
                    _i = self.i.getIndex()
                    #_dir = _orig_dir.joinpath(request.asset.get_encoded_url())
                    page.html.assets_links[request.asset.get_encoded_url()] = _i

                    _dir = _orig_dir.joinpath(str(_i))
                    buffer = await response.body()
                    with open(str(_dir), 'wb+') as _file:
                        _file.write(buffer)

                    self.log('assets: downloaded {0}'.format(_url), role = _roles)
                except Exception as e:
                    self.log_error('error downloading asset {0}'.format(_url), role = list(_roles))

            request.done = True

        #webdriver_page._page.on('request', _request)
        #webdriver_page._page.on('response', _response)

    async def crawl(self, page: WebPage, webdriver_page: WebdriverPage):
        await webdriver_page.integrate(page)

        #download_assets = i.get('crawler.download_other_assets')

        #await asyncio.sleep(i.get('crawler.sleep.before_crawl'))

        page.setEncoding(await webdriver_page.get_encoding())

        #if i.get('scroll_down'):
        #    await page._page.scroll_down(i.get('web.crawler.scroll_down.cycles'), i.get('web.crawler.scroll_down.'))

        #await asyncio.sleep(i.get('crawler.sleep.before_html'))
        #await page._page._page.wait_for_timeout(i.get('crawler.network_timeout'))

        if True:
            await Screenshot().make_viewport(page, webdriver_page)
            await Screenshot().make_fullscreen(page, webdriver_page)

        #if i.get('crawler.screenshot.save'):
            #self.log('making screenshot...')

            #thumbs = await MakeScreenshot().execute({
            #    'page': page
            #})

            #for thumb in thumbs.getItems():
            #    page.add_thumbnail(thumb)

        html = PageHTML.from_html(await webdriver_page.get_html())
        if page.encoding == None:
            page.setEncoding(html.encoding)

        for meta in html.get_meta(page):
            page.meta.append(meta)

        for link in html.get_links(page):
            page.links.append(link)

        for link in html.get_urls(page):
            page.hyperlinks.append(link)

        for link in html.get_media(page):
            page.media.append(link)

        results = dict()
        #for key in ['get_favicons', 'get_media', 'get_downloadable_links', 'get_scripts']:
        #    if results.get(key) == None:
        #        results[key] = list()

        #    self.log('getting {0}...'.format(key[4:]))

        #    for item in getattr(html, key)(page):
        #        found_asset = None

                #match (key):
                #    case 'get_scripts':
                #        if remove_scripts:
                #            item.decompose()
                #            continue

        #        for asset in page._page.got_assets:
        #            if item.url and asset.url_matches(item.url):
        #                found_asset = asset

        #        if found_asset == None and item.has_url():
        #            if download_assets == False:
        #                continue

        #            try:
        #                await item.download_function(page.html.get_assets_dir(), self.i.getIndex())
        #            except Exception as e:
        #                self.log_error(e, exception_prefix='assets downloading error: ', role = ['crawler.asset.download'])

        #        item.replace()
        #        results[key].append(item)

        #for item in results.get('get_favicons'):
        #    page.favicons.append(item)

        #if remove_scripts:
        #    try:
        #        html.clear_js()
        #    except Exception as e:
        #        self.log_error(e)

        page.write(html.prettify())
        page.saveData()

        #await self._after_crawl(page, i)
