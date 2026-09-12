import matplotlib.pyplot as plt

from qr_ec import qr_encoding_blocks
from qr_bulding import build_qr_code
from qr_encoding import find_mode, encode_data
        
#-----------------------------------------------------------------------------------------------------------------------------------
# A. Version (for standard QR Code from 1 to 40).
# 0. Modules: N° of modules.
# 1. Number_of_Alignment_Pattern: N° if Alignment Patterns.
# 2. Row/Col: row an colum of all possible combination position for the alignment pattern (pg. 91 Table E.1 ISO/IEC 18004:2015).
# 3. EC: Error correction levels for each module L, M, Q, H.
# 4. Total_number_of_codewords: represent the total number of bytes available for a specific version.
# 5. Remainder_Bits: number or bits to add at the ned of the final codewords to fill the total number of bits. 
# 6. Number_of_data_codewords: represent the number of bytes for the specific oly of the data and not considering the EC and Remainder bits.
# 7. Number_of_data_bits: represent the maximum number of bits so bytes*8. It can be threfore easily calculate from step 6.
# 8. Numeric: maximum encoding space for number mode.
# 9. Alphanumeric: rapresent the maximum encoding space for alphanumeric mode.
# 10 Byte: rapresent the maximum encoding space for bytes mode.
# 11. Kanji: rapresent the maximum encoding space for Japanese charactes.
# 12. Number_of_EC_codewords: Maximum number of EC codewords (bytes) that can be used for a specific version.
# 13. Value_of_p: number of misdecoded protection codewords.
# 14. Number_of_error_correction_blocks_1: This approach is used to make the most of EC algorithms and, by employing interleaving, to ensure greater resistance to physical effects on the QR code.
# 14. Number_of_error_correction_blocks_2: This approach is used to make the most of EC algorithms and, by employing interleaving, to ensure greater resistance to physical effects on the QR code.
# 16. Error_correction_per_block: (c,k,r), c = total number of codewords, k = number of data codewords, r = error correction capacity (bytes).

dict_qr_info = {}

with open("QR_CODE_DB.txt", "r") as file:
	lines = file.readlines()
file.close()

for i, line in enumerate(lines):
	l = line.split()
	if i == 0:
		dict_qr_info["cols"] = {}
		for j, ele in enumerate(l[1:]):
			dict_qr_info["cols"][ele] = j
	else:
		dict_qr_info[l[0]+l[4]] = [] 
		for ele in l[1:]:
			if ele.isdigit():
				dict_qr_info[l[0]+l[4]].append(int(ele))
			else:
				dict_qr_info[l[0]+l[4]].append(ele)
                
# EC Level to EC bits code
ec_code = {'L':"01",
           'M':"00",
           'Q':"11",
           'H':"10"}
#-----------------------------------------------------------------------------------------------------------------------------------

data = "Hello, world! 123"
version = "1"
ec_mode = "L"
mask_mode = ""
mode = find_mode(data)
code_word = encode_data(data, mode, int(version), dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Number_of_data_bits"]])
if code_word != None:
    code_word = qr_encoding_blocks(code_word, 
                                    dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Number_of_error_correction_blocks"]], 
                                    dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Error_correction_per_block"]], 
                                    dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Total_number_of_codewords"]])

    print("Version: ",version)
    print("Mode: ",mode)
    print("EC Level: ", ec_mode, ec_code[ec_mode])
    print("Final codeword + EC: ", code_word, len(code_word))

    matrix = build_qr_code(version,
                           dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Modules"]], 
                           dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Row/Col"]],
                           ec_code[ec_mode], 
                           code_word,
                           mask_mode)

        
    fig, ax =  plt.subplots(1,1, figsize = (10,10))

    ax.imshow(matrix, cmap='gray')
    ax.set_xticks([i for i in range(dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Modules"]]+8)])
    ax.set_yticks([i for i in range(dict_qr_info[version+ec_mode][dict_qr_info["cols"]["Modules"]]+8)])
    #ax[0].grid()
    #ax[1].grid()
    #ax[0].axis('off')
    plt.show()
