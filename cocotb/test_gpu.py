import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock
import math
from dataclasses import dataclass, field

quit_all_coro = False

@dataclass
class RECT_T:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

@dataclass
class DISPENV_T:
    disp: RECT_T = field(default_factory=lambda: RECT_T())
    screen: RECT_T = field(default_factory=lambda: RECT_T())
    isinter: bool = False
    isrgb24: bool = False
    reverse: bool = False

@dataclass
class DR_TPAGE_T:
    code: int = 0 # uint32_t code[1]

@dataclass
class DR_TWIN_T:
    code: int = 0 # uint32_t code[1]

@dataclass
class DR_AREA_T:
    code: list[int] = field(default_factory=lambda: [0,0]) # uint32_t code[2]

@dataclass
class DR_OFFSET_T:
    code: int = 0 # uint32_t code[1]

@dataclass
class FILL_T:
    r0: int = 0# uint8_t 
    g0: int = 0# uint8_t 
    b0: int = 0# uint8_t 
    code: int = 0 # uint8_t
    x0: int = 0 # uint16_t
    y0: int = 0 # uint16_t
    w: int = 0 # uint16_t
    h: int = 0 # uint16_t
    
@dataclass
class P_TAG:
    addr: int # 24 bits
    len: int # 8 bits
    color: int # 24 bits
    code: int # 8 bits

@dataclass
class DR_ENV_T:
    tpage: DR_TPAGE_T = field(default_factory=lambda: DR_TPAGE_T())
    twin: DR_TWIN_T = field(default_factory=lambda: DR_TWIN_T())
    area: DR_AREA_T = field(default_factory=lambda: DR_AREA_T())
    offset: DR_OFFSET_T = field(default_factory=lambda: DR_OFFSET_T())
    fill: FILL_T = field(default_factory=lambda: FILL_T())
    tag: int = 0

@dataclass
class DRAWENV_T:
    clip: RECT_T = field(default_factory=lambda: RECT_T())   # Drawing area   
    ofs: list[int] = field(default_factory=lambda: [0,0])  # {int16_t ofs[2]} GPU draw offset (relative to draw area)
    tw: RECT_T = field(default_factory=lambda: RECT_T())     # texture window
    tpage: int = 0x0A      # initial tpage value
    dtd: int = 1       # dither processing flag (simply OR'ed to tpage)
    dfe: int = 0       # drawing to display area blocked / allowed (simply OR'ed to tpage)
    isbg: int = 0      # Clear draw area if non-zero
    r0: int = 0        # Draw area clear color (if isbg iz nonzero)
    g0: int = 0
    b0: int = 0
    dr_env: DR_ENV_T  = field(default_factory=lambda: DR_ENV_T())   # GPU primitive cache area (used internally)

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

async def gpu_send_gp0(dut, value:int):
    dut.bus_addr.value = 0
    dut.bus_write.value = 1
    dut.bus_read.value = 0
    dut.bus_dataWrite.value = value
    await RisingEdge(dut.clk1x)
    dut.bus_dataWrite.value = 0
    dut.bus_write.value = 0

async def gpu_send_gp1(dut, value:int):
    dut.bus_addr.value = 4
    dut.bus_write.value = 1
    dut.bus_read.value = 0
    dut.bus_dataWrite.value = value
    await RisingEdge(dut.clk1x)
    dut.bus_dataWrite.value = 0
    dut.bus_write.value = 0
    dut.bus_addr.value = 0

async def gpu_soft_reset(dut):
    dut.bus_addr.value = 0
    dut.bus_read.value = 0
    dut.bus_write.value = 0
    dut.bus_dataWrite.value = 0
    await RisingEdge(dut.clk1x)
    dut.bus_addr.value = 4
    dut.bus_read.value = 0
    dut.bus_write.value = 1
    dut.bus_dataWrite.value = 0 # soft reset command to GP1
    await RisingEdge(dut.clk1x)
    dut.bus_addr.value = 0
    dut.bus_read.value = 0
    dut.bus_write.value = 0
    dut.bus_dataWrite.value = 0

async def ResetGraph(dut, mode):
    # psn00bsdk: adds interrupt callbacks, resets GPU
    # no interrupts or anything here, just reset
    await gpu_send_gp1(dut, 0x0)
    await ClockCycles(dut.clk1x, 4)

