import sys
import itertools
import math

pairs = """
(({}{}{}){}{}){}{}
({}{}({}{}{})){}{}
{}{}({}{}({}{}{}))
{}{}(({}{}{}){}{})
({}{}{}){}({}{}{})
"""

def check_option(nums):
    res = []
    for ops in itertools.product("+-*/", repeat=3):
        for fmt in pairs.strip().splitlines():
            cmd = fmt.format(nums[0], ops[0], nums[1], ops[1], nums[2], ops[2], nums[3])
            try:
                result = eval(cmd)
            except Exception:
                continue
            if math.isclose(result, 24):
                res.append(cmd)
    return res



nums = list(map(int, sys.argv[1:]))
for num in range(1, 10):
    res = check_option(nums + [num])
    if res:
        print(num, res)
