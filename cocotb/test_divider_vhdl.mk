# Makefile for cocotb

# defaults

SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

VHDL_SOURCES ?= $(PWD)/../rtl/divider.vhd

# VERILOG_INCLUDE_DIRS ?= 

# use VHDL_SOURCES for VHDL files

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = divider

# MODULE is the basename of the Python test file
MODULE = test_divider

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
SIM_ARGS += --fst=dump.fst

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
