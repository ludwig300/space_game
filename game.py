import asyncio
import curses
import random
import itertools
from curses_tools import draw_frame, read_controls


class Spaceship:
    def __init__(self, canvas, row, column, frames):
        self.canvas = canvas
        self.row = row
        self.column = column
        self.frames = frames
        self.current_frame = ""

    async def animate(self, canvas):
        for frame in itertools.cycle(self.frames):
            self.current_frame = frame
            draw_frame(canvas, self.row, self.column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, self.row, self.column, frame, negative=True)

    async def move(self, canvas):
        rows, columns = canvas.getmaxyx()
        while True:
            rows_direction, columns_direction, _ = read_controls(canvas)
            draw_frame(
                canvas,
                self.row,
                self.column,
                self.current_frame,
                negative=True
            )

            frame_height, _ = self.get_frame_size(self.current_frame)

            self.update_position(rows_direction, columns_direction)

            self.row = max(0, min(self.row, rows - frame_height))
            self.column = max(1, min(self.column, columns - 1))

            await asyncio.sleep(0)

    async def fire(self, canvas):
        rows, columns = canvas.getmaxyx()
        row, column = self.row, self.column
        while True:
            if 0 < row < rows and 0 < column < columns:
                canvas.addstr(round(row), round(column), '|')
            await asyncio.sleep(0.05)
            if 0 < row < rows and 0 < column < columns:
                canvas.addstr(round(row), round(column), ' ')
            row -= 1
            await asyncio.sleep(0)

    @staticmethod
    def get_frame_size(frame):
        lines = frame.strip().split('\n')
        height = len(lines)
        width = max(len(line) for line in lines)
        return height, width

    def update_position(self, row_direction, column_direction):
        max_row, max_column = self.canvas.getmaxyx()
        frame_height, frame_width = self.get_frame_size(self.current_frame)

        speed_factor = 10
        new_row = max(
            0,
            min(
                max_row - frame_height,
                self.row + row_direction * speed_factor
            )
        )
        new_column = max(
            0,
            min(
                max_column - frame_width,
                self.column + column_direction * speed_factor
            )
        )

        self.row, self.column = new_row, new_column


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0.2)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0.3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0.5)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0.3)


def load_frames(frame_files):
    frames = []
    for file_name in frame_files:
        with open(file_name, 'r') as f:
            frames.append(f.read())
    return frames


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_draw_logic(canvas))


async def main_draw_logic(canvas):
    max_row, max_col = canvas.getmaxyx()
    ship_row, ship_column = max_row // 2, max_col // 2

    frame_files = ["rocket_frame_1.txt", "rocket_frame_2.txt"]
    ship_frames = load_frames(frame_files)
    spaceship = Spaceship(canvas, ship_row, ship_column, ship_frames)

    num_stars = 200
    star_symbols = '+*.:'

    coroutines = [
        blink(
            canvas,
            random.randint(1, max_row - 2),
            random.randint(1, max_col - 2),
            random.choice(star_symbols)
        ) for _ in range(num_stars)
    ]

    coroutines.append(spaceship.animate(canvas))
    coroutines.append(spaceship.move(canvas))
    coroutines.append(spaceship.fire(canvas))

    while True:
        await asyncio.gather(*(coroutine for coroutine in coroutines))
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
