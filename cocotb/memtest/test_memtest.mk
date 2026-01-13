# Makefile for cocotb

# defaults

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES ?= $(PWD)/memtest_top.v
VERILOG_SOURCES += $(PWD)/sdram_test.v
VERILOG_SOURCES += $(PWD)/sdram.sv
VERILOG_SOURCES += $(PWD)/rnd_vec_gen.v
VERILOG_SOURCES += $(PWD)/../MT48LC8M16A2.v


# VERILOG_INCLUDE_DIRS ?= 

# use VHDL_SOURCES for VHDL files

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = memtest_top

# MODULE is the basename of the Python test file
COCOTB_TEST_MODULES = test_memtest

# Example of how to add a verilog define
# this is equivalent to `define INSERT_ERROR in the .v file
# COMPILE_ARGS ?= -DINSERT_ERROR 
# and this is how you'd do something like `define NUM_BITS 12
# COMPILE_ARGS ?= -DNUM_BITS=12

# for icarus verilog:
COMPILE_ARGS ?= -DSIM
WAVES ?= 1

# for verilator:
# COMPILE_ARGS ?= +define+SIM
# EXTRA_ARGS += --trace --trace-structs --trace-fst

# for ghdl
# COMPILE_ARGS ?= --std=08 -frelaxed
# SIM_ARGS ?= --fst=dump.fst --ieee-asserts=disable
# EXTRA_ARGS ?= --std=08 -frelaxed

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
