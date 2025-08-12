import asyncio
import logging
import fastapi
from fastapi import responses

from typing import Optional

from pdhc import constants
from pdhc.utils import network

import pdhc.config

LOG = logging.getLogger(__name__)
CONF = pdhc.config.CONF

router = fastapi.APIRouter()


class StreamGenerator:
    def __init__(self, channel, transcode=False, refresh_interval=60):
        self._channel = channel
        self._transcode = transcode
        self._refresh_interval = refresh_interval
        self._process = None
        self._chunk_reader = None
        self._ffmpeg_args = None
        self._chunk_queue = asyncio.Queue()
    
    async def _get_ffmpeg_args(self):
        ffmpeg_args = []

        if CONF['DEFAULT']['encoder_profile'] == constants.EncoderProfile.VAAPI:
            ffmpeg_args += [
                '-vaapi_device', '/dev/dri/renderD128',
                '-hwaccel', 'vaapi',
                '-hwaccel_output_format', 'vaapi'
            ]
        elif CONF['DEFAULT']['encoder_profile'] == constants.EncoderProfile.VIDEO_TOOLBOX:
            ffmpeg_args += ['-hwaccel', 'videotoolbox']
        
        m3u8_url = await network.get_m3u8_url(self._channel.url)
        ffmpeg_args += ['-re']
        ffmpeg_args += ['-i', f'{m3u8_url}']

        if self._channel.disable_transcode:
            ffmpeg_args += ['-c:v', 'copy']
        else:
            if CONF['DEFAULT']['encoder_profile'] == constants.EncoderProfile.VIDEO_TOOLBOX:
                ffmpeg_args += ['-c:v', 'h264_videotoolbox']
            elif CONF['DEFAULT']['encoder_profile'] == constants.EncoderProfile.VAAPI:
                ffmpeg_args += ['-c:v', 'h264_vaapi', '-vf', 'scale_vaapi=format=nv12,hwupload']
            elif CONF['DEFAULT']['encoder_profile'] == constants.EncoderProfile.OMX:
                ffmpeg_args += ['-c:v', 'h264_omx']
            elif CONF['DEFAULT']['encoder_profile'] == constants.EncoderProfile.CPU:
                ffmpeg_args += ['-c:v', 'libx264', '-preset', 'superfast']
            else:
                raise Exception('Unsupported encoder profile %s.', CONF['DEFAULT']['encoder_profile'])

        ffmpeg_args += [
            '-reconnect', '1',
            '-reconnect_streamed', '1',
            '-reconnect_delay_max', '5',
            '-c:a', 'copy',
            '-copyinkf',
            '-metadata', 'service_provider=AMAZING',
            '-metadata', f'service_name={self._channel.name.replace(" ", "")}',
            '-tune', 'zerolatency',
            '-mbd', 'rd',
            '-flags', '+ilme+ildct',
            '-use_wallclock_as_timestamps', '1',
            '-fflags', '+genpts',
        ]

        if self._transcode == 'internet720':
            ffmpeg_args += ['-s', '1280x720', '-r', '30']

        ffmpeg_args += ['-f', 'mpegts', 'pipe:1']

        LOG.info('ffmpeg args: ffmpeg %s', ' '.join(ffmpeg_args))
        return ffmpeg_args

    async def _read_chunks(self, process):
        while True:
            chunk = await process.stdout.read(1024)
            if not chunk:
                break
            await self._chunk_queue.put(chunk)
    
    async def _start_ffmpeg_process(self, refresh_args=False):
        if refresh_args:
            self._ffmpeg_args = await self._get_ffmpeg_args()
        process = await asyncio.create_subprocess_exec(
            'ffmpeg',
            *self._ffmpeg_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return process

    async def _refresh_ffmpeg_process(self):
        while True:
            await asyncio.sleep(self._refresh_interval)
            
            LOG.info('Switching to new process')
            new_process = await self._start_ffmpeg_process(refresh_args=True)
            new_chunk_reader = asyncio.create_task(self._read_chunks(new_process))

            old_process = self._process
            self._process = new_process
            self._chunk_reader = new_chunk_reader

            if old_process.returncode is None:
                old_process.kill()
                await old_process.wait()
    
    async def stream(self):
        self._process = await self._start_ffmpeg_process(refresh_args=True)
        self._chunk_reader = asyncio.create_task(self._read_chunks(self._process))
        refresh_task = asyncio.create_task(self._refresh_ffmpeg_process())

        try:
            while True:
                chunk = await self._chunk_queue.get()
                if chunk is None:
                    break
                yield chunk
        except asyncio.CancelledError:
            if self._process.returncode is None:
                self._process.kill()
                await self._process.wait()
            refresh_task.cancel()
            

async def stream(request: fastapi.Request, channel_id: int, transcode: Optional[str] = None):
    channels = request.app.state.channels

    found_channel = None
    for channel in channels:
        if channel.number == channel_id:
            found_channel = channel
            break
    if not found_channel:
        raise fastapi.HTTPException(status_code=400, detail='Invalid channel ID')

    stream_generator = StreamGenerator(found_channel)

    headers = {'Content-Type': 'video/mp2t'}

    return responses.StreamingResponse(stream_generator.stream(), headers=headers)


def register_route(router):
    router.add_api_route('/stream/{channel_id}', stream, methods=['GET'])