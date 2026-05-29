from WebpageSaver.API import API
from WebpageSaver.Crawler.Assets.Asset import Asset
from aiohttp import web
from WebpageSaver import config
from WebpageSaver.Crawler.Components.PageHTML import PageHTML
from pathlib import Path
import asyncio
import logging
import aiohttp_jinja2
import jinja2
import urllib

api = API()

routes = web.RouteTableDef()

@routes.get('/')
def ip(request: web.Request):
    return aiohttp_jinja2.render_template('index.html',request,{})

@routes.get('/page')
async def gpbid(request: web.Request):
    query = request.rel_url.query
    page_id = query.get('id')
    mode = query.get('mode', 'page')
    # page, url, meta, text_only, media_only
    pages = api.getPagesById(ids = [page_id], convert = False)
    if len(pages) == 0:
        return web.Response(status = 404)

    page = pages[0]

    match (mode):
        # Page display
        case 'page':
            remove_inline_styles = False
            disable_js = False
            disable_css = False
            disable_iframes = False
            remove_selectors = None

            # Encoding
            encoding = page.encoding
            if query.get('encoding') != None:
                encoding = query.get('encoding')

            text = page.getRootFile().read_text(encoding = encoding)
            html = PageHTML.from_html(text)

            if disable_js:
                html.clear_js()
            if remove_inline_styles:
                html.remove_inline_css()
            if disable_css:
                html.remove_css()
            if disable_iframes:
                html.remove_iframes()
            if remove_selectors:
                html.remove_selectors(remove_selectors)

            html.make_correct_links(page)
            #head_html = html.move_head()

            return web.Response(
                body = html.prettify(encoding = encoding), 
                content_type='text/html',
                charset = encoding
            )

        case 'url':
            p_url = query.get('url')
            new_url = Asset.getDecodedURL(p_url)
            redirect_url = page.getRelativeURL(new_url)

            return aiohttp_jinja2.render_template('url.html', request, {
                'url': redirect_url
            })

@routes.get('/page/asset')
async def gpa(request: web.Request):
    page_id = request.rel_url.query.get('id')
    path_id = request.rel_url.query.get('path', '')
    #path_id = urllib.parse.unquote(path_id)

    pages = api.getPagesById(ids = [page_id], convert = False)
    if len(pages) == 0:
        return web.Response(status = 404)

    page = pages[0]
    path = page.getAssetPathById(path_id)

    #decode_path = request.query.get('d') == '1'
    #if decode_path:
    #    path = base64.urlsafe_b64decode(path.encode('utf-8')).decode()

    assets_path = page.getAssetsDir()
    file: Path = assets_path.joinpath(path)

    try:
        file.absolute().relative_to(assets_path.resolve())
    except (ValueError, RuntimeError) as e:
        logging.exception(e)
        raise web.HTTPForbidden(reason="Access denied")

    if not file.is_file():
        raise web.HTTPNotFound(text="Not found file")

    return web.FileResponse(str(file))

@routes.get('/pages/save')
def spw(request: web.Request):
    return aiohttp_jinja2.render_template('save.html',request,{})

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
