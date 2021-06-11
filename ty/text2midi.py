import base64
import os


basedir = "midi"
for name in os.listdir(basedir):
    if name.endswith(".mid"):
        continue
    newname = os.path.splitext(name)[0] + ".mid"
    newpath = os.path.join(basedir, newname)
    if os.path.exists(newpath):
        continue
    with open(os.path.join(basedir, name), "r") as f:
        text = f.read()
    with open(newpath, "wb") as f:
        f.write(base64.b64decode(text))
        print(newpath)
