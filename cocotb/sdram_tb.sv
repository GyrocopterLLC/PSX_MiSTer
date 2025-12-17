module sdram_tb(
    input              init,        // reset to initialize RAM
	input              clk,         // clock ~100MHz
	input              clk_base,    // clock ~33MHz

	input              SDRAM_EN,    // Set all output SDRAM_* signals to Z ASAP if SDRAM2_EN is 0 
    
	input              refreshForce,                   
	output             ram_idle,    // used to tell the core a write command on ch2 will be accepted instantly               

	input      [26:0]  ch1_addr,    // 25 bit address for 8bit mode. addr[0] = 0 for 16bit mode for correct operations.
	output reg [127:0] ch1_dout,    // data output to cpu
	output reg [31:0]  ch1_dout32,  // data output to cpu
	input      [15:0]  ch1_din,     // data input from cpu
	input              ch1_req,     // request
	input              ch1_rnw,     // 1 - read, 0 - write
	input              ch1_dma,     // 1 - read 128bit for dma
	input      [ 1:0]  ch1_cntDMA,  // count of words-1 for dma read
	input              ch1_cache,   // 1 - read 128bit for cache
	output reg         ch1_ready,
	output reg [ 3:0]  cache_wr,    
	output reg [31:0]  cache_data,  
	output reg [ 7:0]  cache_addr,  
	output reg         dma_wr,  
	output reg         dma_reqprocessed,  
	output reg [31:0]  dma_data,  

	input      [26:0]  ch2_addr,    // 25 bit address for 8bit mode. addr[0] = 0 for 16bit mode for correct operations.
	output reg [31:0]  ch2_dout,    // data output to cpu
	input      [31:0]  ch2_din,     // data input from cpu
	input              ch2_req,     // request
	input              ch2_rnw,     // 1 - read, 0 - write
   input      [3:0]   ch2_be,      
	output reg         ch2_ready,
                      
	input      [26:0]  ch3_addr,    // 25 bit address for 8bit mode. addr[0] = 0 for 16bit mode for correct operations.
	output reg [31:0]  ch3_dout,    // data output to cpu
	input      [31:0]  ch3_din,     // data input from cpu
	input              ch3_req,     // request
	input              ch3_rnw,     // 1 - read, 0 - write
	input      [3:0]   ch3_be,
	output reg         ch3_ready,

	input      [26:0]  dmafifo_adr,   
	input      [31:0]  dmafifo_data, 
	input              dmafifo_empty, 
	output reg         dmafifo_read
);

wire [15:0] sdram_dq_write, sdram_dq_read;
wire [12:0] sdram_adr;
wire sdram_dqml;
wire sdram_dqmh;
wire [1:0] sdram_ba;
wire sdram_ncs;
wire sdram_nwe;
wire sdram_nras;
wire sdram_ncas;
wire sdram_cke;
wire sdram_clk;

sdram u_sdram_ctr(
	.init,		 // reset to initialize RAM	
	.clk,		 // clock ~100MHz
	.clk_base,	 // clock ~33MHz
	.SDRAM_EN,    // Set all output SDRAM_* signals to Z ASAP if SDRAM2_EN is 0 
	.SDRAM_DQ_OUT(sdram_dq_write),    // 16 bit bidirectional data bus
	.SDRAM_DQ_IN(sdram_dq_read),
	.SDRAM_A(sdram_adr),     // 13 bit multiplexed address bus
	.SDRAM_DQML(sdram_dqml),  // two byte masks
	.SDRAM_DQMH(sdram_dqmh),  // 
	.SDRAM_BA(sdram_ba),    // two banks
	.SDRAM_nCS(sdram_ncs),   // a single chip select
	.SDRAM_nWE(sdram_nwe),   // write enable
	.SDRAM_nRAS(sdram_nras),  // row address select
	.SDRAM_nCAS(sdram_ncas),  // columns address select
	.SDRAM_CKE(sdram_cke),   // clock enable
	.SDRAM_CLK(sdram_clk),   // clock for chip

	.refreshForce,
	.ram_idle,
	.ch1_addr,
	.ch1_dout,
	.ch1_dout32,
	.ch1_din,
	.ch1_req,
	.ch1_rnw,
	.ch1_dma,
	.ch1_cntDMA,
	.ch1_cache,
	.ch1_ready,
	.cache_wr,
	.cache_data,
	.cache_addr,
	.dma_wr,
	.dma_reqprocessed,
	.dma_data,
	.ch2_addr,
	.ch2_dout,
	.ch2_din,
	.ch2_req,
	.ch2_rnw,
	.ch2_be,
	.ch2_ready,
	.ch3_addr,
	.ch3_dout,
	.ch3_din,
	.ch3_req,
	.ch3_rnw,
	.ch3_be,
	.ch3_ready,
	.dmafifo_adr,
	.dmafifo_data,
	.dmafifo_empty,
	.dmafifo_read
);

MT48LC8M16A2 u_sdram_sim(
	.dq_in(sdram_dq_write),
	.dq_out(sdram_dq_read),
	.addr(sdram_adr),
	.ba(sdram_ba),
	.clk(sdram_clk),
	.cke(sdram_cke),
	.csb(sdram_ncs),
	.rasb(sdram_nras),
	.casb(sdram_ncas),
	.web(sdram_nwe),
	.dqm({sdram_dqmh, sdram_dqml})
);


endmodule
