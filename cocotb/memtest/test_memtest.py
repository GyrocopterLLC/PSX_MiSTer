import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_memtest(dut):

    dut.reset.value = 1
    cocotb.start_soon(Clock(dut.clk1x, 29.52, 'ns').start())
    # cocotb.start_soon(Clock(dut.clk2x, 14.76, 'ns').start())
    cocotb.start_soon(Clock(dut.clk3x, 9.84, 'ns').start())

    await ClockCycles(dut.clk1x, 100)
    dut.reset.value = 0

    # await ClockCycles(dut.clk1x, 100000)
    await Timer(5, 'ms')    