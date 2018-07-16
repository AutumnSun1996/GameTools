import datetime

with open('eidon-start-time.txt', 'r') as fl:
    timestamp = float(fl.read())
    
start = datetime.datetime.fromtimestamp(timestamp)
changed = False
now = datetime.datetime.now()
dt = datetime.timedelta(minutes=150)

while start < now:
    start = start + dt
    changed = True


seconds = (start - now).total_seconds()

# print(seconds)

if seconds > 100 * 60:
    seconds = seconds - 100 * 60
    status = ["夜晚", "白天", "{:.0f}分钟".format(seconds / 60)]
else:
    hour = seconds // 3600
    seconds -= hour * 3600
    minute = seconds / 60
    status = ["白天", "夜晚", ("{:.0f}小时".format(hour) if hour else "") + "{:.0f}分钟".format(minute)]
    
print("现在是{}，离下一个{}还有{}".format(*status))

if changed:
    with open('eidon-start-time.txt', 'w') as fl:
        fl.write('%f' % (start - dt).timestamp())
    
# total = 0
# while total < 5:
    # if start.hour > 8 and start.hour < 23:
        # print(start)
        # total += 1
    # start = start + dt