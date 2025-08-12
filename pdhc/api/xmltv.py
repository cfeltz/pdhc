from dataclasses import dataclass
from datetime import datetime, timezone
from fastapi import templating
import fastapi
import zoneinfo

import pdhc.config

CONF = pdhc.config.CONF


@dataclass
class ChannelSimplified:
    id: int
    name: str

def build_simplified_channels(channels):
    simplified_channels = []
    for channel in channels:
        simplified_channels.append(
            ChannelSimplified(
                id=channel.number,
                name=channel.name
            )
        )
    
    return simplified_channels

@dataclass
class Program:
    hour: str
    datetime_start: str
    datetime_end: str

def build_programs():
    programs = []
    now = datetime.now(zoneinfo.ZoneInfo('America/Chicago'))

    for hour in range(24):
        start = now.replace(hour=(hour+1) % 24, minute=0, second=0, microsecond=0)
        end = start.replace(minute=59, second=59, microsecond=999000)

        date_time_start = start.strftime("%Y%m%d%H%M%S %z")
        date_time_end = end.strftime("%Y%m%d%H%M%S %z")
        hour_str = start.strftime("%-I%p") 

        programs.append(
            Program(
                hour=hour_str,
                datetime_start=date_time_start,
                datetime_end=date_time_end
            )
        )
    return programs


templates = templating.Jinja2Templates(directory=CONF['DEFAULT']['templates_directory'])

async def xmltv(request: fastapi.Request):
    simplified_channels = build_simplified_channels(request.app.state.channels)
    programs = build_programs()

    rendered = templates.get_template(str(CONF['DEFAULT']['xmltv_template'])).render(
        channels=simplified_channels,
        programs=programs
    )

    return fastapi.Response(content=rendered, media_type='application/xml')

def register_route(router):
    router.add_api_route('/xmltv', xmltv, methods=['GET'])
