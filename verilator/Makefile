N:=cpu_top
SRCDIR:=../rtl
SIMDIR:= ../sim
BUILDDIR:= build
VERILATE_OUTDIR := obj_dir

# cancel implicit rules for .vhd, .v, and .sv source files
%.vhd : ;
%.v : ;
%.sv : ;

VERILOG_SOURCES := \
cpu_top.sv \
$(SIMDIR)/system/src/tb/sdram_model3x.sv \

VHDL_MEM_SRCS := \
$(SRCDIR)/SyncFifo.vhd \
$(SRCDIR)/SyncFifoFallThrough.vhd \
$(SRCDIR)/SyncFifoFallThroughMLAB.vhd \
$(SRCDIR)/SyncRam.vhd \
$(SRCDIR)/SyncRamDual.vhd \
$(SRCDIR)/SyncRamDualNotPow2.vhd \
$(SIMDIR)/system/src/mem/RamMLAB.vhd \
$(SIMDIR)/system/src/mem/SyncRamDualByteEnable.vhd \
$(SIMDIR)/system/src/mem/dpram.vhd \

# NOTES:
# ghdl did not like the declared signal in pexport in file export.vhd
# simply remove the "use" directives on altera stuff in file spu_ram.vhd
VHDL_PSX_SRCS := \
$(SIMDIR)/system/src/mem/dpram.vhd \
$(SIMDIR)/system/src/mem/RamMLAB.vhd \
$(SRCDIR)/export.vhd \
$(SRCDIR)/divider.vhd \
$(SRCDIR)/pGPU.vhd \
$(SRCDIR)/mul32u.vhd \
$(SRCDIR)/mul9s.vhd \
$(SRCDIR)/cheats.vhd \
$(SRCDIR)/gpu_fillVram.vhd \
$(SRCDIR)/gpu_cpu2vram.vhd \
$(SRCDIR)/gpu_vram2vram.vhd \
$(SRCDIR)/gpu_vram2cpu.vhd \
$(SRCDIR)/gpu_line.vhd \
$(SRCDIR)/gpu_rect.vhd \
$(SRCDIR)/gpu_poly.vhd \
$(SRCDIR)/gpu_pixelpipeline.vhd \
$(SRCDIR)/gpu_overlay.vhd \
$(SRCDIR)/gpu_dither.vhd \
$(SRCDIR)/gpu_videoout_async.vhd\
$(SRCDIR)/gpu_videoout_sync.vhd \
$(SRCDIR)/gpu_crosshair.vhd \
$(SRCDIR)/justifier_sensor.vhd \
$(SRCDIR)/gpu_videoout.vhd \
$(SRCDIR)/gpu.vhd \
$(SRCDIR)/irq.vhd \
$(SRCDIR)/pJoypad.vhd \
$(SRCDIR)/joypad_pad.vhd \
$(SRCDIR)/joypad_mem.vhd \
$(SRCDIR)/joypad.vhd \
$(SRCDIR)/timer.vhd \
$(SRCDIR)/dma.vhd \
$(SRCDIR)/exp2.vhd \
$(SRCDIR)/pGTE.vhd \
$(SRCDIR)/gte_mac0.vhd \
$(SRCDIR)/gte_mac123.vhd \
$(SRCDIR)/gte_UNRDivide.vhd \
$(SRCDIR)/gte.vhd \
$(SRCDIR)/mdec.vhd \
$(SRCDIR)/cd_xa_zigzag.vhd \
$(SRCDIR)/cd_xa.vhd \
$(SRCDIR)/cd_top.vhd \
$(SRCDIR)/memctrl.vhd \
$(SRCDIR)/sio.vhd \
$(SRCDIR)/spu_gauss.vhd \
$(SRCDIR)/spu.vhd \
$(SRCDIR)/datacache.vhd \
$(SRCDIR)/cpu.vhd \
$(SRCDIR)/memorymux.vhd \
$(SRCDIR)/memcard.vhd \
$(SRCDIR)/statemanager.vhd \
$(SRCDIR)/savestates.vhd \
$(SRCDIR)/psx_top.vhd \
$(SRCDIR)/psx_mister.vhd \
$(SRCDIR)/spu_ram.vhd 

VHDL_2_VERILOG_MODULES := \
gpu
# gpu_cpu2vram \
# gpu_crosshair \
# gpu_dither \
# gpu_fillVram \
# gpu_line \
# gpu_overlay \
# gpu_pixelpipeline \
# gpu_rect \
# gpu_videoout_async \
# gpu_videoout_sync \
# gpu_videoout \
# gpu_vram2cpu \
# gpu_vram2vram \

