import re
import os
import shutil

for root, dirs, files in os.walk("."):
    if not root[-8:].isnumeric():
        continue
    print("Check dir", root)
    for name in files:
        source = os.path.join(root, name)
        match = re.search(r".+@(\d{6})\d{2}\.log", name)
        if match:
            dirname = match.group(1)
            target = os.path.join(dirname, name)
            target_dir = os.path.dirname(target)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            # print(source, target)
            if not os.path.exists(target):
                shutil.move(source, target)
                print("Moved:", target)
            else:
                print("Exists:", target)

for root, dirs, files in os.walk("."):
    if not dirs + files:
        os.removedirs(root)
        print("Remove", root)
