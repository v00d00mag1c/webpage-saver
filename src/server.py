from WebpageSaver.API import API
from WebpageSaver.Crawler.Assets.Asset import Asset
from aiohttp import web
from WebpageSaver import config
from WebpageSaver.Crawler.Components.PageHTML import PageHTML
from pathlib import Path
from datetime import datetime
import asyncio
import logging
import aiohttp_jinja2
import jinja2
import urllib

api = API()

routes = web.RouteTableDef()

def check_path(maximum_directory: Path, path: Path):
    path.absolute().relative_to(maximum_directory.resolve())

    if not path.exists():
        raise FileNotFoundError()

    if not path.is_file():
        raise FileNotFoundError()

@routes.get('/')
def ip(request: web.Request):
    return aiohttp_jinja2.render_template('index.html',request,{})

@routes.get('/page')
async def gpbid(request: web.Request):
    query = request.rel_url.query
    page_id = query.get('id')
    mode = query.get('mode', 'page')

    if mode not in ['page', 'url', 'meta', 'media']:
        return web.HTTPNotFound(body = 'Invalid mode')

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

        case 'meta':

            return aiohttp_jinja2.render_template('page_info.html', request, {
                'page': page,
                'taken': datetime.fromtimestamp(page.taken).strftime("%d/%m/%Y, %H:%M:%S"),
                'linked': page.getLinkedPages()
            })

        case 'url':
            p_url = query.get('url')
            new_url = Asset.getDecodedURL(p_url)
            redirect_url = page.getRelativeURL(new_url)

            return aiohttp_jinja2.render_template('url.html', request, {
                'url': redirect_url,
                'id': page.identify
            })

@routes.get('/page/asset')
async def gpa(request: web.Request):
    page_id = request.rel_url.query.get('id')
    path_id = request.rel_url.query.get('path', '')
    #path_id = urllib.parse.unquote(path_id)

    pages = api.getPagesById(ids = [page_id], convert = False)
    if len(pages) == 0:
        return web.HTTPNotFound(body = 'Not found page')

    page = pages[0]
    req = page.getAssetById(path_id)
    if req == None:
        return web.HTTPNotFound(body = 'Not found asset')

    path = page.getAssetPathById(path_id)
    file_name = req.asset.getName()

    #decode_path = request.query.get('d') == '1'
    #if decode_path:
    #    path = base64.urlsafe_b64decode(path.encode('utf-8')).decode()

    assets_path = page.getAssetsDir()
    file: Path = assets_path.joinpath(path)

    try:
        check_path(assets_path, file)
    except (ValueError, RuntimeError) as e:
        logging.exception(e)
        return web.HTTPForbidden(reason="Access denied")

    if not file.is_file():
        return web.HTTPNotFound(text="Not found file")

    return web.FileResponse(str(file), headers = {
        'Content-Disposition': f'attachment; filename="{file_name}"',
        'Content-Type': req.getContentType()
    })

@routes.get('/page/screenshot')
def gpsbid(request):
    page_id = request.rel_url.query.get('id')
    filename = request.rel_url.query.get('file')
    pages = api.getPagesById(ids = [page_id], convert = False)

    if len(pages) == 0:
        return web.HTTPNotFound(body = 'Not found page')

    page = pages[0]
    screenshot = page.getThumbsDir().joinpath(filename)

    try:
        check_path(page.getThumbsDir(), screenshot)
    except (ValueError, RuntimeError) as e:
        logging.exception(e)
        return web.HTTPForbidden(reason="Access denied")

    return web.FileResponse(str(screenshot), headers = {
        'Content-Type': 'image/jpeg'
    })

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
    link_to = inputs.get('link_to')
    ps = api.getPagesById(ids = [link_to], convert = False)

    if len(ps) == 0:
        return web.HTTPNotFound(body = 'Not found page to link')

    payload = await api.savePage(url = url, link_pages = ps)

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

@routes.patch('/api/page')
async def epbid(request: web.Request):
    page_id = request.rel_url.query.get('id')
    new_taken = request.rel_url.query.get('new_taken')
    new_name = request.rel_url.query.get('new_name')
    new_url = request.rel_url.query.get('new_url')
    #api.editPageById(id = page_id)

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
