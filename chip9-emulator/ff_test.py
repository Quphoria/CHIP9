a = 0xFF
de = 0b00000000
b = 0x20

i = 1
de += a
while de & 0xffff:
    #print(hex(de))
    de += a
    de = de & 0xffff
    i += 1
print(hex(de))
print("Complete:",i,hex(i))