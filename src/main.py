from Crawler.Downloader import Downloader
import argparse
import asyncio

async def _main():
    parser = argparse.ArgumentParser(
        prog = 'Webpage Saver',
    )
    parser.add_argument('-u', '--url')
    parser.add_argument('--html')

    args = parser.parse_args()

    if args.url:
        urls = [args.url]

        downloader = Downloader()
        await downloader.start_webdriver()
    else:
        raise 

asyncio.run(_main)
