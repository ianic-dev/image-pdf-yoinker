import os
import sys
import subprocess
from collections.abc import Callable
from alive_progress import alive_bar

def printhelp():
    print("help")
    sys.exit(0)

def makeurlgen(ln: list[str], leadingzeros: int):
    if leadingzeros != 0:
        def geturl(num: int):
            return ln[0] + (leadingzeros - len(str(num)) + 1)*"0" + str(num) + ln[1]
    else:
        def geturl(num: int):
            return ln[0] + str(num) + ln[1]
    return geturl

def parseurl(url: str):
    extensionlist = [".png", ".jpg", ".jpeg", ".jfif", ".webp"]
    extension = []
    for i in range(len(extensionlist)):
        if extensionlist[i] in url:
            extension.append(i)

    if len(extension) == 0:
        print(f"{sys.argv[0]}: invalid url -- '{url}' does not contain any of [{', '.join(extensionlist)}]")
        sys.exit(1)
    elif len(extension) > 1:
        print(f"{sys.argv[0]}: invalid url -- '{url}' contains multiple of [{', '.join(extensionlist)}]")
        sys.exit(1)

    extension = extensionlist[extension[0]]
    dotidx = url.find(extension)
    rside = len(url)-1
    slashidx = url.rfind('/', 0, rside)

    while slashidx > dotidx:
        rside -= 1
        slashidx = url.rfind('/', 0, rside)

    numfmt = url[slashidx+1:dotidx]
    leadingzeros = 0
    for c in numfmt:
        if c != '0':
            break
        leadingzeros += 1

    return makeurlgen([url[0:slashidx+1], url[dotidx:]], leadingzeros), extension

if __name__ == "__main__":
    helps = ["-h", "-help", "--help"]
    if len(sys.argv) <= 3:
        printhelp()
    if sys.argv[1] in helps:
        printhelp()

    fullurl = sys.argv[1]

    try:
        npages = int(sys.argv[2])
    except:
        print(f"{sys.argv[0]}: invalid argument -- '{sys.argv[2]}': Expected integer number of pages")
        sys.exit(1)

    path = sys.argv[3]
    if not os.path.exists(sys.argv[3]):
        print(f"{sys.argv[0]}: path '{sys.argv[3]}' does not exist: attempting to create directory")
        try:
            os.mkdir(path)
        except:
            print(f"{sys.argv[0]}: failed to create directory '{sys.argv[3]}'")


    geturl, extension = parseurl(sys.argv[1])
    intlen = len(str(npages-1))

    with alive_bar(npages) as bar:
        bar.text("scraping images")
        for p in range(1, npages+1):
            filename = path + '/' + (intlen - len(str(p)))*'0' + str(p) + extension
            # os.system(f'wget --no-verbose --output-document={filename} {geturl(p)}')
            subprocess.Popen(f'wget --quiet --output-document={filename} {geturl(p)}'.split()).wait()
            bar()
    command = ["magick", f"{path}/*{extension}", f"{path}.pdf"]
    subprocess.Popen(command).wait()
    sys.exit(0)
    
