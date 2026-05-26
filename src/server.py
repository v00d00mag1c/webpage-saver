from WebpageSaver.Crawler.Webdrivers.WebdriversRepo import WebdriversRepo
from WebpageSaver.API import API
from aiohttp import web
from WebpageSaver import config
import asyncio
import logging

api = API()

async def get_webdrivers(request: web.Request):
    return web.json_response(api.getWebdrivers())

async def save_page(request: web.Request):
    inputs = await request.post()
    url = inputs.get('url')

    payload = await api.savePage(url = url)

    return web.json_response(payload)

async def get_pages(request: web.Request):
    page_id = request.rel_url.query.get('id')
    if page_id != None:
        return web.json_response(api.getPages())

    return web.json_response(api.getPages())

async def get_page_by_id(request: web.Request):
    page_id = request.rel_url.query.get('id')
    pages = api.getPagesById(ids = [page_id], convert = False)

    if len(pages) == 0:
        return web.Response(status = 404)

    page = pages[0]

    return web.Response(body = page.getRootFile().read_text(), content_type='text/html')

async def main():
    host = '127.0.0.1'
    port = 7514

    app = web.Application()
    app.router.add_get('/api/webdrivers', get_webdrivers)
    app.router.add_get('/pages', get_pages)
    app.router.add_get('/page', get_page_by_id)
    app.router.add_get('/api/pages', get_pages)
    app.router.add_post('/api/pages/save', save_page)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host = host,
        port = port
    )

    await site.start()

    logging.info('server opened on {0}:{1}'.format(host, port))

    while True:
        await asyncio.sleep(3600)

asyncio.run(main())
