from qr_mask import micro_mask_dict, qr_mask_dict, qr_xoring, find_best_mask, qr_penalty_count
from qr_encoding import format_information_string, version_information_string

def create_square(matrix: list, c: tuple, radius: int, fill: bool = False, center: bool = False):

    """This function is used to create square pattern shapes. In particular in QR code we have two cases:
        1. Finder pattern
        2. Alignment pattern
       the function take four arguments as input:
        1. matrix: is list of list. The blank cavas from which the varius inforamations of the QR code are drawn.
        2. c: is a tuple containing the center coordinates where to draw the square in the matrix.
        3. radius: a int value specifing the dimenzion of the square, distance from the c coordinates.
        4. option: string to specify whether to color the inside of the square (True) or not (False)
        5. center: string to color the center of the square (True) or not (False)"""
    
    # Color the center point 
    if center:
        matrix[c[0]][c[1]] = 0 

    # Fill option by creating a list of radius positions
    if fill:
        radius = [abs(i-radius) for i in range(radius)]
    else:
        radius = [radius]

    # Loop alogn all radius positions
    for r in radius:
        for i in range(r*2+1):
            # Horizontal drawing
            matrix[c[0]-r][c[1]-r+i] = 0   
            matrix[c[0]+r][c[1]-r+i] = 0
            # Vertical drawing
            matrix[c[0]-r+i][c[1]-r] = 0   
            matrix[c[0]-r+i][c[1]+r] = 0

def create_finder_pattern(matrix: list, mask_matrix: list, modules: int):
    
    """Three identical patterns located at the upper left, upper right and lower left. Each finder pattern may be viewed as three superimposed concentric squares and is constructed of 
       dark 7x7 modules, light 5x5 modules and dark 3x3 modules. The ratio of module widths in each finder pattern is 1:1:3:1:1. The symbol is preferentially encoded so that similar 
       patterns have a low probability of being encountered elsewhere in the symbol, enabling rapid identification and unambiguosly defines the location and rotation orientation of symbol
       in the filed of view (pg. 24 chapter 6.3.3 ISO/IEC 18004:2015)."""
    
    if modules < 21:    # Condition for Micro QR Code
        c_matrix = [(3, 3)]
        c_mask_matrix = [(4, 4)]
    else:   # Condition for QR Code from version 21 to 40
        c_matrix = [(3, 3), (modules - 4,3), (3, modules - 4)]
        c_mask_matrix = [(4, 4), (modules - 5,4), (4, modules - 5)]

    # Loop for the three center position of the finder patter
    for c in c_matrix:
        create_square(matrix, c, radius=3)   # User the create_square fucntion to make the finder pattern
        create_square(matrix, c, radius=1, fill = True, center = True)
    
    # The mask matrix is used as a reference to know positions where info have already been added in the matrix
    # Differently from the matrix the radius is bigger since the finder pattern have a external white border
    # Here we are covering also the format information spots in the matrix. 
    for c in c_mask_matrix:
        create_square(mask_matrix, c, radius=4, fill = True, center = True)  
    
    # Correct for the top-right and bottom-left format information, pyt the line at index 9 back to white
    if modules >= 21: 
        for i in range(9):  
            mask_matrix[modules - 9][i] = 1
            mask_matrix[i][modules - 9] = 1

    # Mask the version information spot
    if modules >= 45:
        for i in range(modules - 11, modules - 8):
            for j in range(6):
                mask_matrix[i][j] = 0
                mask_matrix[j][i] = 0

def create_timing_pattern(matrix: list, mask_matrix: list, modules: int):
    
    """The horizontal and vertical timing patterns respectively consist of a one module wide row or column of alternating dark and light modules, commencing and ending with a dark module. They
       enable the symbol density and version to be determined and provide datum positions for determining modules cordinates (pg. 25 chapter 6.3.5 ISO/IEC 18004:2015)"""

    if modules < 21:
        offset = 0
        offset2 = 0
    else:
        offset = 7
        offset2 = 1

    # The lenght of the timing pattern is always the same of the version (modules)
    for i in range(7,modules-offset):
        mask_matrix[offset-offset2][i] = 0 # In the mask matrix fill all point with 0 (black pixel)
        mask_matrix[i][offset-offset2] = 0
        if i % 2 == 0:  # For the actual matrix alternate the white (1) and black (0) pixels
            matrix[offset-offset2][i] = 0
            matrix[i][offset-offset2] = 0
        else:
            matrix[offset-offset2][i] = 1
            matrix[i][offset-offset2] = 1 

def create_alignment_pattern(matrix: list, mask_matrix: list, modules: int, r_c: str):

    """Alignment patterns are present only in QR Code symbols of version 2 or larger. Each alignment pattern may be viewed as three superimposed concentric squares and is constructed of dark 
    5x5 modules, light 3x3 modules and a single central dark module. The number of alignment patterns depends on the symbol version and they shall be placed in all symbol of verison 2 or
    larger in defined positions (pg. 25 chapter 6.3.6).
    The cordinate posiitons are given by r_c (r = row, c = column)."""
    
    # Only if version is larger than 21
    if modules > 21:
        cc = []
        l = r_c.split(',') 
        for i in l: # from the r, c values find all possible combinations of rows and columns of possible center poisition of the patterns
            for j in l:
                r = int(i) 
                c = int(j)
                if (r <= 10 and c <= 10) or (r <= 10 and c >= modules - 7) or (r >= modules - 7 and c <= 10):   # check whether the center pattern is inside the region of the Finder Pattern
                    continue
                else:   
                    cc.append((r,c))    # Only in this case save the cordinate
        
        for c in cc:
            create_square(matrix, c, radius=2, center = True)  # create the pattern
            create_square(mask_matrix, c, radius=2, fill = True, center = True)

