import asyncio
import argparse

async def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--executable_path')
    args = parser.parse_args()

asyncio.run(_main())
