import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock
import math
import numpy as np
import cv2

def init_ports(dut):
    dut.clk1x.value = 0
    dut.clk2x.value = 0
    dut.ce.value = 0
    dut.reset.value = 1
    dut.pauseNext.value = 0
    dut.loadExe.value = 0
    dut.exe_initial_pc.value = 0
    dut.exe_initial_gp.value = 0
    dut.exe_load_address.value = 0
    dut.exe_file_size.value = 0
    dut.exe_stackpointer.value = 0
    dut.fastboot.value = 0
    dut.PATCHSERIAL.value = 0
    dut.TURBO.value = 0
    dut.region_in.value = 0
    dut.ram_dataRead.value = 0
    dut.ram_done.value = 0
    dut.mem_in_request.value = 0
    dut.mem_in_rnw.value = 0
    dut.mem_in_isData.value = 0
    dut.mem_in_isCache.value = 0
    dut.mem_in_oldtagvalids.value = 0
    dut.mem_in_addressInstr.value = 0
    dut.mem_in_addressData.value = 0
    dut.mem_in_reqsize.value = 0
    dut.mem_in_writeMask.value = 0
    dut.mem_in_dataWrite.value = 0
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
    dut.SS_DataWrite.value = 0
    dut.SS_Adr.value = 0
    dut.SS_wren_SDRam.value = 0
    dut.SS_rden_SDRam.value = 0

@cocotb.test()
async def test_memorymux(dut):

    init_ports(dut)


    cocotb.start_soon(Clock(dut.clk1x, 30, 'ns').start())
    cocotb.start_soon(Clock(dut.clk2x, 15, 'ns').start())

    await ClockCycles(dut.clk1x, 20)
    dut.SS_reset.value = 0
    dut.reset.value = 0

    await ClockCycles(dut.clk1x, 20)
    dut.ce.value = 1

    await ClockCycles(dut.clk1x, 100)
    
    dut.mem_in_rnw.value = 1
    
    dut.mem_in_request.value = 1
    dut.mem_in_addressInstr.value = 0x80004000
    dut.mem_in_addressData.value = 0x80004000
    dut.mem_in_isData.value = 1
    await RisingEdge(dut.clk1x)
    dut.mem_in_request.value = 0
    await RisingEdge(dut.ram_ena)
    await ClockCycles(dut.clk1x, 3)
    dut.ram_done.value = 1
    await RisingEdge(dut.clk1x)
    dut.ram_done.value = 0

    await ClockCycles(dut.clk1x, 100)

    dut.mem_in_request.value = 1
    dut.mem_in_addressInstr.value = 0x80004000
    dut.mem_in_addressData.value = 0x80004000
    dut.mem_in_isData.value = 0
    await RisingEdge(dut.clk1x)
    dut.mem_in_request.value = 0
    await RisingEdge(dut.ram_ena)
    await ClockCycles(dut.clk1x, 3)
    dut.ram_done.value = 1
    await RisingEdge(dut.clk1x)
    dut.ram_done.value = 0
    await ClockCycles(dut.clk1x, 100)
    
    dut.mem_in_rnw.value = 0

    dut.mem_in_request.value = 1
    dut.mem_in_addressInstr.value = 0x80004000
    dut.mem_in_addressData.value = 0x80004000
    dut.mem_in_isData.value = 0
    await RisingEdge(dut.clk1x)
    dut.mem_in_request.value = 0
    await RisingEdge(dut.ram_ena)
    await ClockCycles(dut.clk1x, 3)
    dut.ram_done.value = 1
    await RisingEdge(dut.clk1x)
    dut.ram_done.value = 0
    await ClockCycles(dut.clk1x, 100)

    dut.mem_in_request.value = 1
    dut.mem_in_addressInstr.value = 0x80004000
    dut.mem_in_addressData.value = 0x80004000
    dut.mem_in_isData.value = 1
    await RisingEdge(dut.clk1x)
    dut.mem_in_request.value = 0
    await RisingEdge(dut.ram_ena)
    await ClockCycles(dut.clk1x, 3)
    dut.ram_done.value = 1
    await RisingEdge(dut.clk1x)
    dut.ram_done.value = 0
    await ClockCycles(dut.clk1x, 100)