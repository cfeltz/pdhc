import asyncio
import fastapi
import logging
import uvicorn

from pdhc.utils import network
from pdhc import api

logger = logging.getLogger('uvicorn.error')  # or setup your own logger

import pdhc.config

CONF = pdhc.config.CONF
LOG = logging.getLogger(__name__)


app = fastapi.FastAPI(lifespan=api.lifespan)
app.include_router(api.ROUTER)

async def main():
    uvicorn_config = uvicorn.Config(app, host='0.0.0.0')
    server = uvicorn.Server(uvicorn_config)
    await server.serve()

if __name__ == '__main__':
    asyncio.run(main())