import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock
from random import getrandbits

async def write_mem_ch1(dut, addr, data):
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = addr
    dut.ch1_din.value = data
    dut.ch1_req.value = 1
    dut.ch1_rnw.value = 0
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = 0
    dut.ch1_din.value = 0
    dut.ch1_req.value = 0
    dut.ch1_rnw.value = 0

async def read_mem_ch1(dut, addr):
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = addr
    dut.ch1_din.value = 0
    dut.ch1_req.value = 1
    dut.ch1_rnw.value = 1
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = 0
    dut.ch1_din.value = 0
    dut.ch1_req.value = 0
    dut.ch1_rnw.value = 0

async def write_mem_ch2(dut, addr, data):
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = addr
    dut.ch2_din.value = data
    dut.ch2_req.value = 1
    dut.ch2_rnw.value = 0
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = 0
    dut.ch2_din.value = 0
    dut.ch2_req.value = 0
    dut.ch2_rnw.value = 0

async def read_mem_ch2(dut, addr):
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = addr
    dut.ch2_din.value = 0
    dut.ch2_req.value = 1
    dut.ch2_rnw.value = 1
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = 0
    dut.ch2_din.value = 0
    dut.ch2_req.value = 0
    dut.ch2_rnw.value = 0

async def write_mem_ch3(dut, addr, data):
    await RisingEdge(dut.clk_base)
    dut.ch3_addr.value = addr
    dut.ch3_din.value = data
    dut.ch3_req.value = 1
    dut.ch3_rnw.value = 0
    await RisingEdge(dut.clk_base)
    dut.ch3_addr.value = 0
    dut.ch3_din.value = 0
    dut.ch3_req.value = 0
    dut.ch3_rnw.value = 0

async def read_mem_ch3(dut, addr):
    await RisingEdge(dut.clk_base)
    dut.ch3_addr.value = addr
    dut.ch3_din.value = 0
    dut.ch3_req.value = 1
    dut.ch3_rnw.value = 1
    await RisingEdge(dut.clk_base)
    dut.ch3_addr.value = 0
    dut.ch3_din.value = 0
    dut.ch3_req.value = 0
    dut.ch3_rnw.value = 0

async def read_cache_ch1(dut, addr):
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = addr
    dut.ch1_din.value = 0
    dut.ch1_req.value = 1
    dut.ch1_cache.value = 1
    dut.ch1_rnw.value = 1
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = 0
    dut.ch1_din.value = 0
    dut.ch1_req.value = 0
    dut.ch1_cache.value = 0
    dut.ch1_rnw.value = 0

async def read_dma_ch1(dut, addr):
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = addr
    dut.ch1_din.value = 0
    dut.ch1_req.value = 1
    dut.ch1_dma.value = 1
    dut.ch1_rnw.value = 1
    await RisingEdge(dut.clk_base)
    dut.ch1_addr.value = 0
    dut.ch1_din.value = 0
    dut.ch1_req.value = 0
    dut.ch1_dma.value = 0
    dut.ch1_rnw.value = 0

async def write_mem_ch2(dut, addr, data):
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = addr
    dut.ch2_din.value = data
    dut.ch2_req.value = 1
    dut.ch2_rnw.value = 0
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = 0
    dut.ch2_din.value = 0
    dut.ch2_req.value = 0
    dut.ch2_rnw.value = 0

async def read_mem_ch2(dut, addr):
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = addr
    dut.ch2_din.value = 0
    dut.ch2_req.value = 1
    dut.ch2_rnw.value = 1
    await RisingEdge(dut.clk_base)
    dut.ch2_addr.value = 0
    dut.ch2_din.value = 0
    dut.ch2_req.value = 0
    dut.ch2_rnw.value = 0

@cocotb.test()
async def test_sdram(dut):
    cocotb.start_soon(Clock(dut.clk, 10, 'ns').start())
    cocotb.start_soon(Clock(dut.clk_base, 30, 'ns').start())

    dut.init.value = 0
    dut.SDRAM_EN.value = 1
    dut.refreshForce.value = 0
    dut.ch1_addr.value = 0
    dut.ch1_din.value = 0
    dut.ch1_req.value = 0
    dut.ch1_rnw.value = 0
    dut.ch1_dma.value = 0
    dut.ch1_cntDMA.value = 0
    dut.ch1_cache.value = 0
    dut.ch2_addr.value = 0
    dut.ch2_din.value = 0
    dut.ch2_req.value = 0
    dut.ch2_rnw.value = 0
    dut.ch2_be.value = 0xF
    dut.ch3_addr.value = 0
    dut.ch3_din.value = 0
    dut.ch3_req.value = 0
    dut.ch3_rnw.value = 0
    dut.ch3_be.value = 0xF
    dut.dmafifo_adr.value = 0
    dut.dmafifo_data.value = 0
    dut.dmafifo_empty.value = 1

    await Timer(100, 'ns')

    dut.init.value = 1

    await Timer(100, 'ns')
    dut.init.value = 0

    await Timer(400, 'us')


    await write_mem_ch1(dut, 0x100, 0x35bd)
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x102, 0x88da)
    await ClockCycles(dut.clk_base, 10)

    await write_mem_ch2(dut, 0x110, 0x907b0101)
    await ClockCycles(dut.clk_base, 100)

    await write_mem_ch3(dut, 0x4110, 0x907b0101)
    await ClockCycles(dut.clk_base, 100)

    await read_mem_ch1(dut, 0x100)
    await ClockCycles(dut.clk_base, 100)
    await read_mem_ch1(dut, 0x110)
    await ClockCycles(dut.clk_base, 100) 
    await read_mem_ch2(dut, 0x110)
    await ClockCycles(dut.clk_base, 100) 

    await read_mem_ch3(dut, 0x4110)
    await ClockCycles(dut.clk_base, 100) 

    await write_mem_ch1(dut, 0x200, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x202, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x204, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x206, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x208, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x20A, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x20C, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x20E, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x210, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)
    await write_mem_ch1(dut, 0x212, getrandbits(16))
    await ClockCycles(dut.clk_base, 10)

    await read_cache_ch1(dut, 0x200)
    await ClockCycles(dut.clk_base, 10)
    await read_cache_ch1(dut, 0x100)
    await ClockCycles(dut.clk_base, 10)
    await read_cache_ch1(dut, 0x202)
    await ClockCycles(dut.clk_base, 10)
    await read_cache_ch1(dut, 0x204)
    await ClockCycles(dut.clk_base, 10)


    await Timer(10,'us')
