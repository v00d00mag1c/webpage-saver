from WebpageSaver.API import API
from aiohttp import web
from WebpageSaver import config
import asyncio
import logging
import aiohttp_jinja2
import jinja2

api = API()

routes = web.RouteTableDef()

@routes.get('/')
def ip(request: web.Request):
    return aiohttp_jinja2.render_template('index.html',request,{})

@routes.get('/page')
async def gpbid(request: web.Request):
    page_id = request.rel_url.query.get('id')
    print(page_id)
    pages = api.getPagesById(ids = [page_id], convert = False)

    if len(pages) == 0:
        return web.Response(status = 404)

    page = pages[0]

    return web.Response(body = page.getRootFile().read_text(), content_type='text/html')

@routes.get('/pages/save')
def spw(request: web.Request):
    return aiohttp_jinja2.render_template('save.html',request,{})

@routes.get('/pages/url')
def sud(request: web.Request):
    return aiohttp_jinja2.render_template('url.html',request,{})

@routes.get('/api/webdrivers')
async def gw(request: web.Request):
    return web.json_response(api.getWebdrivers())

@routes.post('/api/pages/save')
async def sp(request: web.Request):
    inputs = await request.post()
    url = inputs.get('url')

    payload = await api.savePage(url = url)

    return web.json_response(payload)

@routes.get('/api/pages')
async def gp(request: web.Request):
    page_id = request.rel_url.query.get('id')
    if page_id != None:
        return web.json_response(api.getPagesById(ids = [page_id]))

    return web.json_response(api.getPages())

@routes.delete('/api/page')
async def dpbid(request: web.Request):
    page_id = request.rel_url.query.get('id')
    api.deletePagesById(id = page_id)

    return web.Response(body = 1, content_type='text/html')

async def main():
    host = '127.0.0.1'
    port = 7514

    app = web.Application()
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader(config.cwd.joinpath('web').joinpath('templates')))

    app.router.add_routes(routes)

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
