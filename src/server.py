from App.Crawler.Webdrivers.WebdriversRepo import WebdriversRepo
from App.API import API
from aiohttp import web
from App import config
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

    logging.info('server opened on {0}:{1}'.format(host, port))

    while True:
        await asyncio.sleep(3600)

asyncio.run(main())