async def PutDispEnv(dut, env: DISPENV_T):
    # psn00bsdk - initializes display ranges, video mode, initial vram page
    gpu_video_mode = 0 # GPUSTAT bit 20: 0 = ntsc, 1 = pal
    mode = gpu_video_mode << 3
    mode = mode | ((1 if env.isrgb24 else 0) << 4)
    mode = mode | ((1 if env.isinter else 0) << 5)
    mode = mode | ((1 if env.reverse else 0) << 7)

    h_span = env.screen.w if env.screen.w != 0 else 256
    v_span = env.screen.h if env.screen.h != 0 else 240
    
    # calculate the horizontal and vertical display range values
    h_span = int(h_span * 10)
    if env.disp.w > 560:
        # 640 pixels
        mode = mode | (3 << 0)
        #h_span *= 4;
    elif env.disp.w > 400:
        # 512 pixels
        mode = mode | (2 << 0)
        #h_span *= 5;
    elif env.disp.w > 352:
        # 368 pixels
        mode = mode | (1 << 6)
        #h_span *= 7;
    elif env.disp.w > 280:
        # 320 pixels
        mode = mode | (1 << 0)
        #h_span *= 8;
    else:
        # 256 pixels
        mode = mode | (0 << 0)
        #h_span *= 10;
    
    if env.disp.h > 256:
        mode = mode | (1 << 2)
        #v_span /= 2;

    x = env.screen.x + 0x760
    y = env.screen.y + (0xa3 if gpu_video_mode != 0 else 0x88)
    h_span = int(h_span / 2)
    v_span = int(v_span / 2)

    fb_pos = (env.disp.x & 0x3FF)
    fb_pos = fb_pos | ((env.disp.y & 0x1FF) << 10)
    h_range = ((x - h_span) & 0xFFF)
    h_range = h_range | (((x + h_span) & 0xFFF) << 12)
    v_range = ((y - v_span) & 0x3FF)
    v_range = v_range | (((y + v_span) & 0x3FF) << 10)

    await gpu_send_gp1(dut, 0x05000000 | fb_pos) # set vram location to display
    await gpu_send_gp1(dut, 0x06000000 | h_range) # set horizontal display range
    await gpu_send_gp1(dut, 0x07000000 | v_range) # set vertical display range
    await gpu_send_gp1(dut, 0x08000000 | mode) # set video mode

def _get_window_mask(size: int):
    mask = size >> 3
    mask = mask | (mask << 1)
    mask = mask | (mask << 2)
    mask = mask | (mask << 4)
    return mask & 0x1F

async def PutDrawEnv(dut, env: DRAWENV_T):
    # DrawOTagEnv((const uint32_t *) 0xffffff, env)
    # EnqueueDrawOp(&_send_linked_list, DRAWOP_TYPE_DMA, _build_drawenv_ot(ot, env), 0)
    # DRAWOP_TYPE_DMA = 1
    # _send_linked_list in drawing.c
    #   SetDrawOpType(type);
    #   GPU_GP1 = 0x04000002; // Enable DMA request, route to GP0
    #   MADR = ot // (ends up being the address of the DR_ENV type)
    #   BCR = 0
    #   CHCR = 0x01000401 // ram to device, linked-list mode, start transfer
    # _build_drawenv_ot returns a DR_ENV pointer (to the one contained in DRAWENV_T)

    # Texture page (reset active page and set dither/mask bits)
    # setDrawTPage_T(&(prim->tpage), env->dfe & 1, env->dtd & 1, env->tpage);
    env.dr_env.tpage.code = 0xE1000000 | env.tpage | (env.dtd << 9) | (env.dfe << 10)

    # Texture window
    env.dr_env.twin.code = 0xE2000000 | _get_window_mask(env.tw.w) | (_get_window_mask(env.tw.h) << 5) \
        | ((env.tw.x & 0xF8) << 7) | ((env.tw.y & 0xF8) << 12)

    # Set drawing area
    # setDrawArea_T(&(prim->area), &(env->clip));
    # setDrawAreaXY_T(p, r->x, r->y, r->x + r->w - 1, r->y + r->h - 1)
    x1 = env.clip.x + env.clip.w - 1
    y1 = env.clip.y + env.clip.h - 1
    env.dr_env.area.code[0] = 0xE3000000 | (env.clip.x & 0x3FF) | ((env.clip.y & 0x3FF) << 10)
    env.dr_env.area.code[1] = 0xE4000000 | (x1 & 0x3FF) | ((y1 & 0x3FF) << 10)

    # setDrawOffset_T(
	# 	&(prim->offset), env->clip.x + env->ofs[0], env->clip.y + env->ofs[1]
	# );

    env.dr_env.offset.code = 0xE5000000 | ((env.clip.x + env.ofs[0]) & 0x7FF) | (((env.clip.y + env.ofs[1]) & 0x7FF) << 11)

    # next it performs a background fill, which we don't need because env.isbg == 0
    
    # finally, perform the GP1 commands.
    # psn00bsdk does this as a DMA transfer
    await gpu_send_gp0(dut, env.dr_env.tpage.code)
    await gpu_send_gp0(dut, env.dr_env.twin.code)
    await gpu_send_gp0(dut, env.dr_env.area.code[0])
    await gpu_send_gp0(dut, env.dr_env.area.code[1])
    await gpu_send_gp0(dut, env.dr_env.offset.code)
    

