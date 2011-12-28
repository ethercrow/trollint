

def full_text_for_cursor(cur):
    if cur.location.file:
        with open(cur.location.file.name) as fi:
            e = cur.extent
            text = fi.read()[e.start.offset:e.end.offset]
            return text
    else:
        return cur.displayname
