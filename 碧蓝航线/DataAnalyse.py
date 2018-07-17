import os

def loop_file(cur, lvl=0):
    if os.path.isfile(cur):
        with open(cur, "rb") as fl:
            head = fl.read(32)
        print("{:60s} {}".format(("--" * lvl) + cur, head))
    else:
        for name in os.listdir(cur):
            loop_file(os.path.join(cur, name), lvl+1)

loop_file("Data")