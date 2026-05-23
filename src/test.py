from App.Crawler.Webdrivers.WebdriversRepo import WebdriversRepo
from App.Crawler.Webdrivers.Webdriver import Webdriver
from App import app
import argparse
import asyncio

async def _main():
    '''parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--html')

    args = parser.parse_args()

    if args.url:
        urls = [args.url]

        downloader = Downloader()
        await downloader.start_webdriver()
    else:
        raise '''

    repo = WebdriversRepo()
    #repo.add(Webdriver(
    #    executable_path = ''
    #))
    webdriver = repo.getDefault()
    await webdriver.start()

    print(webdriver)

asyncio.run(_main())
