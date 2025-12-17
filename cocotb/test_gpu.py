import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock
import math
import numpy as np
import cv2

from gpu import *
from ddram_model import *

SCR_W = 320
SCR_H = 240

quit_all_coro = False

async def start_clocks(dut):
    global quit_all_coro

    # clk1x = 33.8688 MHz
    # clk2x = 67.7376 MHz (exactly 2x clk1x)
    # clkvid = 53.693175 MHz (about 1.585x clk1x)

    cocotb.start_soon(Clock(dut.clk1x, 29.52, 'ns').start())
    cocotb.start_soon(Clock(dut.clk2x, 14.76, 'ns').start())
    # cocotb.start_soon(Clock(dut.clk3x, 9.84, 'ns').start())
    cocotb.start_soon(Clock(dut.clkvid, 18.62, 'ns').start())

    while not quit_all_coro:
        await RisingEdge(dut.clk1x)
        dut.clk2xIndex.value = 1
        '''dut.clk3xIndex.value = 1'''

        # wait for falling edges:
        # make sure we don't accidentally trigger the 
        # rising edge of the faster clock on the same
        # cycle as the rising edge of the slower clock
        '''await FallingEdge(dut.clk3x) '''
        await FallingEdge(dut.clk2x)
        '''await RisingEdge(dut.clk3x)
        dut.clk3xIndex.value = 0'''
        await RisingEdge(dut.clk2x)
        dut.clk2xIndex.value = 0

async def frame_saver(dut):
    global quit_all_coro

    vid_dat = np.zeros((320,240,3),dtype=np.uint8)
    vidx = 0
    vidy = 0
    frame_num = 0
    while not quit_all_coro:
        await RisingEdge(dut.video_ce)
        if dut.video_hblank.value == 0 and dut.video_vblank.value == 0:
            vid_dat[vidx,vidy,0] = dut.video_r.value.to_unsigned()
            vid_dat[vidx,vidy,1] = dut.video_g.value.to_unsigned()
            vid_dat[vidx,vidy,2] = dut.video_b.value.to_unsigned()
            # dut._log.info(f"Recorded pixel {vidx}, {vidy} = {vid_dat[vidx,vidy,:]}")
            vidx += 1
            if vidx >= 320:
                dut._log.info(f"New line! Completed line {vidy}")
                vidx = 0
                vidy += 1
                if vidy >= 240:
                    # frame done!
                    dut._log.info('Frame done!')
                    cv2.imwrite(f'frame_{frame_num:03}.jpg', np.transpose(vid_dat, axes=(1,0,2)))
                    vid_dat[:] = 0
                    frame_num += 1
                    vidy = 0
        else:
            if vidx != 0 or vidy != 0:
                if dut.video_vsync.value == 1:
                    dut._log.info('Early frame write')
                    cv2.imwrite(f'frame_{frame_num:03}.jpg', np.transpose(vid_dat, axes=(1,0,2)))
                    vid_dat[:] = 0
                    frame_num += 1
                    vidx = 0
                    vidy = 0


async def hsync_talker(dut):
    global quit_all_coro

    hsync_count = 0
    while not quit_all_coro:
        await RisingEdge(dut.video_hsync)
        if dut.video_vsync.value == 1:
            hsync_count = 0
        dut._log.info(f"Hey, it's hsync {hsync_count}")
        hsync_count += 1


@cocotb.test()
async def test_gpu(dut):
    global quit_all_coro

    dut.clk1x.value = 0
    dut.clk2x.value = 0
    dut.clk2xIndex.value = 0
    dut.clkvid.value = 0
    dut.ce.value = 0
    dut.reset.value = 0

    dut.savestate_busy.value = 0
    dut.system_paused.value = 0

    dut.ditherOff.value = 0
    dut.interlaced480pHack.value = 0
    dut.REPRODUCIBLEGPUTIMING.value = 0
    dut.videoout_on.value = 1
    dut.isPal.value = 0
    dut.pal60.value = 0
    dut.fpscountOn.value = 0
    dut.noTexture.value = 0
    dut.textureFilter.value = 0
    dut.textureFilterStrength.value = 0
    dut.textureFilter2DOff.value = 0
    dut.dither24.value = 0
    dut.render24.value = 0
    dut.drawSlow.value = 0
    dut.debugmodeOn.value = 0
    dut.syncVideoOut.value = 0
    dut.syncInterlace.value = 0
    dut.rotate180.value = 0
    dut.fixedVBlank.value = 0
    dut.vCrop.value = 0
    dut.hCrop.value = 0

    dut.oldGPU.value = 0

    dut.Gun1CrosshairOn.value = 0
    dut.Gun1X.value = 0
    dut.Gun1Y_scanlines.value = 0
    dut.Gun1offscreen.value = 0

    dut.Gun2CrosshairOn.value = 0
    dut.Gun2X.value = 0
    dut.Gun2Y_scanlines.value = 0
    dut.Gun2offscreen.value = 0

    dut.cdSlow.value = 0

    dut.errorOn.value = 0
    dut.errorEna.value = 0
    dut.errorCode.value = 0

    dut.LBAOn.value = 0
    dut.LBAdisplay.value = 0

    dut.bus_addr.value = 0
    dut.bus_dataWrite.value = 0
    dut.bus_read.value = 0
    dut.bus_write.value = 0
    dut.dmaOn.value = 0
    dut.DMA_GPU_waiting.value = 0
    dut.DMA_GPU_writeEna.value = 0
    dut.DMA_GPU_readEna.value = 0
    dut.DMA_GPU_write.value = 0
    dut.vram_pause.value = 0
    dut.vram_BUSY.value = 0
    dut.vram_DOUT.value = 0
    dut.vram_DOUT_READY.value = 0
    dut.loading_savestate.value = 0
    dut.SS_reset.value = 0
    dut.SS_DataWrite.value = 0
    dut.SS_Adr.value = 0
    dut.SS_wren_GPU.value = 0
    dut.SS_wren_Timing.value = 0
    dut.SS_rden_GPU.value = 0
    dut.SS_rden_Timing.value = 0

    cocotb.start_soon(start_clocks(dut))

    ddram_model = ddr_model()
    cocotb.start_soon(ddram_model.run(dut))
    cocotb.start_soon(frame_saver(dut))
    cocotb.start_soon(hsync_talker(dut))

    await Timer(10, 'ns')
    dut.reset.value = 1
    await Timer(10, 'ns')
    dut.reset.value = 0
    dut.ce.value = 1
    await Timer(100, 'ns')
    # await send_triangle(dut, 160, 120, 240)
    # await gpu_soft_reset(dut)

    # await Timer(100, 'ns')
    # await gpu_send_gp1(dut, 0x03 << 24) # display enable
    await init_video(dut, SCR_W, SCR_H)
    await Timer(1, 'us')
    await RisingEdge(dut.clk1x)
    await setDithering(dut, 0)
    await send_triangle(dut, SCR_W//4, SCR_H//4, 120)
    await send_triangle(dut, 3*SCR_W//4, SCR_H//4, 120)
    await setDithering(dut, 1)
    await send_triangle(dut, SCR_W/2, 3*SCR_H//4, 120)
    await RisingEdge(dut.video_vsync) # first frame, kinda junk
    await Timer(1, 'ms')
    # await RisingEdge(dut.video_vsync) # second frame should look good
    # await Timer(2,'ms')

    quit_all_coro = True
    ddram_model.destroy()

