import fastapi
from typing import List
from dataclasses import dataclass


@dataclass
class ChannelLineup:
    GuideNumber: str
    GuideName: str
    Tags: str
    URL: str


async def lineup(request: fastapi.Request):
    channel_lineups = []
    host = request.headers.get('host', 'localhost')

    for channel in request.app.state.channels:
        channel_lineups.append(ChannelLineup(
            GuideNumber=str(channel.number),
            GuideName=channel.name,
            Tags='',
            URL='http://%s/stream/%d' % (host, channel.number)
        ))
    
    return channel_lineups

def register_route(router):
    router.add_api_route('/lineup', lineup, methods=['GET'], response_model=List[ChannelLineup])