async def setResolution(dut, width, height):
    # ps1-tests: sets display and draw environments
    # SetDefDispEnv(0,0,width,height): psn00bsdk - initializes a DISPENV struct
    dispenv = DISPENV_T()
    dispenv.disp.x = 0
    dispenv.disp.y = 0
    dispenv.disp.w = width
    dispenv.disp.h = height
    # SetDefDrawEnv(0,0,1024,512): psn00bsdk - initializes a DRAWENV struct
    drawenv = DRAWENV_T()
    drawenv.clip.x = 0
    drawenv.clip.y = 0
    drawenv.clip.h = 1024
    drawenv.clip.w = 512
    drawenv.tw.w = 256
    drawenv.tw.h = 256
    
    # some variables depend on 480 lines...
    dispenv.isinter = height == 480
    drawenv.dfe = 1 if (height == 480) else 0

    await PutDispEnv(dut, dispenv)
    await PutDrawEnv(dut, drawenv)

async def SetDispMask(dut, mask: bool):
    # psn00bsdk - simple GP1 command
    # mask==True will enable display
    await gpu_send_gp1(dut,  0x03000000 | (0 if mask else 1))

async def init_video(dut, width: int, height: int):
    await ResetGraph(dut, 0) 
    await setResolution(dut, width, height)
    await SetDispMask(dut, True)

async def send_triangle(dut, cx, cy, a):
    # places a triangle centered at cx,cy
    # with side length a
    # color is preset as a gradient from
    # corner to corner

    h = a * math.sqrt(3)/2
    x = [
        int(cx - a/2),
        int(cx + a/2),
        int(cx)
    ]
    y = [
        int(cy + h/2),
        int(cy + h/2),
        int(cy - h/2)
    ]

    # polygon structure:
    #  - first word:
    # 31-29        001    polygon render
    #   28         1/0    gouraud / flat shading
    #   27         1/0    4 / 3 vertices
    #   26         1/0    textured / untextured
    #   25         1/0    semi-transparent / opaque
    #   24         1/0    raw texture / modulation
    #  23-0        rgb    first color value.
    #  - subsequent words:
    #  color       xxBBGGRR (optional, only for gouraud shading)
    #  vertex      YYYYXXXX (required, two signed 16 bit values)
    #  UV          ClutVVUU or PageVVUU (optional, only for textured polygons) 
    code = 0x30 # polygon render, gouraud shading, 3 vertices, no texture, opaque

    poly_words = [
        (code << 24) + (0 << 16) + (0 << 8) + 255, # code and color1
        (y[0] << 16) + x[0], # vertex1
        (0 << 24) + (0 << 16) + (255 << 8) + 0, # color2
        (y[1] << 16) + x[1], # vertex2
        (0 << 24) + (255 << 16) + (0 << 8) + 0, # color3
        (y[2] << 16) + x[2], # vertex3
    ]
    
    dut.bus_addr.value = 0
    dut.bus_read.value = 0
    dut.bus_write.value = 0
    for word in poly_words:
        await RisingEdge(dut.clk1x)
        dut.bus_dataWrite.value = word
        dut.bus_write.value = 1

    await RisingEdge(dut.clk1x)
    dut.bus_dataWrite.value = 0
    dut.bus_write.value = 0
    

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
    await init_video(dut, 320, 240)
    await Timer(1, 'us')
    await send_triangle(dut, 160, 120, 240)
    for _ in range(15):
        await Timer(100, 'us')
        dut._log.info("100us passed")
    # await Timer(2,'ms')

    quit_all_coro = True
