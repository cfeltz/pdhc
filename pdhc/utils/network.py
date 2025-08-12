import aiohttp

from pdhc import objects

import pdhc.config

CONF = pdhc.config.CONF


async def get_channels():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:%d/lineup/' % int(CONF['DEFAULT']['proxy_port'])) as response:
            response_json = await response.json()
            channels = []
            for channel in response_json:
                channels.append(objects.Channel(**channel))

            return channels

async def get_m3u8_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            return text
