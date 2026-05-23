from qr_encoding import binToDec, decToBin

"""Codifica QR based on Reed-Solomon in Galois-Field, GF(256)
    The generator polinomial is defined as:

        g(x) = (x - a**0)(x - a**1)(x - a**2)...(x - x**(n-1))
        where:
            a: the primitive element os the field
            n: number of EC codewords 
            
    Why for QR Code we use GF(256)? This is because in QR code we work with byte (8 bits). With a byte we can represent 256 unique values. So we need a field with 256 elements.

    For a better understanding this algorithm i belive a simple example could be useful looking at it step-by-step:

    Let's consider the easiest case:
    EC codewords = r = 2
    
    G(x) = (x - a**0)(x - a**1) = (x - 1)(x - a) = x**2 + (a + 1)x + a

    The value of the primitive element a**i we can find it from the log/antiglog Table for GF(256)

    a**0 = GF256_EXP[0] = 1
    a**1 = GF256_EXP[1] = 2

    So we obtain:

    G(x) = x**2 + 3x + 2 --> the coefficent of out generator polinomial will be: [1, 3, 2]

    NOTE: In the ISO/IEC 18004:2015 you will se that for this condition the G(x) = x**2 + a**25*x + a. If you check in the log/antiglog Table you will see that they corresponde 
            as well to [1, 3, 2] respectively.
    
    Let's suppose:

    D(x) = 2x**2 + 1

    D(x)*x**r = 2x**4 + x**2

    D(x)*x**r mod G(x) = (2x**4 + x**2)/(x**2 + 3x + 2)

    To get the remainder need to remove the highest order until we are below the highest order of G(x).
    Remeber that in GF:
    - Addition = sobtraction = XOR
    - moltiplicatio = division = sum of the primitive exponent in module 255 --> a*b = antolog(log(a)+log(b) mod 255) = GF256_EXP[GF256_LOG[a] + GF256_LOG[b]]

    Step 1.

    (2x**4 + x**2) - (x**2 + 3x + 2)*2x**2

    1*2 = GF256_EXP[GF256_LOG[1] + GF256_LOG[2]] = GF256_EXP[0 + 1] = 2
    3*2 = GF256_EXP[GF256_LOG[3] + GF256_LOG[2]] = GF256_EXP[25 + 1] = 6 
    2*2 = GF256_EXP[GF256_LOG[2] + GF256_LOG[2]] = GF256_EXP[1 + 1] = 4

    (2x**4 + x**2) - (x**2 + 3x + 2)*2x**2 = 2x**4 + x**2 - 2x**4 - 6x**3 - 4x**2

    2 XOR 2 = 0
    0 XOR 6 = 6
    1 XOR 4 = 5

    2x**4 + x**2 - 2x**4 - 6x**3 - 4x**2 = 6x**3 + 5x**2 

    Step 2.

    (6x**3 + 5x**2) - (x**2 + 3x + 2)*(6x) 

    1*6 = GF256_EXP[GF256_LOG[1] + GF256_LOG[6]] = GF256_EXP[0 + 26] = 6
    3*6 = GF256_EXP[GF256_LOG[3] + GF256_LOG[6]] = GF256_EXP[25 + 26] = 10 
    2*6 = GF256_EXP[GF256_LOG[2] + GF256_LOG[6]] = GF256_EXP[1 + 26] = 12

    (6x**3 + 5x**2) - (x**2 + 3x + 2)*(6x) = 6x**3 + 5x**2 + 6x**3 + 10x**2 + 12x

    6 XOR 6 = 0
    5 XOR 10 = 15
    0 XOR 12 = 12

    6x**3 + 5x**2 + 6x**3 + 10x**2 + 12x = 15x**2 + 12x 

    Step 3.

    (15x**2 + 12x) - (x**2 + 3x + 2)*(15) 

    1*15 = GF256_EXP[GF256_LOG[1] + GF256_LOG[15]] = GF256_EXP[0 + 75] = 15
    3*15 = GF256_EXP[GF256_LOG[3] + GF256_LOG[15]] = GF256_EXP[25 + 75] = 17 
    2*15 = GF256_EXP[GF256_LOG[2] + GF256_LOG[15]] = GF256_EXP[1 + 75] = 30

    (15x**2 + 12x) - (x**2 + 3x + 2)*(15) = 15x**2 + 12x + 15x**2 + 17x + 30

    15 XOR 15 = 0
    12 XOR 17 = 29
    0 XOR 30 = 30

    15x**2 + 12x + 15x**2 + 17x + 30 = 29x + 30 

    Since we have obtain a value with a degree lower than the G(x) this will be our rest:

    R(x) = 29x + 30

    If we would have done the operation algebrically we would have obtain:

    (2x**4 + x**2) - (x**2 + 3x + 2)*2x**2 = 2x**4 + x**2 - 2x**4 - 6x**3 - 4x**2 = -6x**3 - 3x**2
    (-6x**3 - 3x**2) - (x**2 + 3x + 2)*(-6x) = -6x**3 - 3x**2 + 6x**3 + 18x**2 + 12x = 15x**2 + 12x
    (15x**2 + 12x) - (x**2 + 3x + 2)*15 = 15x**2 + 12x - 15x**2 - 45x - 30 = - 33x - 30

    R(x) = -33x - 30
    """