# FILL THE QR CODE WITH THE TOTAL CODEWORDS BIT STRING

def zig_zag_up(bit_string: str, matrix: list, mask_matrix: list, modules: int, posx: int, posy: int, count: int):
    for i in range(1,modules+1):
        for j in range(0,2):
            if mask_matrix[posy][posx] != 0:
                matrix[posy][posx] = int(bit_string[count])^1
                count += 1
            posx -= 1
        posy -= 1
        posx += 2 
    posy = 0

    return count, posy, "down"
    
def zig_zag_down(bit_string: str, matrix: list, mask_matrix: list, modules: int, posx: int, posy: int, count: int):
    for i in range(1,modules+1):
        for j in range(0,2):
            if mask_matrix[posy][posx] != 0:
                matrix[posy][posx] = int(bit_string[count])^1
                count += 1
            posx -= 1
        posy += 1
        posx += 2

    return count, posy-1, "up"

def fill_qr_code(bit_string: str, matrix: list, mask_matrix: list, modules: int):
    direction = "up"
    posy = modules-1
    count = 0
    for i in range(modules, 0, -1):
        posx = i
        if i%2 == 0:
            if i <= 6 and modules >= 21: # In this line there is the timig pattern. Therefore we have to move to the previous columns. Only for version from 1 to 40
                posx -= 1
            if direction == "up":
                try:
                    count, posy, direction = zig_zag_up(bit_string, matrix, mask_matrix, modules, posx, posy, count)
                except IndexError:
                    break
            elif direction == "down":
                count, posy, direction = zig_zag_down(bit_string, matrix, mask_matrix, modules, posx, posy, count)
    
def add_information(version: str, modules: int, ec_code: str, mask_mode: str, matrix: list):
    
    fis = format_information_string(ec_code, mask_mode)
    
    fi1 = [(0,8), (1,8), (2,8), (3,8), (4,8), (5,8), (7,8), (8,8), (8,7), (8,5), (8,4), (8,3), (8,2), (8,1), (8,0)]
    f12 = [(8,modules-1), (8,modules-2), (8,modules-3), (8,modules-4), (8,modules-5), (8,modules-6), (8,modules-7), (8,modules-8), (modules-7,8), (modules-6,8), (modules-5,8), (modules-4,8), (modules-3,8), (modules-2,8), (modules-1,8)]
    
    matrix[modules - 8][8] = 0
    for i, ele in enumerate(fi1):
        matrix[ele[0]][ele[1]] = int(fis[14-i])^1
        matrix[f12[i][0]][f12[i][1]] = int(fis[14-i])^1
    
    if modules > 45:
        vis = version_information_string(int(version))
        
def apply_masking(version: str, modules: int, ec_code: str, matrix: list, mask_matrix: list, mode: str = "") -> list:
    
    mask_mode = mode
    
    if mode and set(mode) <= {'0','1'} and len(mode) == 2:
        matrix = qr_xoring(modules, matrix, mask_matrix, micro_mask_dict, mode)
    elif mode and set(mode) <= {'0','1'} and len(mode) == 3:
        matrix = qr_xoring(modules, matrix, mask_matrix, qr_mask_dict, mode)
        add_information(version, modules, ec_code, mask_mode, matrix)
    elif mode == "":
        mask_mode = find_best_mask(version, modules, ec_code, matrix, mask_matrix, add_information)
        print("Mask Mode: ", mask_mode)
        if modules >= 21:
            matrix = qr_xoring(modules, matrix, mask_matrix, qr_mask_dict, mask_mode)
            add_information(version, modules, ec_code, mask_mode, matrix)
        elif modules < 21:
            matrix = qr_xoring(modules, matrix, mask_matrix, micro_mask_dict, mask_mode)
            add_information(version, modules, ec_code, mask_mode, matrix)
    else:
        print("Input non valido")
        return 0
    
    return matrix

def add_quite_zone(modules: int, matrix: list) -> list:
    
    line = [1 for i in range(4)]

    for i in range(modules):
        matrix[i] = line + matrix[i] + line

    line = [1 for i in range(modules+8)]

    for i in range(4):
        matrix.insert(0, line)
        matrix.append(line)

def build_qr_code(version: str, modules: int, r_c: str, ec_code: str, bit_string: str, mask_mode: str = ""):
    
    matrix = []
    mask_matrix = []

    for i in range(modules):
        matrix.append([1]*(modules))    
        mask_matrix.append([1]*(modules))

    create_finder_pattern(matrix, mask_matrix, modules)
    create_timing_pattern(matrix, mask_matrix, modules)
    create_alignment_pattern(matrix, mask_matrix, modules, r_c)
    fill_qr_code(bit_string, matrix, mask_matrix, modules)
    matrix = apply_masking(version, modules, ec_code, matrix, mask_matrix, mode = mask_mode)
    add_quite_zone(modules, matrix)

    return matrix
