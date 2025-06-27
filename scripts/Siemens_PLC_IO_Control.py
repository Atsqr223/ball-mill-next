# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 12:29:21 2025

@author: TCS
"""

import snap7
from snap7.util import set_bool
import snap7.type

def write_m0_0(plc, value):
    byte_index = 0
    bit_index = 0
    data = plc.read_area(snap7.type.Areas.MK, 0, byte_index, 1)
    set_bool(data, 0, bit_index, value)
    plc.write_area(snap7.type.Areas.MK, 0, byte_index, data)

# Connect to the PLC
plc = snap7.client.Client()
plc.connect('10.135.114.201', 0, 1)  

write_m0_0(plc, False)