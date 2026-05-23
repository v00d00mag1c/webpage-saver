from App.Crawler.Webdrivers.WebdriversRepo import WebdriversRepo
from App.Crawler.WebPage import WebPage
from aiohttp import web
from App import config
import asyncio

webdrivers_repo = WebdriversRepo()

async def get_webdrivers(request):
    data = list()
    for wd in webdrivers_repo.getAll():
        data.append(wd.model_dump(exclude_none = True))

    return web.json_response(
        data = data,
        content_type = 'application/json'
    )

async def save_page(request: web.Request):
    inputs = await request.post()
    url = inputs.get('url')
    data = {}

    # TODO: w selection
    webdriver = webdrivers_repo.getDefault()
    await webdriver.start()

    page = WebPage(
        url = url
    )
    page.create_dir(config.webpages_dir)
    await webdriver.openPage(page)

    return web.json_response(
        data = page.model_dump(exclude_none = True),
    )

async def main():
    host = '127.0.0.1'
    port = 7514

    app = web.Application()
    app.router.add_get('/api/webdrivers', get_webdrivers)
    app.router.add_post('/api/pages/save', save_page)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host = host,
        port = port
    )

    await site.start()

    print('server opened on {0}:{1}'.format(host, port))

    while True:
        await asyncio.sleep(3600)

asyncio.run(main())
