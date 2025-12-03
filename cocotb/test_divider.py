import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock


async def test_divide(dut, x, y):
    dut._log.info(f"dividing {x} by {y}")
    await ClockCycles(dut.clk, 20)

    dut.start.value = 1
    dut.dividend.value = x
    dut.divisor.value = y

    await RisingEdge(dut.clk)

    dut.start.value = 0

    await RisingEdge(dut.done)

    quotient = dut.quotient.value.to_signed()
    remainder = dut.remainder.value.to_signed()

    if y != 0:
        equotient = int((abs(int(x)) / abs(int(y))))
        eremainder = int(abs(int(x)) % abs(int(y)))
        if (x > 0 and y < 0) or (x < 0 and y > 0):
            equotient = -equotient
        if (x < 0):
            eremainder = -eremainder
    else:
        equotient = -1
        eremainder = -1

    dut._log.info(f"expected quotient: {equotient}, expected remainder: {eremainder}")
    dut._log.info(f"quotient: {quotient}, remainder: {remainder}")

    if y != 0:
        assert(quotient == equotient)
        assert(remainder == eremainder)


@cocotb.test()
async def test_divider(dut):
    cocotb.start_soon(Clock(dut.clk, 2, 'ps').start())

    dut.start.value = 0
    dut.dividend.value = 0
    dut.divisor.value = 0

    await test_divide(dut, 32, 32)
    await test_divide(dut, 0, 0)
    await test_divide(dut, 1237141, 575434)
    await test_divide(dut, -32, 32)
    await test_divide(dut, 32, -32)
    await test_divide(dut, -32, -32)
    await test_divide(dut, 865, 22)
    await test_divide(dut, -865, 22)
    await test_divide(dut, -865, -22)
    await test_divide(dut, 865, -22)
    await test_divide(dut, 22, -865)
    await test_divide(dut, -22, -865)
    await test_divide(dut, -22, 865)
    await test_divide(dut, 22, 865)

    await ClockCycles(dut.clk, 100)