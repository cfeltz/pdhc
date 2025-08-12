import dataclasses
import fastapi
import random

import pdhc.config

CONF = pdhc.config.CONF


@dataclasses.dataclass
class DVR:
    FriendlyName: str
    ModelNumber: str
    FirmwareName: str
    TunerCount: int
    FirmwareVersion: str
    DeviceID: str
    DeviceAuth: str
    BaseURL: str
    LineupURL: str
    Manufacturer: str


async def discover(request: fastapi.Request):
    device_id = random.randint(10_000_000, 90_000_000)

    host = request.headers.get("host", "localhost")

    tuner_count = len(request.app.state.channels) * 3

    return DVR(
        FriendlyName=CONF['DEFAULT']['friendly_name'],
        ModelNumber="HDTC-2US",
        FirmwareName="hdhomeruntc_atsc",
        TunerCount=tuner_count,
        FirmwareVersion="20150826",
        DeviceID=str(device_id),
        DeviceAuth="test1234",
        BaseURL=f"http://{host}",
        LineupURL=f"http://{host}/lineup.json",
        Manufacturer="Silicondust"
    )

def register_route(router):
    router.add_api_route('/discover.json', discover, methods=['GET'], response_model=DVR)
