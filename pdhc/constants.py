import enum

class EncoderProfile(str, enum.Enum):
    CPU = 'cpu'
    VIDEO_TOOLBOX = 'video_toolbox'
    VAAPI = 'vaapi'
    OMX = 'omx'

