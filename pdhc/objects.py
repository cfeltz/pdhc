from dataclasses import dataclass

# should match definition in pdhc-parser repo
@dataclass
class Channel:
    number: int
    url: str
    name: str | None = None
    disable_transcode: bool = False