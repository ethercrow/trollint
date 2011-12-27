

def full_text_for_cursor(cur):
    with open(cur.location.file.name) as fi:
        e = cur.extent
        text = fi.read()[e.start.offset:e.end.offset]
        return text
