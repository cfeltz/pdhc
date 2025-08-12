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

@dataclass
class Status:
    ScanInProgress: int
    ScanPossible: int
    Source: str
    Cable: list

async def lineup_status(request: fastapi.Request):
    return Status(
        ScanInProgress=0,
        ScanPossible=1,
        Source='Cable',
        Cable=['Cable']
    )
    

def register_route(router):
    router.add_api_route('/lineup.json', lineup, methods=['GET'], response_model=List[ChannelLineup])
    router.add_api_route('/lineup_status.json', lineup_status, methods=['GET'], response_model=Status)
