import curses

class PagedUI(object):
    KEYS_UP = [ord('k'), curses.KEY_UP]
    KEYS_DOWN = [ord('k'), ord('\n'), curses.KEY_DOWN]
    KEYS_PGDOWN = [ord(' '), curses.KEY_NPAGE]
    KEYS_PGUP = [ord('p'), curses.KEY_PPAGE]
    KEYS_START = [ord('g')]
    KEYS_END = [ord('G')]

    def __init__(self):
        self.width = 0
        self.height = 0
        self.row = 0
        self.col = 0
        self.row_count = 0

    def start(self):
        self.stdscr = curses.initscr()
        curses.noecho() # no echo
        curses.cbreak() # input without enter
        curses.curs_set(0) # no cursor
       
        self.stdscr.clear()
        self.stdscr.keypad(1)
        self.height, self.width = self.stdscr.getmaxyx()

        self.scroll_win = curses.newpad(self.height, self.width)
        half_size = self.width//2
        self.cmd_win= curses.newwin(1, half_size, self.height-1, 0)
        self.status_win = curses.newwin(1, half_size, self.height-1, half_size)

    def display(self, source):
        self.update(source)

        while self.run(source):
            pass

    def restore(self):
        self.stdscr.keypad(0)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def resize(self, new_cols, new_rows):
        rows, cols = self.scroll_win.getmaxyx()
        new_cols = max(cols, new_cols or 0)
        new_rows = max(rows, new_rows or 0)

        if new_cols>=cols or new_rows>=rows:
            self.scroll_win.resize(new_cols+1, new_rows+1)

    def fetch_rows(self, source):
        last_row = self.row + self.height

        # read more rows if scrolled past current data
        new_rows = []
        if last_row > self.row_count:
            new_rows = source.next_page(self.height)

        # load rows into pad
        if (new_rows):
            row_count = self.row_count + len(new_rows)

            self.resize(None, row_count)
            for i, line in enumerate(new_rows):
                self.resize(len(line), None)
                self.scroll_win.addstr(self.row_count+i, 0, line)

            self.row_count += len(new_rows)

        if (last_row > self.row_count):
            self.row = self.row_count - self.height + 1
            self.end = True

    def update(self, source):
        self.end = False
        self.fetch_rows(source)

        status = "{},{}".format(self.row, self.col)
        status = " "*(self.width//2-len(status)-1) + status

        self.cmd_win.erase()
        if (self.end):
            self.cmd_win.addstr(0, 0, "(END)", curses.A_REVERSE)
        else:
            self.cmd_win.addstr(0, 0, ":")

        self.status_win.addstr(0, 0, status)
        self.stdscr.refresh()
        self.scroll_win.refresh(self.row, self.col, 0, 0, self.height-2, self.width-1)
        self.cmd_win.refresh()
        self.status_win.refresh()

    def run(self, source):
        ch = self.stdscr.getch()
        if ch == ord("q"): 
            return False

        if ch in self.KEYS_UP:
            self._dec(1)
            self.update(source)
        elif ch in self.KEYS_DOWN:
            self._inc(1)
            self.update(source)
        elif ch in self.KEYS_PGUP:
            self._dec(self.height-1)
            self.update(source)
        elif ch in self.KEYS_PGDOWN:
            self._inc(self.height-1)
            self.update(source)
        elif ch in self.KEYS_START:
            self.row = 0
            self.update(source)
        elif ch in self.KEYS_END:
            self.cmd_win.addstr(0, 0, "(LOADING...)", curses.A_REVERSE)
            self.cmd_win.refresh()
            while not self.end:
                self._inc(self.height)
                self.fetch_rows(source)
            self.update(source)
        elif ch == curses.KEY_LEFT:
            self._left(1)
            self.update(source)
        elif ch == curses.KEY_RIGHT:
            self._right(1)
            self.update(source)
        self.update(source)
        return True

    def _inc(self, offset):
        self.row += offset

    def _dec(self, offset):
        self.row = max(self.row-offset, 0)

    def _left(self, offset):
        self.col = max(self.col-offset, 0)

    def _right(self, offset):
        self.col += offset
