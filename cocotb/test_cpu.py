import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock
import math
import numpy as np
import cv2
import struct

SCR_W = 320
SCR_H = 240

quit_all_coro = False

class FakeRam:
    def __init__(self):
        self.bios = [0]*(int(2**19)//4) # 512 K of BIOS as words
        self.ram = [0]*(int(2**21)//4) # 2 Meg of RAM as words
        self.scratch = [0]*(int(2**10)//4) # 1 K of scratchpad as words
        self.quit_now = False
    
    def load_bios(self, filename):
        with open(filename, 'rb') as fil:
            fileContent = fil.read()
            self.bios = struct.unpack("<"+"i"*(len(fileContent)//4), fileContent)
        
    def get_mem(self, addr):
        seg = (addr & 0xE0000000) >> 29
        raw_addr = addr & 0x1FFFFFFF
        if raw_addr < 0x800000: # ram
            return self.ram[raw_addr//4]
        elif raw_addr >= 0x1FC00000 and raw_addr < 0x1FC80000: # bios
            return self.bios[(raw_addr - 0x1FC00000)//4]
        else:
            return None
            # return 0

    def set_mem(self, addr, data) -> bool:
        seg = (addr & 0xE0000000) >> 29
        raw_addr = addr & 0x1FFFFFFF
        if raw_addr < 0x800000: # ram
            self.ram[raw_addr//4] = data
            return True
        else:
            return False
            # pass

    def destroy(self):
        self.quit_now = True 

    async def memory_listener(self, dut):
        while not self.quit_now:
            await RisingEdge(dut.clk1x)
            dut.mem_done.value = 0
            if dut.mem_request.value == 1:
                isdata = dut.mem_isData.value == 1
                isread = dut.mem_rnw.value == 1
                addr = dut.mem_addressData.value.to_unsigned() if isdata else dut.mem_addressInstr.value.to_unsigned()
                wrval = dut.mem_dataWrite.value.to_unsigned()

                # dut._log.info(f"isdata:{isdata}, isread{isread}, addr:{addr:08X}, wrval:{wrval:08X}")
                if isread:
                    memval = self.get_mem(addr)
                    await ClockCycles(dut.clk1x, 4)
                    dut.mem_done.value = 1
                    if memval is not None:
                        dut.mem_dataRead.value = memval
                    else:
                        dut.mem_dataRead.value = 0
                        dut._log.info(f"Read data  -- {addr:08X}")
                    # seg = (addr & 0xE0000000)
                    # raw_addr = addr & 0x1FFFFFFF
                    # if raw_addr >= 0x1F801080 and raw_addr < 0x1F801100:
                    #     dut._log.info(f"DMA Read  -- Addr: {addr:08X}, Data: {self.get_mem(addr):08X}")

                    # dut._log.info(f"Seg: {seg:08X}, raw: {raw_addr:08X}")
                else:
                    if not self.set_mem(addr, wrval):
                        dut._log.info(f"Write data -- {addr:08X}: {wrval:08X}")
                    # raw_addr = addr & 0x1FFFFFFF
                    # if raw_addr >= 0x1F801080 and raw_addr < 0x1F801100:
                    #     dut._log.info(f"DMA Write -- Addr: {addr:08X}, Data: {wrval:08X}")

                if isread and not isdata:
                    tag_bits = (addr & 0x0000000C) >> 2
                    # tagvalids depend on RAM or BIOS
                    if (addr & 0x3FFFFFFF) < 0x800000: # ram
                        if tag_bits == 0:
                            dut.mem_tagvalids.value = 0xF
                        elif tag_bits == 1:
                            dut.mem_tagvalids.value = 0xE
                        elif tag_bits == 2:
                            dut.mem_tagvalids.value = 0xC
                        elif tag_bits == 3:
                            dut.mem_tagvalids.value = 0x8
                    else: # bios
                        oldtagvalids = dut.mem_oldtagvalids.value.to_unsigned()
                        if tag_bits == 0:
                            dut.mem_tagvalids.value = oldtagvalids | 0x01
                        elif tag_bits == 1:
                            dut.mem_tagvalids.value = oldtagvalids | 0x02
                        elif tag_bits == 2:
                            dut.mem_tagvalids.value = oldtagvalids | 0x04
                        elif tag_bits == 3:
                            dut.mem_tagvalids.value = oldtagvalids | 0x08

                # dut.mem_done.value = 1
                # if isread:
                #     await raise_done_after_4(dut)


# async def raise_done_after_4(dut):
#     await ClockCycles(dut.clk1x, 4)
#     dut.mem_done.value = 1
#     await RisingEdge(dut.clk1x)
#     dut.mem_done.value = 0

async def start_clocks(dut):
    global quit_all_coro

    # clk1x = 33.8688 MHz
    # clk2x = 67.7376 MHz (exactly 2x clk1x)
    # clkvid = 53.693175 MHz (about 1.585x clk1x)

    cocotb.start_soon(Clock(dut.clk1x, 29.52, 'ns').start())
    cocotb.start_soon(Clock(dut.clk2x, 14.76, 'ns').start())
    cocotb.start_soon(Clock(dut.clk3x, 9.84, 'ns').start())

def set_all_inputs(dut):
    dut.clk1x.value = 0
    dut.clk2x.value = 0
    dut.clk3x.value = 0
    dut.ce.value = 0
    dut.reset.value = 1

    dut.TURBO.value = 0
    dut.TURBO_CACHE.value = 0
    dut.TURBO_CACHE50.value = 0

    dut.irqRequest.value = 0
    dut.dmaStallCPU.value = 0
    dut.cpuPaused.value = 0

    dut.mem_dataRead.value = 0
    dut.mem_done.value = 0
    dut.mem_fifofull.value = 0
    dut.mem_tagvalids.value = 0

    dut.cache_wr.value = 0
    dut.cache_data.value = 0
    dut.cache_addr.value = 0

    dut.dma_cache_Adr.value = 0
    dut.dma_cache_data.value = 0
    dut.dma_cache_write.value = 0

    dut.ram_done.value = 0
    dut.ram_rnw.value = 0
    dut.ram_dataRead.value = 0

    dut.gte_busy.value = 0
    dut.gte_readData.value = 0

    dut.SS_reset.value = 1
    dut.SS_DataWrite.value = 0
    dut.SS_Adr.value = 0
    dut.SS_wren_CPU.value = 0
    dut.SS_wren_SCP.value = 0
    dut.SS_rden_CPU.value = 0
    dut.SS_rden_SCP.value = 0

    dut.debug_firstGTE.value = 0

@cocotb.test()
async def test_cpu(dut):
    global quit_all_coro

    set_all_inputs(dut)

    cocotb.start_soon(start_clocks(dut))

    # load BIOS
    fakeram = FakeRam()
    fakeram.load_bios(r"../../../psx/bios/ps-30a.bin")
    # dut._log.info(f"bios length: {len(fakeram.bios)}")
    # dut._log.info(f"first word: {fakeram.bios[0]:08X}")
    cocotb.start_soon(fakeram.memory_listener(dut))

    await ClockCycles(dut.clk1x, 10)
    dut.reset.value = 1
    dut.SS_reset.value = 1
    await ClockCycles(dut.clk1x, 10)
    dut.reset.value = 0
    dut.SS_reset.value = 0
    await ClockCycles(dut.clk1x, 10)
    
    dut.ce.value = 1
    # await ClockCycles(dut.clk1x, 100000)
    await Timer(10, 'ms')
    

    quit_all_coro = True
    fakeram.destroy()

