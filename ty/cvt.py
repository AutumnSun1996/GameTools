import os
import base64

basedir = "midi"
for name in os.listdir(basedir):
    if name.endswith((".mid", ".mml")):
        continue
    path = os.path.join(basedir, name)
    newname = os.path.splitext(name)[0] + ".mid"
    newpath = os.path.join(basedir, newname)
    if os.path.exists(newpath):
        continue
    with open(path, "r") as f:
        data = f.read()
    with open(newpath, "wb") as f:
        f.write(base64.b64decode(data))
    print(newpath)
