debug = False

# LIST OF CHAR FOR THE ALPHANUMERIC MODE
# This info contain the character for the Alphanumeric encoding according to ISO/IEC 18004:2015 (pg. 28, chapter 7.3.4 and pg. 34 Table 5)

alphanumeric_list = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T''U','V','W','X','Y','Z',' ','$','%','*','+','-','.','/',':']

# FUNCTIONS TO DEFINE THE MODE OF THE INPURT STRING

def check_alphanumeric(data: str, alphanumeric_list: list) -> bool:

    """Given a string check if all charaters correspond to the one listed in db_alphacoding"""

    cond = True
    for j in data:
        if j in alphanumeric_list:
            continue
        else:
            cond = False
            
    return cond

def check_byte(data: str) -> bool:

    """Given an string asses if it is possible to encode it accordingly to ISO/IEC 8859-1 (1 bytes, so 8-bits, 2**8 = 256 characters). 
        This is the required encding accordingly to ISO/IEC 18004:2015 (pg. 28, chapter 7.3.5 and pg. 35 Table 6)."""
    
    cond = True
    try:
        data.encode("iso-8859-1")
    except UnicodeEncodeError:
        cond = False
        
    return cond

def check_kanji(data: str) -> bool:

    """Given an string asses if it is possible to encode it accordingly to iso-8859-1. 
        This is the required encding accordingly to ISO/IEC 18004:2015 (pg. 28, chapter 7.3.6)."""
    
    cond = True
    try:
        data.encode("shift_jis")
    except UnicodeEncodeError:
        cond = False
        
    return cond 

def find_mode(data: str, alphanumeric_list: list = alphanumeric_list) -> str:

    """Given a string input finds the correct mode to encode it in a QR code accoridnly to ISO/IEC 18004:2015"""

    if data.isdigit():
        mode = "Numeric"
    elif check_alphanumeric(data, alphanumeric_list):
        mode = "Alphanumeric"
    elif check_byte(data):
        mode = "Byte"
    elif check_kanji(data):
        mode = "Kanji"
    else:
        print("Character encoding cannot be perfomed")
        mode = None
        
    return mode

# BINARY/DECIMAL CONVETIONS FUNCTIONS

def decToBin(dec: int, n_bits: int) -> str:

    """Convert decimal number into a binary number. As second input select the number of bits for the conversion.
        return the binary number as a string."""
    
    bits = ['0' for i in range(n_bits)]

    i = 0
    while dec != 0:
        val = dec%2
        dec = dec//2
        bits[i] = str(val)
        i += 1
        
    return "".join(bits)[::-1]

def binToDec(binary: str) -> int:
    """Converta a binary written as a string into a decimal number
        return the number as int"""
    
    dec = 0
    for i, b in enumerate(binary[::-1]):
        dec += int(b)*2**i
    
    return dec

# QR CODE FUNCTIONS TO ENCODE INPUT STRING IN THE APPROPRIATE BITS SEQUENCE

def char_count(data, version, mode) -> str:

    """Encode the input data character count in the binary string. The number of bits change accordingly to the mode and the version as described 
        by the ISO/IEC 18004:2015 (pg. 31 Table 3)"""
    
    lunghezza = len(data)
    
    m_micro = {"Numeric": [3,4,5,6],
               "Alphanumeric": [0,3,4,5],
               "Byte": [0,0,4,5],
               "Kanji": [0,0,3,4]}
    
    m = {"Numeric": [10,12,14],
         "Alphanumeric": [9,11,13],
         "Byte": [8,16,16],
         "Kanji": [8,10,12]}
    
    if version < 0:
        char_count_bits = decToBin(lunghezza, m_micro[mode][version])   # Micro QR Code 
    elif version > 0 and version <= 9:
        char_count_bits = decToBin(lunghezza, m[mode][0]) 
    elif version > 9 and version <= 26:
        char_count_bits = decToBin(lunghezza, m[mode][1]) 
    elif version > 26 and version <= 40:
        char_count_bits = decToBin(lunghezza, m[mode][2]) 
    else:
        print("QR code version not valid")
        return
    
    return char_count_bits

