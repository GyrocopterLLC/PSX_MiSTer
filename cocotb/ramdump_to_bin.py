import struct
import re

ramdat = bytearray()

linere = re.compile('([0-9a-fA-F]{8}):\\s+([0-9a-fA-F]{8}),\\s+([0-9a-fA-F]{8}),\\s+([0-9a-fA-F]{8}),\\s+([0-9a-fA-F]{8})')

with open('psx_mister/cocotb/ramdump_bios_4sec.txt','r') as fil:
    for lines in fil.readlines():
        vals = linere.search(lines)
        if vals:
            loc = int(vals[1], 16)
            vals_ints = [int(bb, 16) for bb in vals.groups()[1:]]
            newbytes = struct.pack('<IIII',*vals_ints)
            ramdat.extend(newbytes)

with open('psx_mister/cocotb/ramdump_bios_4sec.bin','wb') as filo:
    filo.write(ramdat)
