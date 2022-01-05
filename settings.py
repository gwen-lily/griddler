import pathlib

GRID_DIR = pathlib.Path('output/grids')
FONT_DIR = pathlib.Path('assets/fonts')

ALBUM_REGEX = r'(.*)\[(\d{4})(-(\d{2}))?(-(\d{2}))?\] (.*)'
# this is how my album images look, learn regex and edit it to your needs :3
# (ordering info up front)[yyyy(-mm)(-dd)] (album name)

ALBUM_MAX_LENGTH = 50
ALBUM_FORMAT_STRING = '{:} ({:})'
ALBUM_FONT_FILEPATH = FONT_DIR.joinpath('SEGOEUI.TTF')