def encode_numeric_qr(data: str, version: int) -> str:

    """This function convert the input data in the desired bits sequence if the mode is Numeric. The structure for the sequence in binary has to contain:
            mode indicator + character count + input data bits sequence
        For a more in depth understanding see pg. 33 chapter 7.4.3 or pg. 102 chapter Annex I of ISO/IEC 18004:2015"""

    m_micro = {-4:"", -3:"0", -2:"00", -1:"000"}
    bits_string = ""
    if version < 0:
        bits_string += m_micro[version] # Numeric mode indicator encoding for micro QR code, see pg. 31 Table 2
    else:
        bits_string += "0001" # Numeric mode indicator encoding

    char_count_bits = char_count(data, version, "Numeric") # character count into binary encoding

    bits_string += char_count_bits   # concatenate strings

    # For the numeric encoding the ISO/IEC 18004:2015 requires that data are group by three and encoded in 10 bits (if only 2 char in 7 bit and 1 in 4 bit)
    n_bits = {3:10, 2:7, 1:4}
    
    # Add a 1 in the range for the grouping of 3 element is the remainder is diffent from zero.
    # 9//3 = 3 so the range must be up tp 3, but 8//3 = 2 but also in this case the range has to be up to 3
    add = 0
    if len(data)%3 != 0:
        add = 1
    
    for i in range(0,len(data)//3+add):
        dec = data[i*3:(i*3)+3]
        bits = decToBin(int(dec), n_bits[len(dec)])
        bits_string += bits 
        
    return bits_string

def encode_alphanumeric_qr(data: str, version: int, db_alphacoding) -> str:

    """This function convert the input data in the desired bits sequence if the mode is Alphanumeric. The structure for the sequence in binary has to contain:
            mode indicator + character count + input data bits sequence
        For a more in depth understanding see pg. 34 chapter 7.4.4 of ISO/IEC 18004:2015"""

    m_micro = {-3:"1", -2:"01", -1:"001"}
    bits_string = ""
    if version < 0:
        bits_string += m_micro[version] # Alphanumeric mode indicator encoding for micro QR code, see pg. 31 Table 2
    else:
        bits_string = "0010" # Alphanumeric mode indicator encoding
    
    char_count_bits = char_count(data, version, "Alphanumeric") # character count into binary encoding
    
    bits_string += char_count_bits   # concatenate
    
    # The ISO/IEC 18004:2015 requires that data are group by two and encoded in 11 bits (if only 1 char in 6 bit)
    n = {2:11, 1:6}
    
    for i in range(0,len(data)//2+1):
        val = data[i*2:(i*2)+2] # indx in the string by taking only two consecutive char
        val_enc = []
        for j in val:
            try:
                x = db_alphacoding[db_alphacoding["Char."]==j].index[0] # for a specific char find the corresponding decimal value
            except IndexError:
                print("Value not supported by Alphanumeric mode")
                return
            val_enc.append(x)   # append the x valus in the list val_enc
        try:
            dec = val_enc[0]*45+val_enc[1]  # if val_enc contains 2 values the ISO require their values to be calcualtes as (d1*45 + d2)
        except IndexError:
            dec = val_enc[0]    # if val_enc contains only 1 value just use it as is
        bits = decToBin(int(dec), n[len(val_enc)])  # convert decimal value to binary
        bits_string += bits  # concatenate
        
    return bits_string

def encode_byte_qr(data: str, version: int) -> str:

    """This function convert the input data in the desired bits sequence if the mode is Byte. The structure for the sequence in binary has to contain:
            mode indicator + character count + input data bits sequence
        For a more in depth understanding see pg. 35 chapter 7.4.5 of ISO/IEC 18004:2015"""
    
    m_micro = {-2:"10", -1:"010"}
    bits_string = ""
    if version < 0:
        bits_string += m_micro[version] # Byte mode indicator encoding for micro QR code, see pg. 31 Table 2
    else:
        bits_string = "0100" # Byte mode indicator encoding
    
    char_count_bits = char_count(data, version, "Byte") # character count into binary encoding

    bits_string += char_count_bits # concatenate
    
    for i in data:
        if ord(i) <= 255:
            dec = i.encode('iso-8859-1')[0] # find the decimal value correspoding to the char accorsingly to ISO/IEC 8859-1
            bits = decToBin(int(dec), 8)    # covert decimal to binary
            bits_string += bits  # concatenate
        else:
            print("Value not supported by Byte mode (ISO/IEC 8859-1)")
            return
    return bits_string

def encode_kanji_qr(data: str, version: int) -> str:

    """This function convert the input data in the desired bits sequence if the mode is Kanji. The structure for the sequence in binary has to contain:
            mode indicator + character count + input data bits sequence
        For a more in depth understanding see pg. 37 chapter 7.4.6 of ISO/IEC 18004:2015"""

    m_micro = {-2:"11", -1:"011"}
    bits_string = ""
    if version < 0:
        bits_string += m_micro[version] # Kanji mode indicator encoding for micro QR code, see pg. 31 Table 2
    else:
        bits_string = "1000" # Kanji mode indicator encoding
    
    char_count_bits = char_count(data, version, "Kanji")    # character count into binary encoding
    
    bits_string += char_count_bits   # concatenate                        
    
    for i in data:
        encoded = i.encode('shift_jis') # find the binary value correspoding to the char accorsingly to ISO/IEC 8859-1
        k_hex = encoded.hex()   # convert to hexadecmal
        k_bin = int(k_hex, 16)  # convert to decimal (Kanji are represened by two bytes therefore to convert to decimal we need 16 bits)

        # Now depeding on the value of the k_bin the char will be encoded ina  different way
        if k_bin >= int("8140", 16) and k_bin <= int("9FFC", 16):
            step1 = int(k_hex, 16) - int("8140", 16)
            step2 = hex(step1)
            step3 = int(step2[2:4], 16) * int("C0", 16) + int("1F", 16)
            bits = decToBin(step3, 13)  # The final bit string has to be 13 bit long
        elif k_bin >= int("E040", 16) and k_bin <= int("EBBF", 16):
            step1 = int(k_hex, 16) - int("C140", 16)
            step2 = hex(step1)
            step3 = int(step2[2:4], 16) * int("C0", 16) + int("6A", 16)
            bits = decToBin(step3, 13)  # The final bit string has to be 13 bit long
        else:
            print("Not valid value for kanji encoding")
            return
        
        bits_string += bits # concatenate

    return bits_string

def padding(version: int, bits_string: str, data_bits_capacity: int) -> str:

    """The QR Code requireda certain expected number of bits depending on the versione and EC level. Therefore if the bit string generated, by encoding the data as
            mode indicator + character count + input data bits sequence
        contains a number of bits less than the full capacity we need to pad it and fill the remaining bits.
        First add the terminator. Maximum 4 bits unless bit string allows less or none.
        If there is still space add: the maximum number of padding bits and fill the remaining empty spaces with 0 bits.
        For a more in depth understanding see pg. 40 chapter 7.4.9/7.4.10 of ISO/IEC 18004:2015"""
    
    terminator = {-4:"000",
                  -3:"00000",
                  -2:"0000000",
                  -1:"000000000"}
                  
    pad = {0:"11101100", 1:"00010001"}
    nibble = 0 
    
    try:
        terminator = terminator[version]
    except KeyError:
        terminator = "0000"
    
    if version == -2 or version == -4:
        nibble = 4
    
    if len(bits_string) + len(terminator) <= data_bits_capacity:
        bits_string += terminator
        if data_bits_capacity - len(bits_string) >= nibble:
            q = (data_bits_capacity - len(bits_string) - nibble)//8
            x = data_bits_capacity - len(bits_string) - nibble - q*8
            bits_string += '0'*x
            for i in range(q):
                bits_string += pad[i%2]
            bits_string += '0'*nibble
            if debug:
                print("Terminator added")
                print(f"Padding of zeros added: {x}")
                print(f"Padding codewords added: {q}")
                print(f"Nibble: {nibble}")
    elif data_bits_capacity - len(bits_string) < len(terminator):
        bits_string += '0'*(data_bits_capacity - len(bits_string))
        if debug:
            print("Partial Terminator added")
    elif data_bits_capacity == len(bits_string):
        if debug:
            print("No padding required")
    else:
        print(len(bits_string), len(terminator), nibble, data_bits_capacity)
    
    return bits_string

def encode_data(data: str, mode: str, version: int, data_bits_capacity: int) -> str:

    """Given a string input to encode generate the bit string sequence"""

    if mode == "Numeric":
        bits_string = encode_numeric_qr(data, version)
    elif mode == "Alphanumeric":
        bits_string = encode_alphanumeric_qr(data, version)
    elif mode == "Byte":
        bits_string = encode_byte_qr(data, version)
    elif mode == "Kanji":
        bits_string = encode_kanji_qr(data, version)

    bits_string = padding(version, bits_string, data_bits_capacity)

    if len(bits_string) == data_bits_capacity:
        return bits_string
    else:
        print("There are some error in the encoding")
        return

# FORMAT INFORMATION ENCODING

def remove_zeros(string: str) -> str:
    
    """Given a string as an input remove the zeros in the head"""

    for i in range(len(string)):
        if string[i] != '0':
            break
    return string[i:] 

def XOR(string1: str, string2: str) -> str:

    """This function perfomed a XOR operation between two string of same lenght"""

    new_str = ''
    for i in range(len(string1)):
        new_str += str(int(string1[i]) ^ int(string2[i]))
    return new_str

def format_information_string(modules: int, EC_level: str, mask_mode: str) -> str:

    """The format information consists of a 15-bit sequence comprising 5 data bits and 10 BCH (Bose-Chaudhuri-Hocquenghem) (15,5) error corretion (EC) bits.
       The 5 data bits consist of 2 bits for the EC level and 3 for the masking.
        In BCH:
       
            - n = 2**m - 1: total message length, given by the original messages + Error Correcion bits (in our case 15)
            - k: information length, original message bits to be trasmitted (in our case 5, given by the 2 bits of EC type + 3 bits of Mask type)
            - r = n - k: redundance, lenght of the EC bits sequence (in our case 10)
            - t: correctable errors (in our case 3)
            - d_min >= 2t + 1 = 7: minimum distance (also known as Hamming distance), which is the parameter that determines error resilience. To understand this more simply, 
              let's visualize it from a geometric perspective as follows: imagine the code words as spheres of radius t. If the condition on d_min is satisfied, the spheres do 
              not overlap; every code word, even if noisy, falls only within one sphere, and it is guaranteed that t errors can be corrected unambiguously.
        
        The parametrs above mention are well-known and selected for reasons related to QR code efficiency. 
        The calculation of the 10 EC bits sequence works as in the follow example:
            1. message: 00101 --> convert to a polynomial based on the coefficent: m(x) = x**2 + 1
            2. generator polynomial: g(x) = x**10 + x**8 + x**5 + x**4 + x**2 + x + 1
            3. m(x)*x**10 = x**12 + x**10
            4. perfome the division and find the reminder of the operation: m(x)*x**10/g(x). To get the remainder we need to remove the highest order x**12. So:
               x**2*g(x) = x**12 + x**10 + x**7 + x**6 + x**4 + x**3 + *x**2 
               (x**12 + x**10) - (x**12 + x**10 + x**7 + x**6 + x**4 + x**3 + *x**2) = x**7 + x**6 + x**4 + x**3 + x**2
               For this example this first operation is enough, but if the remainder would have been >= x**10 the highest order of the generator polinomial then GOTO 3
            5. Add the remainder coefficents (bit information of the EC): 00101 + 0011011100
            6. XOR the final message for the mask bit sequence 101010000010010
        (pg. 87 Annex C, C.2 of ISO/IEC 18004:2015).
            """
    string = EC_level + mask_mode
    original = string
    string = string + (15 - len(string))*'0'    # This correspond to 3. (example. 00101 0000000000 --> x**12 + x**10)
    pol_gen = "10100110111" # generator polynomial g(x) coeffincents
    # Polynomial division in modul 2, GF(2). It is the binary approch to do the algebric polynomial operation
    while len(string) > 10: # The order of the remainder has to be <= than maximum order of g(x) since it means that m(x) is still divisible (In the example above mean x**9)
        string= remove_zeros(string)    # In the example above would be 101 0000000000
        pol_gen += (len(string) - len(pol_gen))*'0'
        string = XOR(string, pol_gen)   # In the example above 0000011011100
        string= remove_zeros(string)    # In the example above 11011100. Now since the maximum order is x**7, is not divisible anymore for x**10. So stop here.

    if string == "1": # In the case of EC_level 00 and mask mode 000
        string = "0"
        
    if len(string) < 10:
        string = (10 - len(string))*'0' + string
        
    string = original + string
    if modules >= 21:
        string = XOR(string, "101010000010010")
    else:
        string = XOR(string, "100010001000101")
    
    return string

def version_information_string(version: int) -> str:

    """The version information consists of a 18-bit sequence comprising 6 data bits and 12 BCH (Bose-Chaudhuri-Hocquenghem) (18,6) error corretion (EC) bits (pg. 87 Annex C, 
       C.1 of ISO/IEC 18004:2015). The 6 bits refer to the version of the QR Code.
       In BCH:
       
        The parameters above mention are well-known and selected for reasons related to QR code efficiency. 
        The calculation of the 10 EC bits sequence works as in the follow example:
            1. message: 000111 --> convert to a polynomial based on the coefficent: m(x) = x**2 + x + 1
            2. generator polynomial: g(x) = x**12 + x**11 + x**10 + x**9 + x**8 + x**5 + x**2 + 1
            3. m(x)*x**12 = x**14 + x**13 + x**12
            4. perfome the division end find the reminder of the operation: m(x)*x**12/g(x). To get the remainder we need to remove the highest order x**12. So:
               x**2*g(x) = x**14 + x**13 + x**12 + x**11 + x**10 + x**7 + x**4 + x**2
               (x**14 + x**13 + x**12) - (x**14 + x**13 + x**12 + x**11 + x**10 + x**7 + x**4 + x**2) = x**11 + x**10 + x**7 + x**4 + x**2
               For this example this first operation is enough, but if the remainder would have been >= x**12 the highest order of the generator polinomial then GOTO 3
            5. Add the remainder coefficents (bit information of the EC): 000111 + 110010010100
        (pg. 89 Annex D, D.2 of ISO/IEC 18004:2015).
            """
    
    string = decToBin(version, 6)
    original = string
    string = string + (18 - len(string))*'0'    
    pol_gen = "1111100100101" 
    
    # Polynomial division in modul 2, GF(2). It is the binary approch to do the algebric polynomial operation
    while len(string) > 12: 
        string= remove_zeros(string)    
        pol_gen += (len(string) - len(pol_gen))*'0'
        string = XOR(string, pol_gen)  
        string= remove_zeros(string)    
        
    if len(string) < 12:
        string = (12 - len(string))*'0' + string
        
    string = original + string
    
    return string
