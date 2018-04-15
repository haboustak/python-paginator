class RowSource(object):
    def get_rows(self, start, count):
        raise Exception("not implemented")

class FileRowSource(RowSource):
    def __init__(self, fileobj):
        super().__init__();

        self.fileobj = fileobj

    def next_page(self, rows):
        lines = []
        for i in range(rows):
            line = self.fileobj.readline()
            if not line:
                break

            lines.append(line)
        return lines
