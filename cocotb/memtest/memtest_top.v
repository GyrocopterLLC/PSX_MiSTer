module memtest_top(

    input clk1x,
    input clk3x,
    input reset,

    output [31:0] passcount,
    output [31:0] failcount
);

wire sdram_rst_n;
wire sdram_idle;

wire [26:0] addr;
wire [31:0] wdat;
wire [31:0] rdat;

wire init_write;
wire init_read;
wire write_done;
wire read_done;

sdram_test u_test(
    .clk(clk1x),
    .reset(reset),
    .sdram_rst_n(sdram_rst_n),
    .dram_init_done(sdram_idle),
    .dram_addr(addr),
    .test_wr_en(init_write),
    .dram_wdat(wdat),
    .dram_write_complete(write_done),
    .test_rd_en(init_read),
    .dram_rdat(rdat),
    .dram_read_ready(read_done),
    .passcount(passcount),
    .failcount(failcount)
);
wire [15:0]     SDRAM_DQ_READ;
wire [15:0]     SDRAM_DQ_WRITE;
wire [12:0]     SDRAM_A;
wire            SDRAM_DQML;
wire            SDRAM_DQMH;
wire  [1:0]     SDRAM_BA;
wire            SDRAM_nCS;
wire            SDRAM_nWE;
wire            SDRAM_nRAS;
wire            SDRAM_nCAS;
wire            SDRAM_CKE;
wire            SDRAM_CLK;

sdram u_sdram_controller(

    .init(~sdram_rst_n),
    .clk(clk3x),
    .clk_base(clk1x),
    .SDRAM_EN(~reset),
    .SDRAM_DQ_IN(SDRAM_DQ_READ),
    .SDRAM_DQ_OUT(SDRAM_DQ_WRITE),
    .SDRAM_A(SDRAM_A),
    .SDRAM_DQML(SDRAM_DQML),
    .SDRAM_DQMH(SDRAM_DQMH),
    .SDRAM_BA(SDRAM_BA),
    .SDRAM_nCS(SDRAM_nCS),
    .SDRAM_nWE(SDRAM_nWE),
    .SDRAM_nRAS(SDRAM_nRAS),
    .SDRAM_nCAS(SDRAM_nCAS),
    .SDRAM_CKE(SDRAM_CKE),
    .SDRAM_CLK(SDRAM_CLK),
    .refreshForce(),
    .ram_idle(sdram_idle),
    .ch1_addr(addr),
    .ch1_dout(),
    .ch1_dout32(rdat),
    .ch1_din(16'b0),
    .ch1_req(init_read),
    .ch1_rnw(1'b1),
    .ch1_dma(1'b0),
    .ch1_cntDMA(2'b0),
    .ch1_cache(1'b0),
    .ch1_ready(read_done),
    .cache_wr(),
    .cache_data(),
    .cache_addr(),
    .dma_wr(),
    .dma_reqprocessed(),
    .dma_data(),
    .ch2_addr(addr),
    .ch2_dout(),
    .ch2_din(wdat),
    .ch2_req(init_write),
    .ch2_rnw(1'b0),
    .ch2_be(4'b1111),
    .ch2_ready(write_done),
    .ch3_addr(27'b0),
    .ch3_dout(),
    .ch3_din(32'b0),
    .ch3_req(1'b0),
    .ch3_rnw(1'b1),
    .ch3_be(4'b1111),
    .ch3_ready(),
    .dmafifo_adr(27'b0),
    .dmafifo_data(32'b0),
    .dmafifo_empty(1'b1),
    .dmafifo_read()
);

MT48LC8M16A2 u_sdram(
    .dq_in(SDRAM_DQ_WRITE),
    .dq_out(SDRAM_DQ_READ),
    .addr(SDRAM_A),
    .ba(SDRAM_BA),
    .clk(SDRAM_CLK),
    .cke(SDRAM_CKE),
    .csb(SDRAM_nCS),
    .rasb(SDRAM_nRAS),
    .casb(SDRAM_nCAS),
    .web(SDRAM_nWE),
    .dqm({SDRAM_DQMH, SDRAM_DQML})
);

endmodule
