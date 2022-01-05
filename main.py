import pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing import List, Tuple
import datetime as dt
import re

from settings import *

album_font = ImageFont.truetype(str(ALBUM_FONT_FILEPATH), 40)
first_listens_font = ImageFont.truetype(str(ALBUM_FONT_FILEPATH), 48)


def format_album_image(s: str) -> str:
    if match := re.match(ALBUM_REGEX, s):
        _, year, _, month, _, day, name = match.groups()
        return ALBUM_FORMAT_STRING.format(name, year)
    else:
        return s


def make_rectangle_grid(images: list,
                        dimensions: tuple,
                        image_dimension: int,
                        border_width: int,
                        pad_sides: List[str] = None,
                        custom_column_offset: int = 0,
                        custom_row_offset: int = 0,
                        custom_columns: List[int] = None,
                        custom_rows: List[int] = None
                        ) -> Image:
    try:
        if 'all' in pad_sides:
            pad_top, pad_bot, pad_left, pad_right = (True,)*4
        else:
            pad_top = 'top' in pad_sides
            pad_bot = 'bot' in pad_sides
            pad_left = 'left' in pad_sides
            pad_right = 'right' in pad_sides
    except TypeError:
        pad_top, pad_bot, pad_left, pad_right = (False,)*4

    custom_columns = custom_columns if custom_columns else []
    custom_rows = custom_rows if custom_rows else []

    m, n = dimensions
    assert m * n == len(images)
    d = image_dimension
    b = border_width
    anchors = []

    for j in range(m):
        y_extra_offset = sum(custom_row_offset for r in custom_rows if r <= 1)
        y = (j + 1*pad_top)*b + j*d + y_extra_offset

        for i in range(n):
            x_extra_offset = sum(custom_column_offset for c in custom_columns if c <= i)
            x = (i + 1*pad_left)*b + i*d + x_extra_offset
            anchors.append((x, y))

    grid_y = ((m-1) + 1*pad_top + 1*pad_bot)*b + m*d + len(custom_rows)*custom_row_offset
    grid_x = ((n-1) + 1*pad_left + 1*pad_right)*b + n*d + len(custom_columns)*custom_column_offset
    grid_image = Image.new('RGBA', (grid_x, grid_y), (0,)*4)

    for image, anchor in zip(images, anchors):
        image = image.resize((d,)*2)
        grid_image.paste(image, anchor)

    return grid_image


def make_text_column(text: List[str],
                     image_dim: Tuple[int, int],
                     align: str = 'left',
                     offset: Tuple[int, int] = (0, 0),
                     font=None) -> Image:
    font = font if font else album_font

    image = Image.new('RGBA', image_dim, (0,)*4)
    drawer = ImageDraw.Draw(image)
    drawer.multiline_text(offset, '\n'.join(text), font=font, align=align)
    return image


def make_forty_two_collage(images_dir: pathlib.Path) -> Image:
    images = [Image.open(fp) for fp in images_dir.iterdir()]

    assert len(images) == 42
    collage_top = images[:10]
    collage_mid = images[10:22]
    collage_bot = images[22:]

    # target
    top_dim = 600
    mid_dim = 500
    bot_dim = 300

    top_border = 10
    mid_border = 8
    bot_border = 4

    grid_top = make_rectangle_grid(collage_top, (2, 5), top_dim, top_border, ['top', 'bot'])
    grid_mid = make_rectangle_grid(collage_mid, (2, 6), mid_dim, mid_border, ['bot'])
    grid_bot = make_rectangle_grid(collage_bot, (2, 10), bot_dim, bot_border, custom_column_offset=1,
                                   custom_columns=[2, 4, 6, 8])
    grids = [grid_top, grid_mid, grid_bot]

    assert all(x.size[0] == y.size[0] for x in grids for y in grids)
    super_grid_x = grid_top.size[0] + 2*top_border
    super_grid_y = sum(x.size[1] for x in grids) + top_border
    super_grid = Image.new('RGBA', (super_grid_x, super_grid_y), (0,)*4)

    super_grid_x_offset = top_border
    super_grid_y_offset = 0
    super_grid.paste(grid_top, (super_grid_x_offset, super_grid_y_offset))

    super_grid_y_offset = grid_top.size[1]
    super_grid.paste(grid_mid, (super_grid_x_offset, super_grid_y_offset))

    super_grid_y_offset = grid_top.size[1] + grid_mid.size[1]
    super_grid.paste(grid_bot, (super_grid_x_offset, super_grid_y_offset))

    # timestamp = int(dt.datetime.utcnow().timestamp())
    # super_grid_image_filepath = GRID_DIR.joinpath('super-' + str(timestamp) + '.png')
    # super_grid.save(super_grid_image_filepath)
    # super_grid.show()
    # grid_top_image_filepath = GRID_DIR.joinpath('top-' + str(timestamp) + '.png')
    # grid_mid_image_filepath = GRID_DIR.joinpath('mid-' + str(timestamp) + '.png')
    # grid_bot_image_filepath = GRID_DIR.joinpath('bot-' + str(timestamp) + '.png')
    # grid_top.save(grid_top_image_filepath)
    # grid_mid.save(grid_mid_image_filepath)
    # grid_bot.save(grid_bot_image_filepath)

    return super_grid


