from cocotb.triggers import RisingEdge, ClockCycles, Timer
from random import getrandbits

'''
GPU ports:
    clk2x                : in  std_logic;
    ...
    vram_BUSY            : in  std_logic;                    
    vram_DOUT            : in  std_logic_vector(63 downto 0);
    vram_DOUT_READY      : in  std_logic;
    vram_BURSTCNT        : out std_logic_vector(7 downto 0) := (others => '0'); 
    vram_ADDR            : out std_logic_vector(27 downto 0) := (others => '0');                       
    vram_DIN             : out std_logic_vector(63 downto 0) := (others => '0');
    vram_BE              : out std_logic_vector(7 downto 0) := (others => '0'); 
    vram_WE              : out std_logic := '0';
    vram_RD              : out std_logic := '0';   
'''

# BUSY - high during writes
# BURSTCNT - number of sequential transactions to perform, start at address ADDR
#          - for a read, will pump out data with DOUT_READY high until BURSTCNT is reached
#          - for a write, takes in data when WE is high until BURSTCNT is reached
# ADDR - the usual meaning of a memory address. should be divisible by 8 since we
#      - are sending 64 bit transfers
# DOUT - data reads go here, coming from the DDR memory
# DOUT_READY - high when DOUT is valid
# RD - assert once with the ADDR and BURSTCNT to start a read
# DIN - the data write data, going into the DDR memory
# BE - byte enable, only applies to writes. each of the 8 bytes in the 64-bit input
#    - has a write flag. Writes the byte to that position when high. Valid on every
#    - write.
# WE - write data is valid this cycle. Can start a write when not in the middle of a burst already

class ddr_model:
    def __init__(self):
        self.quit_now = False
        self.slow_timing = 15
        self.first_time = True # write all the vram on the first read
        self.data = [getrandbits(32) for _ in range(2**20)]

    def destroy(self):
        self.quit_now = True 

    async def run(self, dut):
        dut.vram_BUSY.value = 0
        dut.vram_DOUT.value = 0
        dut.vram_DOUT_READY.value = 0
        while not self.quit_now:
            await RisingEdge(dut.clk2x)

            if dut.vram_WE.value == 1:
                burst_count = dut.vram_BURSTCNT.value.to_unsigned()
                addr = dut.vram_ADDR.value[27:2].to_unsigned()
                dut.vram_BUSY.value = 1
                i = 0
                while i < burst_count:
                    if dut.vram_WE.value == 1:
                        be = dut.vram_BE.value.to_unsigned()
                        data_in_high = dut.vram_DIN.value[63:32].to_unsigned()
                        data_in_low = dut.vram_DIN.value[31:0].to_unsigned()
                        if (be & 0xF0) == 0xF0:
                            self.data[addr + (2*i) + 1] = data_in_high
                        elif (be & 0xF0) == 0xC0:
                            self.data[addr + (2*i) + 1] = (data_in_high & 0xFFFF0000) | (self.data[addr + (2*i) + 1] & 0x0000FFFF)
                        elif (be & 0xF0) == 0x30:
                            self.data[addr + (2*i) + 1] = (data_in_high & 0x0000FFFF) | (self.data[addr + (2*i) + 1] & 0xFFFF0000)

                        if (be & 0x0F) == 0x0F:
                            self.data[addr + (2*i)] = data_in_low
                        elif (be & 0x0F) == 0x0C:
                            self.data[addr + (2*i)] = (data_in_low & 0xFFFF0000) | (self.data[addr + (2*i) + 1] & 0x0000FFFF)
                        elif (be & 0x0F) == 0x03:
                            self.data[addr + (2*i)] = (data_in_low & 0x0000FFFF) | (self.data[addr + (2*i) + 1] & 0xFFFF0000)

                        i += 1
                    await RisingEdge(dut.clk2x)
                dut.vram_BUSY.value = 0

            if dut.vram_RD.value == 1:
                if self.first_time:
                    self.first_time = False
                    with open("ramdump.txt", 'w') as fil:
                        for dumpaddr, dumpval in enumerate(self.data):
                            fil.write(f"{(dumpaddr*4):08X}: {dumpval:08X}\n")

                burst_count = dut.vram_BURSTCNT.value.to_unsigned()
                addr = dut.vram_ADDR.value[27:2].to_unsigned()
                i = 0
                while i < burst_count:
                    if self.slow_timing > 0:
                        dut.vram_DOUT_READY.value = 0
                        await ClockCycles(dut.clk2x, self.slow_timing)
                    dut.vram_DOUT.value = self.data[addr + (2*i)] + (self.data[addr + (2*i) + 1] << 32)
                    # dut._log.info(f'Reading {((addr + (2*i))<<2):08X}: {self.data[addr + (2*i)]:08X}')
                    # dut._log.info(f'    and {((addr + (2*i))<<2)+4:08X}: {self.data[addr + (2*i)+1]:08X}')
                    dut.vram_DOUT_READY.value = 1
                    i += 1
                    await RisingEdge(dut.clk2x)
                dut.vram_DOUT_READY.value = 0
