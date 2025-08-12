import contextlib
import fastapi

from pdhc.api import discover 
from pdhc.api import lineup 
from pdhc.api import stream 
from pdhc.api import xmltv 
from pdhc.utils import network 


ROUTER = fastapi.APIRouter()

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    channels = await network.get_channels()
    print(channels)
    app.state.channels = channels
    yield

discover.register_route(ROUTER)
lineup.register_route(ROUTER)
stream.register_route(ROUTER)
xmltv.register_route(ROUTER)
