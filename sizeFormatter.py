import os

def formatTopLevel(fname:str) -> str:
    '''
    Format the file size to the max level.
     fname => size(unformatted) (B)

    Example: formatTopLevel(1024[file size]) -> "1 KB";
                formatTopLevel(1048576[file size]) -> "1 MB"
    '''

    size = os.path.getsize(fname)
    if size == 0:
        return "0 B"
    lev = 0
    levList = ["B","KB","MB","GB","TB","PB"]
    while int(size) > 1:
        size /= 1024
        lev += 1
    size *= 1024
    return "{} {}".format(round(size, 2), levList[lev-1])