# 1. Bulding the matematic field GF(256) 
# Tabelle log/antilog GF(256): the purpose of this is to fasten moltiplications operations, a*b = EXP(LOG(a) + LOG(b))
GF256_EXP = [0] * 512   # Primitive elemente a**i (This array has a dimension twice of 256 since the moltiplication)
GF256_LOG = [0] * 256   # Exponent value of the primitive element a**i, so it represent i

# Build the power of the primitive elements a
x = 1
for i in range(255):
    GF256_EXP[i] = x # Primitive elemente a**i
    GF256_LOG[x] = i
    x <<= 1 # inserts a 0 bits on the left (bitwise shift left operation)
    if x & 0x100:  # if after the shift it overflow the 8 bit
        x ^= 0x11D  # reduce by the irriducible polinomial (x^8 + x^4 + x^3 + x^2 + 1 --> 11D Hex = 100011101) (bitwise XOR operation)

# 2. Extend the table EXP to avoid the module 255 in the LOG sum
for i in range(255, 512):
    GF256_EXP[i] = GF256_EXP[i - 255]   # Fill the zeros value with the same values already in the table GF256_EXP[:256]

# 3. Moltiplication in the GF(256), a*b = EXP(LOG(a) + LOG(b))
def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return GF256_EXP[GF256_LOG[a] + GF256_LOG[b]]

# 4. Generate the generator polinomial G(x)
def qr_generator_poly(ec_cws: int) -> list:
    g = [1] # Define the starting g(x)
    for i in range(ec_cws):   # This loop correspond as doing the moltiplication g(x)*(x + a**i)
        new_g = [0] * (len(g) + 1)
        for j in range(len(g)):
            new_g[j] ^= g[j]    # This XOR operation correspond to g(x)*x         
            new_g[j + 1] ^= gf_mul(g[j], GF256_EXP[i])  # This XOR operation correspond to g(x)*a**i
        g = new_g
    return g

# 5. Perform the Reed-Solom operation and calculate the EC bits
def ec_remainder(bits_string: str, gx: list, ec_cws: int) -> str:

    # Starting form the final bits string divide it in bytes and calculate the corresponding decimal value. This will be the coefficents of the polynomial D(x)
    dx = []
    for i in range(int(len(bits_string)/8)):
        dx.append(binToDec(bits_string[i*8:i*8+8]))
    dx_new = dx + [0]*ec_cws    # Add the space for the EC bytes, it would be as doing D(x)*x**ec_cws. So we are shifting the degree of the polinomial to have a base as big at least as the one of the G(x)

    for i in range(len(dx)):
        coef = dx_new[i]    # highest degree elemet of the polinomial that has to be reduced, meaning has to be subtracted which if GF means XORing

        if coef != 0:   # If the coefficent is zero it mean that it has already been reduced to the minimum
            for j in range(len(gx)):    # WE loop for every values og og beazued we have to imagein a operation like such: g(x) = (ax**2 + b*x + c)*coef
                dx_new[i + j] ^= gf_mul(gx[j], coef)

    # Create the EC bit string, by converting the decimal coefficents above calculated into binary
    bits_string_ec = ""
    for i in dx_new[-ec_cws:]:
        bits_string_ec += decToBin(i,8)
    
    return bits_string_ec

def qr_encoding_blocks(bits_string: str, n_blocks: list, ec_blocks: str, qr_capacity: int) -> str:

    """Depending on the Version and EC the codeword shall be subdivided into one or more blocks, to each of which the error correction algotithm shall be applied separately.
        The function takes four inputs:
            1. bits_string: the code words cmposed of mode indicator + character count + input data bits sequence + padding
            2. n_blocks: the required numer of blocks for the versiona and EC selected
            3. ec_blocks: information about the total codewords, data codewords and error correction capacity for each block
        It returns the final bytes string sorted accrodingly to the ISO block structures requirements
        (pg. 44 chapter 7.5.1/7.6 of ISO/IEC 18004:2015)"""

    n_blocks = [i for i in n_blocks if i != 0]
    ec_blocks = ec_blocks.split(";")  

    c = 0
    offset = 0
    blocks = {"data": [],
              "ec": []}

    # 
    for i, b in enumerate(n_blocks):
        ec_block = ec_blocks[i].split(",")
        for row in range(b):
            blocks["data"].append([])
            blocks["ec"].append([])
            bits_string_block = bits_string[offset*8:(int(ec_block[1]) + offset)*8]
            ec_cws = int(ec_block[0]) - int(ec_block[1])
            gx = qr_generator_poly(ec_cws)  # Calculate the generator polinomial
            bits_string_ec = ec_remainder(bits_string_block, gx, ec_cws)    # perfomed the EC bits calculation
            for col in range(int(ec_block[1])):
                blocks["data"][c].append(bits_string_block[col*8:col*8+8])
            for col in range(ec_cws):
                blocks["ec"][c].append(bits_string_ec[col*8:col*8+8])
            c += 1
            offset += int(ec_block[1])

    bits_string = ""

    # Constructe the final bits string
    for d in ["data", "ec"]:
        m = [len(i) for i in blocks[d]]
        for i in range(max(m)):
            for j in range(len(blocks[d])):
                try:
                    bits_string += blocks[d][j][i]
                    print(blocks[d][j][i])
                except IndexError:
                    continue

    # Add the Remanider bits if necessary
    if len(bits_string) < qr_capacity*8:
        bits_string += 0*(qr_capacity*8 - len(bits_string))  
        print(f"Remainder bits: {qr_capacity*8 - len(bits_string)}")          
    
    return bits_string