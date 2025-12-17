import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock
from cocotb.simtime import get_sim_time
import math
import numpy as np
import cv2
import struct

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
            if len(fileContent) > 0x80000:
                assert(False)
            
            endpos = (len(fileContent)+3)//4
            self.bios[:endpos] = struct.unpack("<"+"i"*(len(fileContent)//4), fileContent)

    def load_exe(self, filename, offset):
        with open(filename, 'rb') as fil:
            fileContent = fil.read()[0x800:] # trim the exe header placed by psn00bsdk
            
            if len(fileContent) + offset > 0x200000:
                assert(False)
            startpos = offset // 4
            endpos = (offset + len(fileContent) + 3)//4
            self.ram[startpos:endpos] = struct.unpack("<"+"i"*(len(fileContent)//4), fileContent)

    def get_mem(self, addr):

        if addr < 0x800000: # RAM
            return self.ram[addr//4]
        elif addr >= 0x800000 and addr < 0x880000:
            return self.bios[(addr - 0x800000)//4]
        else:
            return None
        

    def set_mem(self, addr, data, mask) -> bool:
        if addr < 0x800000: # ram
            prev_data = self.ram[addr//4]
            new_data = (data & 0xFF000000) if (mask & 0x8 == 0x8) else (prev_data & 0xFF000000)
            new_data += (data & 0x00FF0000) if (mask & 0x4 == 0x4) else (prev_data & 0x00FF0000)
            new_data += (data & 0x0000FF00) if (mask & 0x2 == 0x2) else (prev_data & 0x0000FF00)
            new_data += (data & 0x000000FF) if (mask & 0x1 == 0x1) else (prev_data & 0x000000FF)
            self.ram[addr//4] = new_data
            return True
        else:
            return False
        
    def dump_ram(self, filename):
        with open(filename, 'w') as fil:
            i = 0
            while i < len(self.ram):
                fil.write(f"{4*i:08X}: ")
                for j in range(4):
                    fil.write(f"{self.ram[i+j]:08X}, ")
                fil.write('\n')
                i = i + 4

    def destroy(self):
        self.quit_now = True

    async def cache_read_clk3x(self, dut):
        while not self.quit_now:
            await RisingEdge(dut.clk3x)
            if dut.ram_ena.value == 1 and dut.ram_cache.value == 1:
                addr = dut.ram_Adr.value.to_unsigned() & 0xFFFFFFF0
                dut.cache_addr.value = (dut.ram_Adr.value.to_unsigned() >> 4) & 0xFF
                await ClockCycles(dut.clk3x, 8)
                for i in range(4):
                    dut.cache_data.value = self.get_mem(addr + 4*i)
                    dut.cache_wr.value = 1<<i
                    await RisingEdge(dut.clk3x)
                    dut.cache_wr.value = 0
                    await RisingEdge(dut.clk3x)
                
    async def memory_listener(self, dut):
        cocotb.start_soon(self.cache_read_clk3x(dut))
        # first_print = False
        while not self.quit_now:
            await RisingEdge(dut.clk1x)
            if dut.ram_done.value == 1:
                dut.ram_done.value = 0
            if dut.ram_ena.value == 1:
                isread = dut.ram_rnw.value == 1
                addr = dut.ram_Adr.value.to_unsigned()
                wrval = dut.ram_dataWrite.value.to_unsigned()
                mask = dut.ram_be.value.to_unsigned()

                if isread:
                    memval = self.get_mem(addr)
                    await ClockCycles(dut.clk1x, 2 if (dut.ram_cache.value == 0) else 3)
                    dut.ram_done.value = 1
                    if memval is not None:
                        dut.ram_dataRead32.value = memval
                    else:
                        dut.ram_dataRead32.value = 0
                        dut._log.info(f"Read data  -- {addr:08X}")

                else:
                    if not self.set_mem(addr, wrval, mask):
                        dut._log.info(f"Write data -- {addr:08X}: {wrval:08X} (mask: {mask:02X})")
                    dut.ram_done.value = 1
                    # if not first_print:
                    #     if wrval != 0:
                    #         dut._log.info(f"addr:{addr:08X}, wrval:{wrval:08X}, mask:{mask:02X}")
                    #         dut._log.info(f"saving to {addr//4:08X}")
                    #         dut._log.info(f"new value is {self.ram[addr//4]:08X}")
                    #         first_print = True
                    # raw_addr = addr & 0x1FFFFFFF
                    # if raw_addr >= 0x1F801080 and raw_addr < 0x1F801100:
                    #     dut._log.info(f"DMA Write -- Addr: {addr:08X}, Data: {wrval:08X}")

# async def raise_done_after_4(dut):
#     await ClockCycles(dut.clk1x, 4)
#     dut.mem_done.value = 1
#     await RisingEdge(dut.clk1x)
#     dut.mem_done.value = 0

async def start_clocks(dut):
    global quit_all_coro

    # clk1x = 33.8688 MHz
    # clk2x = 67.7376 MHz (exactly 2x clk1x)
    # clk3x = 101.6064 MHz (exactly 3x clk1x)

    cocotb.start_soon(Clock(dut.clk1x, 29.52, 'ns').start())
    cocotb.start_soon(Clock(dut.clk2x, 14.76, 'ns').start())
    cocotb.start_soon(Clock(dut.clk3x, 9.84, 'ns').start())

def set_all_inputs(dut):
    dut.clk1x.value = 0
    dut.clk2x.value = 0
    dut.clk3x.value = 0
    dut.ce.value = 0
    dut.reset_intern.value = 1

    dut.cpuPaused.value = 0

    dut.loadExe.value = 0
    dut.exe_initial_pc.value = 0
    dut.exe_initial_gp.value = 0
    dut.exe_load_address.value = 0
    dut.exe_file_size.value = 0
    dut.exe_stackpointer.value = 0

    dut.fastboot.value = 0
    dut.PATCHSERIAL.value = 0
    dut.TURBO_MEM.value = 0
    dut.TURBO_COMP.value = 0
    dut.TURBO_CACHE.value = 0
    dut.TURBO_CACHE50.value = 0
    dut.biosregion.value = 0

    dut.ram_dataRead32.value = 0
    dut.ram_done.value = 0

    dut.gte_busy.value = 0
    dut.gte_readData.value = 0

    dut.cache_wr.value = 0
    dut.cache_data.value = 0
    dut.cache_addr.value = 0

    dut.bios_memctrl.value = 0

    dut.ex1_memctrl.value = 0
    dut.bus_exp1_dataRead.value = 0

    dut.bus_memc_dataRead.value = 0

    dut.bus_pad_dataRead.value = 0

    dut.bus_sio_dataRead.value = 0

    dut.bus_memc2_dataRead.value = 0

    dut.bus_irq_dataRead.value = 0

    dut.bus_dma_dataRead.value = 0

    dut.bus_tmr_dataRead.value = 0

    dut.cd_memctrl.value = 0
    dut.bus_cd_dataRead.value = 0

    dut.bus_gpu_dataRead.value = 0
    dut.bus_gpu_stall.value = 0

    dut.bus_mdec_dataRead.value = 0
    dut.spu_memctrl.value = 0
    dut.bus_spu_dataRead.value = 0
    dut.ex2_memctrl.value = 0
    dut.bus_exp2_dataRead.value = 0
    dut.ex3_memctrl.value = 0
    dut.bus_exp3_dataRead.value = 0
    dut.com0_delay.value = 0
    dut.com1_delay.value = 0
    dut.com2_delay.value = 0
    dut.com3_delay.value = 0
    dut.loading_savestate.value = 0
    dut.SS_reset.value = 1

async def show_ticks(dut):
    while not quit_all_coro:
        await Timer(1000,'us')
        dut._log.info(f"Elapsed: {get_sim_time('us')} us")

@cocotb.test()
async def test_cpu(dut):
    global quit_all_coro

    set_all_inputs(dut)

    cocotb.start_soon(start_clocks(dut))
    cocotb.start_soon(show_ticks(dut))

    # load BIOS
    fakeram = FakeRam()
    fakeram.load_bios(r"../../../psx/bios/ps-30a.bin")
    # fakeram.load_exe(r"/mnt/c/Users/david/Desktop/code-in-io.bin", 0x10000)
    # dut._log.info(f"bios length: {len(fakeram.bios)}")
    # dut._log.info(f"first word: {fakeram.bios[0]:08X}")
    cocotb.start_soon(fakeram.memory_listener(dut))

    await ClockCycles(dut.clk1x, 10)
    dut.reset_intern.value = 1
    dut.SS_reset.value = 1
    await ClockCycles(dut.clk1x, 10)
    dut.SS_reset.value = 0
    # dut.icpu.PC.value = 0x80011684
    await ClockCycles(dut.clk1x, 40)
    dut.reset_intern.value = 0
    
    await ClockCycles(dut.clk1x, 10)
    # dut.icpu.SS_DataWrite.value = 0x801FFF00 # initial stack pointer
    # dut.icpu.SS_wren_CPU.value = 1
    # dut.icpu.SS_Adr.value = 96 + 29 # reg 29 = sp
    # await RisingEdge(dut.clk1x)
    # dut.icpu.SS_DataWrite.value = 0
    # dut.icpu.SS_wren_CPU.value = 0
    # dut.icpu.SS_Adr.value = 0

    dut.ce.value = 1
    # await ClockCycles(dut.clk1x, 100000)
    await Timer(4000, 'ms')

    fakeram.dump_ram("ramdump.txt")


    quit_all_coro = True
    fakeram.destroy()

