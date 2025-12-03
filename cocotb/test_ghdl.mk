# Makefile for cocotb

# defaults

SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

VHDL_SOURCES_MEM ?= $(PWD)/../rtl/SyncFifo.vhd
VHDL_SOURCES_MEM += $(PWD)/../rtl/SyncFifoFallThrough.vhd
VHDL_SOURCES_MEM += $(PWD)/../rtl/SyncFifoFallThroughMLAB.vhd
VHDL_SOURCES_MEM += $(PWD)/../rtl/SyncRam.vhd
VHDL_SOURCES_MEM += $(PWD)/../rtl/SyncRamDual.vhd
VHDL_SOURCES_MEM += $(PWD)/../rtl/SyncRamDualNotPow2.vhd
VHDL_SOURCES_MEM += $(PWD)/../sim/system/src/mem/RamMLAB.vhd
VHDL_SOURCES_MEM += $(PWD)/../sim/system/src/mem/SyncRamDualByteEnable.vhd
VHDL_SOURCES_MEM += $(PWD)/../sim/system/src/mem/dpram.vhd

VHDL_SOURCES ?= $(PWD)/../rtl/pGPU.vhd
VHDL_SOURCES += $(PWD)/../sim/system/src/mem/dpram.vhd
VHDL_SOURCES += $(PWD)/../rtl/justifier_sensor.vhd
VHDL_SOURCES += $(PWD)/../rtl/mul9s.vhd
VHDL_SOURCES += $(PWD)/../rtl/mul32u.vhd
VHDL_SOURCES += $(PWD)/../rtl/divider.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_cpu2vram.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_crosshair.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_dither.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_fillVram.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_line.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_overlay.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_pixelpipeline.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_poly.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_rect.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_videoout_async.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_videoout_sync.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_videoout.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_vram2cpu.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu_vram2vram.vhd
VHDL_SOURCES += $(PWD)/../rtl/gpu.vhd


# VERILOG_INCLUDE_DIRS ?= 

# use VHDL_SOURCES for VHDL files

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = gpu

# MODULE is the basename of the Python test file
COCOTB_TEST_MODULES = test_gpu

# Example of how to add a verilog define
# this is equivalent to `define INSERT_ERROR in the .v file
# COMPILE_ARGS ?= -DINSERT_ERROR 
# and this is how you'd do something like `define NUM_BITS 12
# COMPILE_ARGS ?= -DNUM_BITS=12

# for icarus verilog:
# COMPILE_ARGS ?= -DSIM
# WAVES ?= 1

# for verilator:
# COMPILE_ARGS ?= +define+SIM
# EXTRA_ARGS += --trace --trace-structs --trace-fst

# for ghdl
# COMPILE_ARGS ?= --std=08 -frelaxed
SIM_ARGS ?= --fst=dump.fst --ieee-asserts=disable
EXTRA_ARGS ?= --std=08 -frelaxed

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
