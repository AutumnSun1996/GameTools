data = """
0 p
1 c
2 d
3 e
4 f
5 g
6 a
7 b
A 1   N - - -
B 2   N -
C 4   N
D 8   下划线*1
E 16  下划线*2
F 32  下划线*3
"""
reps = [line.split()[:2] for line in data.strip().splitlines()]

text = """
LD <<6>3>1<54+B |<6>3>1<54+C >35| 7B. 0>1| 2B 0<335|

656>1<765C| 653C. 0335|656>1 <7663|&32C. 06>2C|

<6>2C 0<6>2D.<6E| 7C3C 0232| 5C 02567>1| 7E6E7C. 0335|

656>1<7656|&63C. 0335| 656>1<7665|&5>3C. 06>2.<6E|
>2B 03<7.6E | 7E>1E<7&7B 6>2 | <736>2<736.5E| 6B. >53|
2C 022312| 3B 0C 53| 2C
"""
for a, b in reps:
    text = text.replace(a, b)
print(text)
