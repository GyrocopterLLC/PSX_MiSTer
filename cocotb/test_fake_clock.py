import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb.clock import Clock

async def start_clocks(dut):
    # clk1x = 33.8688 MHz
    # clk2x = 67.7376 MHz (exactly 2x clk1x)
    # clk3x = 101.606400 MHz (exactly 3x clk1x)
    # clkvid = 53.693175 MHz (about 1.585x clk1x)

    cocotb.start_soon(Clock(dut.clk1x, 29.52, 'ns').start())
    cocotb.start_soon(Clock(dut.clk2x, 14.76, 'ns').start())
    cocotb.start_soon(Clock(dut.clk3x, 9.84, 'ns').start())


@cocotb.test()
async def test_fake_clock(dut):

    cocotb.start_soon(start_clocks(dut))

    await Timer(100,'us')
    