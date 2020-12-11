R = 0b11111110
A = 0b01111111

if R & 0b10000000:
    R = - ((0x100 - R) & 0xff)
if A & 0b10000000:
    A = - ((0x100 - A) & 0xff)

def SUB_8(value1, value2):
    value = value1 - value2
    if value < 0:
        value += 0x100
    if value == 0:
        print("Z")
    if value & 0b10000000:
        print("N")
    if (value1 & 0xf) < (value2 & 0xf):
        print("H")
    if value1 < value2:
        print("C")
    return value & 0xff

print(R)
print(A)

d = SUB_8(R,A)

if d < 0:
    d += 0x100
d = 0x80
print(bin(d))
e = d
if e & 0b10000000:
    e = - ((0x100 - e) & 0xff)
print(e)