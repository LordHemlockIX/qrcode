#import numpy as np
#import matplotlib.pyplot as plt


from qr_encoding import find_mode, encode_data, format_information_string, version_information_string
from qr_bulding import *
from qr_ec import qr_encoding_blocks
from qr_bulding import build_qr_code

ec_code = {'L':"01",
           'M':"00",
           'Q':"11",
           'H':"10"}

data = "01234567"
version = 1
ec_mode = "M"
mask_mode = "010"
mode = find_mode(data)
code_word = encode_data(data, mode, version, 128)
fis = format_information_string(ec_code[ec_mode], mask_mode)
vis = version_information_string(version)
code_word = qr_encoding_blocks(code_word, [1,0], "26,16,4", 26)

print("Version: ",version)
print("Mode: ",mode)
print("EC Level: ", ec_mode, ec_code[ec_mode])
print("Mask Mode: ",mask_mode)
print("Version Information: ", vis)
print("Format Information: ", fis)
print("Final codeword + EC: ", code_word, len(code_word))

build_qr_code(21, "nan", code_word)