def make_top_albums_collage(images_dir: pathlib.Path):
    collage_image = make_forty_two_collage(images_dir)
    border_width = 10

    images_filepaths = [fp for fp in images_dir.iterdir()]
    images_text = [format_album_image(fp.stem) for fp in images_filepaths]

    top_lines = images_text[:10]
    mid_lines = images_text[10:22]
    bot_lines = images_text[22:]

    text_x = 940
    top_text_y = 1220
    mid_text_y = 1877 - 1220
    bot_text_y = 2860 - 1877

    text_x_offset = border_width
    top_text_y_offset = border_width
    mid_text_y_offset = border_width
    bot_text_y_offset = 8

    top_text = make_text_column(top_lines, (text_x, top_text_y), offset=(text_x_offset, top_text_y_offset))
    mid_text = make_text_column(mid_lines, (text_x, mid_text_y), offset=(text_x_offset, mid_text_y_offset))
    bot_text = make_text_column(bot_lines, (text_x, bot_text_y), offset=(text_x_offset, bot_text_y_offset))
    texts = [top_text, mid_text, bot_text]

    assert sum(z.size[1] for z in texts) == collage_image.size[1]
    collage_x = collage_image.size[0]
    full_x = collage_x + text_x
    full_y = collage_image.size[1]

    full_image = Image.new('RGBA', (full_x, full_y), (0,)*4)
    full_image.paste(collage_image)
    full_image.paste(top_text, (collage_x, 0))
    full_image.paste(mid_text, (collage_x, top_text_y))
    full_image.paste(bot_text, (collage_x, top_text_y + mid_text_y))

    timestamp = int(dt.datetime.utcnow().timestamp())
    full_image_filepath = GRID_DIR.joinpath('full-' + str(timestamp) + '.png')
    full_image.save(full_image_filepath)
    # full_image.show()


def make_five_by_five(images_dir: pathlib.Path, image_dimension: int, border_width: int):

    images_filepaths = [fp for fp in images_dir.iterdir()]
    images = [Image.open(fp) for fp in images_filepaths]

    grid_image = make_rectangle_grid(images, (5, 5), image_dimension, border_width)
    timestamp = int(dt.datetime.utcnow().timestamp())
    grid_image_filepath = GRID_DIR.joinpath(images_dir.name + '-' + str(timestamp) + '.png')
    grid_image.save(grid_image_filepath, 'PNG')


def make_2021_first_listens(images_dir: pathlib.Path, image_dimension: int, border_width: int):
    images_filepaths = [fp for fp in images_dir.iterdir()]
    images_text = [format_album_image(fp.stem) for fp in images_filepaths]
    images = [Image.open(fp) for fp in images_filepaths]

    grid = make_rectangle_grid(images, (9, 9), image_dimension, border_width, ['all'])

    timestamp = int(dt.datetime.utcnow().timestamp())
    # grid_filepath = GRID_DIR.joinpath('first-listens-' + str(timestamp) + '.png')
    # grid.save(grid_filepath)
    # grid.show()

    grid_x = grid.size[0]
    grid_y = grid.size[1]
    text_x = 2000
    text_y = grid_y
    super_x = grid_x + text_x
    super_y = grid_y

    text = make_text_column(images_text, (text_x, text_y), offset=(border_width, border_width), font=first_listens_font)
    super_image = Image.new('RGBA', (super_x, super_y), (0,)*4)
    super_image.paste(grid)
    super_image.paste(text, (grid_x + border_width, border_width))

    super_filepath = GRID_DIR.joinpath('first-listens-full-' + str(timestamp) + '.png')
    super_image.save(super_filepath)
    # super_image.show()


if __name__ == '__main__':
    make_five_by_five(pathlib.Path('artist-albums'), 500, 10)
    make_top_albums_collage(pathlib.Path('example-albums'))
    # make_2021_first_listens(pathlib.Path(r'A:\pictures\editing\Albums\2021 Review'), 500, 10)

