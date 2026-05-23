import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from qr_info import db_qr_info, db_alphacoding
from qr_bulding import *
from qr_encoding import find_mode, encode_data



data = "Hello World!"
mode = find_mode(data, db_alphacoding)
print(encode_data(data, mode, 4, 288))

"""modules = 25
r_c = "6,18"

blank = []
mask_blank = []

for i in range(modules):
    blank.append([1]*(modules))    
    mask_blank.append([1]*(modules))

create_finder_pattern(blank, mask_blank, modules)
create_timing_pattern(blank, mask_blank, modules)
create_alignment_pattern(blank, mask_blank, modules, r_c)

fig, ax = plt.subplots(1,2)

ax[0].imshow(blank, cmap="gray")
ax[0].set_xticks(np.arange(0, modules, 1))
ax[0].set_yticks(np.arange(0, modules, 1))
ax[0].grid()

ax[1].imshow(mask_blank, cmap="gray")
ax[1].set_xticks(np.arange(0, modules, 1))
ax[1].set_yticks(np.arange(0, modules, 1))
ax[1].grid()
plt.show()"""