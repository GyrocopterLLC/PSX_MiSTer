import os
from pathlib import Path

from cocotb_tools.runner import get_runner

def test_my_design_runner():
    sim = os.getenv("SIM", "ghdl")
    proj_path = Path(__file__).resolve().parent.parent
    print(proj_path)
    sources = [proj_path / "rtl/divider.vhd"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel = "divider",
    )
    
    runner.test(hdl_toplevel = "divider", test_module="test_divider,")

if __name__ == '__main__':
    test_my_design_runner()