GF256_EXP = [0] * 512
GF256_LOG = [0] * 256

x = 1
for i in range(255):
    GF256_EXP[i] = x
    GF256_LOG[x] = i
    x <<= 1
    if x & 0x100:  # overflow di 8 bit
        x ^= 0x11D  # polinomio irriducibile QR (x^8 + x^4 + x^3 + x^2 + 1)
print(GF256_EXP)
print(GF256_LOG)