# memctrl \
# memorymux \
# gte \
# cpu \
# mdec \
# gpu

GENERATED_VERILOG := $(VHDL_2_VERILOG_MODULES:%=$(BUILDDIR)/%.v)

.PHONY: verilog verilate build ghdlimport trace clean

verilog: $(GENERATED_VERILOG)

verilate: $(VERILATE_OUTDIR)/V$(N).cpp

build: $(VERILATE_OUTDIR)/V$(N)

ghdlimport: $(BUILDDIR)/mem-obj08.cf $(BUILDDIR)/psx-obj08.cf

$(BUILDDIR)/mem-obj08.cf: $(VHDL_MEM_SRCS)
	@echo "GHDL Import (-i) for mem library"
	$(shell mkdir -p $(BUILDDIR))
	ghdl -i --std=08 --work=mem --workdir=$(BUILDDIR) -P$(BUILDDIR) $(VHDL_MEM_SRCS)

$(BUILDDIR)/psx-obj08.cf: $(VHDL_PSX_SRCS)
	@echo "GHDL Import (-i) for psx library"
	$(shell mkdir -p $(BUILDDIR))
	ghdl -i --std=08 --work=psx --workdir=$(BUILDDIR) -P$(BUILDDIR) $(VHDL_PSX_SRCS)

$(GENERATED_VERILOG): $(BUILDDIR)/mem-obj08.cf $(BUILDDIR)/psx-obj08.cf
	@echo "GHDL Make (-m) for $@"
	ghdl -m --std=08 --work=psx --workdir=$(BUILDDIR) -P$(BUILDDIR) -frelaxed $(basename $(notdir $@))
	@echo "GHDL Synth to Verilog for $@"
	ghdl synth --std=08 --work=psx --workdir=$(BUILDDIR) -P$(BUILDDIR) -frelaxed --out=verilog -o=$@ $(basename $(notdir $@)) 

$(VERILATE_OUTDIR)/V$(N).cpp: $(GENERATED_VERILOG) $(VERILOG_SOURCES) sim_main.cpp
	verilator --top-module $(N) --trace-fst -cc -O3 --exe $^

$(VERILATE_OUTDIR)/V$(N): $(VERILATE_OUTDIR)/V$(N).cpp
	make -C obj_dir -f V$N.mk V$N
	
# ./obj_dir/V$N.cpp: sim_main.cpp $(SRCS) $(DEPS)
# 	@echo
# 	@echo "### VERILATE ####"
# 	mkdir -p obj_dir
# 	#verilator --top-module $N --trace -cc -O3 --exe -CFLAGS "$(CFLAGS_SDL)" -LDFLAGS "$(LIBS_SDL)" $(INCLUDES) $(SRCS) sim_main.cpp
# 	verilator --top-module $N --trace-fst -cc -O3 --exe -CFLAGS "$(CFLAGS_SDL)" -LDFLAGS "$(LIBS_SDL)" $(INCLUDES) $(SRCS) sim_main.cpp

# ./obj_dir/V$N: verilate
# 	@echo
# 	@echo "### BUILDING SIM ###"
# 	make -C obj_dir -f V$N.mk V$N
# 	cp -a $D/roms obj_dir
# 	cp -a $D/chip/DSP/*.hex obj_dir
# 	test -s obj_dir/random_4m_words.hex || hexdump -vn8388608 -e '8/2 "%04x ""\n"' /dev/random > obj_dir/random_4m_words.hex

# sim: ./obj_dir/V$N
# 	@echo
# 	@echo "### SIMULATION (GUI) ###"
# 	@cd obj_dir && ./V$N -c 400000000

trace: $(VERILATE_OUTDIR)/V$N
	@echo
	@echo "### SIMULATION (trace) ###"
	@cd $(VERILATE_OUTDIR) && ./V$N -t -c 100000000 2> stderr.log

# trace2: ./obj_dir/V$N
# 	@echo
# 	@echo "### SIMULATION (trace) ###"
# 	@cd obj_dir && ./V$N -t -c 3000000000 -s 300000000

# gtkwave:
# 	gtkwave obj_dir/waveform.fst

# audio:
# 	ffmpeg -y -f s16le -ar 32k -ac 2 -i obj_dir/snes.aud snes.wav

clean:
	rm -rf $(BUILDDIR) $(VERILATE_OUTDIR)
