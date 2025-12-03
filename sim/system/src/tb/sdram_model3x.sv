module sdram_model3x
#(
    parameter DOREFRESH = 0//,
    // parameter INITFILE = "NONE",
    // parameter SCRIPTLOADING = 0,
    // parameter FILELOADING = 0
)
(
    input              clk,
    input              clk3x,
    input              refresh,
    input   [26 : 0]   addr,
    input              req,
    input              ram_dma,
    input   [1:0]      ram_dmacnt,
    input              ram_iscache,
    input              rnw,
    input   [3:0]      be,
    input   [31:0]     di,
    output reg [127:0] dout,
    output reg [31:0]  do32,
    output reg         done,
    output reg [3:0]   cache_wr,
    output reg [31:0]  cache_data,
    output reg [7:0]   cache_addr,
    output reg         dma_wr,
    output reg [31:0]  dma_data,
    output reg         reqprocessed,
    output reg         ram_idle,
    input   [22:0]     ram_dmafifo_adr,
    input   [31:0]     ram_dmafifo_data ,
    input              ram_dmafifo_empty,
    output reg         ram_dmafifo_read//,
    // output reg [29:0]  fileSize,
    // output reg [31:0]  exe_initial_pc,
    // output reg [31:0]  exe_initial_gp,
    // output reg [31:0]  exe_load_address,
    // output reg [31:0]  exe_file_size,
    // output reg [31:0]  exe_stackpointer
);

localparam cycles_per_refresh = 780;
localparam BURST_LENGTH = 8;
localparam CAS_LATENCY = 2;

logic clk1xToggle;
logic clk1xToggle3X;
logic clk1xToggle3X_1;
logic clk3xIndex;

logic [BURST_LENGTH+CAS_LATENCY:0] data_ready_delay1;

logic req_buffer;
logic refresh_buffer;
logic [26:0] addr_buffer;
logic rnw_buffer;

logic [12:0] lastbank;
integer refreshcnt;
logic initFromFile;
logic reqprocessed_3x;
logic req_1;
logic refresh_1;
logic cache_buffer;
logic cache_buffer_next;
logic cache_done_0;
logic cache_done_1;
logic cache_done_2;
logic cache_done_3;
logic [3:0] cache_wr_next;

logic dma_buffer;
logic dma_done;
logic dma_ack;
logic [1:0] dma_count_3x;
logic [1:0] dma_count;
logic [1:0] dma_counter;
logic [127:0] dma_do;

localparam  STATE_IDLE      = 0,
            STATE_WAIT      = 1,
            STATE_RW1       = 2,
            STATE_RW2       = 3,
            STATE_IDLE_9    = 4,
            STATE_IDLE_8    = 5,
            STATE_IDLE_7    = 6,
            STATE_IDLE_6    = 7,
            STATE_IDLE_5    = 8,
            STATE_IDLE_4    = 9,
            STATE_IDLE_3    = 10,
            STATE_IDLE_2    = 11,
            STATE_IDLE_1    = 12,
            STATE_RFSH      = 13;

logic [3:0] state;

always_ff @(posedge clk) begin
    clk1xToggle <= ~clk1xToggle;

    done <= done_3x;
    reqprocessed <= reqprocessed_3x;

    ram_idle <= 1'b0;
    if((state == STATE_IDLE) || (state == STATE_IDLE_1) || (state == STATE_IDLE_2) || (state == STATE_RW1) || (state == STATE_RW2))
    begin
        if(refreshcnt < (cycles_per_refresh - 16) && req_buffer == 1'b0 ) begin
            ram_idle <= 1'b1;
        end
    end

    if (done_3x) begin
        if(addr_buffer[0]) begin
            do32 <= {8'h00, dout[31:8]}
        end else begin
            do32 <= dout[31:0];
        end
    end

    dma_wr <= 1'b0;
    dma_ack <= 1'b0;

    if(dma_wr) begin
        if(dma_counter < dma_count) begin
            dma_wr <= 1'b1;
            dma_counter <= dma_counter = 2'd1;
            if(dma_counter == 2'd0) dma_data <= dma_do[ 63:32];
            if(dma_counter == 2'd1) dma_data <= dma_do[ 95:64];
            if(dma_counter == 2'd2) dma_data <= dma_do[127:96];
        end
    end

    if(dma_done) begin
         dma_ack     <= 1'b1;
         dma_wr      <= 1'b1;
         dma_data    <= dout[31:0];
         dma_do      <= dout;
         dma_counter <= 2'd0;
         dma_count   <= dma_count_3x;
    end

end

always_ff @(posedge clk3x) begin

    reg [26:0] addr_rotate;
    reg [7:0]  data [(2**27)-1:0];

    clk1xToggle3x   <= clk1xToggle;
    clk1xToggle3X_1 <= clk1xToggle3X;
    clk3xIndex    <= 1'b0;
    if (clk1xToggle3X_1 == clk1xToggle) begin
        clk3xIndex <= 1'b1;
    end
    if(done) begin
    done_3x <= 1'b0;
    end
    if(dma_ack) begin
    dma_done <= 1'b0;
    end

    cache_wr <= 4'h0;
    cache_done_0 <= 1'b0;
    cache_done_1 <= 1'b0;
    cache_done_2 <= 1'b0;
    cache_done_3 <= 1'b0;
    if(cache_done_0) begin cache_data <= dout[ 31: 0]; cache_wr <= cache_wr_next; cache_wr_next <= {cache_wr_next[2:0], 1'b0}; end
    if(cache_done_1) begin cache_data <= dout[ 63:32]; cache_wr <= cache_wr_next; cache_wr_next <= {cache_wr_next[2:0], 1'b0}; end
    if(cache_done_2) begin cache_data <= dout[ 95:64]; cache_wr <= cache_wr_next; cache_wr_next <= {cache_wr_next[2:0], 1'b0}; end
    if(cache_done_3) begin cache_data <= dout[127:96]; cache_wr <= cache_wr_next; cache_wr_next <= {cache_wr_next[2:0], 1'b0}; end

    if(reqprocessed) begin
        reqprocessed_3x <= 1'b0;
    end

    ram_dmafifo_read <= 1'b0;

    if(clk3xIndex && req) begin
        req_buffer <= 1'b1;
    end

    refresh_1 <= refresh;
    if(refresh && (!refresh_1)) begin
        refresh_buffer <= 1'b1;
    end

    if(DOREFRESH && refreshcnt < 1000) begin
        refreshcnt <= refreshcnt + 1;
    end

    data_ready_delay1 <= {1'b0, data_ready_delay1[10:1]};

    if(data_ready_delay1[6] == 1'b1 and dma_buffer == 1'b0 and cache_buffer_next == 1'b0) begin done_3x  <= 1'b1; end
    if(data_ready_delay1[4] == 1'b1 and cache_buffer_next == 1'b1)                        begin done_3x  <= 1'b1; end
    if(data_ready_delay1[6] == 1'b1 and dma_buffer == 1'b1)                               begin dma_done <= 1'b1; end
    
    if(data_ready_delay1[7] == 1'b1)                               begin cache_buffer_next <= cache_buffer; end
    if(data_ready_delay1[6] == 1'b1 and cache_buffer_next == 1'b1) begin cache_done_0 <= 1'b1; end
    if(data_ready_delay1[4] == 1'b1 and cache_buffer_next == 1'b1) begin cache_done_1 <= 1'b1; end
    if(data_ready_delay1[2] == 1'b1 and cache_buffer_next == 1'b1) begin cache_done_2 <= 1'b1; end
    if(data_ready_delay1[0] == 1'b1 and cache_buffer_next == 1'b1) begin cache_done_3 <= 1'b1; end

    if(data_ready_delay1[7]) begin
        addr_rotate = addr_buffer;
        integer i;
        for(i = 0; i < 7; i = i + 1) begin
            dout[7 + (i * 16):(i*16)] <= data[{addr_rotate[26:1],1'b0} + 0];
            dout[15 + (i * 16): 8 + (i*16)] <= data[{addr_rotate[26:1],1'b0} + 1];
            addr_rotate[9:1] = addr_rotate[9:1] + 1;
        end
    end

    case(state)
    STATE_IDLE: begin
        if(DOREFRESH && (refresh_buffer || refreshcnt > cycles_per_refresh)) begin
            state <= STATE_RFSH;
            if(refreshcnt > cycles_per_refresh) begin
                refreshcnt <= refreshcnt - cycles_per_refresh + 1;
            end else begin
                refreshcnt <= 0;
            end
            refresh_buffer <= 1'b0;
        end
        else if(ram_dmafifo_empty == 1'b0) begin
            data[{ram_dmafifo_adr[22:1],1'b0} + 3] = ram_dmafifo_data[31:24];
            data[{ram_dmafifo_adr[22:1],1'b0} + 2] = ram_dmafifo_data[23:16];
            data[{ram_dmafifo_adr[22:1],1'b0} + 1] = ram_dmafifo_data[15: 8];
            data[{ram_dmafifo_adr[22:1],1'b0} + 0] = ram_dmafifo_data[ 7: 0];
            lastbank         <= ram_dmafifo_adr[22:10];
            ram_dmafifo_read <= 1'b1;
            rnw_buffer       <= 1'b0;
            state            <= STATE_WAIT;
        end 
        else if((req || req_buffer) && (!rnw)) begin
            if(be[3]) data[{addr[26:1], 1'b0} + 3] = di[31:24];
            if(be[2]) data[{addr[26:1], 1'b0} + 2] = di[23:16];
            if(be[1]) data[{addr[26:1], 1'b0} + 1] = di[15: 8];
            if(be[0]) data[{addr[26:1], 1'b0} + 0] = di[ 7: 0];
            req_buffer       <= 1'b0;
            rnw_buffer       <= 1'b0;
            done_3x          <= 1'b1;
            state            <= STATE_WAIT;
        end 
        else if((req || req_buffer) && rnw) begin
            req_buffer <= 1'b0;
            addr_buffer <= addr;
            rnw_buffer <= 1'b1;
            state <= STATE_WAIT;

            cache_buffer <= ram_iscache;
            cache_addr <= addr[11:4];
            if(addr[3:2] == 2'b00) cache_wr_next <= 4'b0001;
            if(addr[3:2] == 2'b01) cache_wr_next <= 4'b0010;
            if(addr[3:2] == 2'b10) cache_wr_next <= 4'b0100;
            if(addr[3:2] == 2'b11) cache_wr_next <= 4'b1000;

            dma_buffer <= ram_dma;
            reqprocessed_3x <= ram_dma;
            dma_count_3x <= ram_dmacnt;
        end
    end
    STATE_WAIT: begin
        state <= STATE_RW1;
    end

    STATE_RW1: begin
        if(rnw_buffer) begin
            state <= STATE_IDLE_9;
            data_ready_delay1[CAS_LATENCY+BURST_LENGTH] <= 1'b1;
        end else begin
            state <= STATE_RW2;
        end
    end

    STATE_RW2: begin
        if((!ram_dmafifo_empty) && ram_dmafifo_adr[22:10] == lastbank) begin
            data[{ram_dmafifo_addr[22:1], 1'b0} + 3] = ram_dmafifo_data[31:24];
            data[{ram_dmafifo_addr[22:1], 1'b0} + 2] = ram_dmafifo_data[23:16];
            data[{ram_dmafifo_addr[22:1], 1'b0} + 1] = ram_dmafifo_data[15: 8];
            data[{ram_dmafifo_addr[22:1], 1'b0} + 0] = ram_dmafifo_data[ 7: 0];
            ram_dmafifo_read <= 1'b1;
            state <= STATE_RW1;
        end else begin
            state <= STATE_IDLE2;
        end
    end
    STATE_IDLE_9: state <= STATE_IDLE_8;
    STATE_IDLE_8: state <= STATE_IDLE_7;
    STATE_IDLE_7: state <= STATE_IDLE_6;
    STATE_IDLE_6: state <= STATE_IDLE_5;
    STATE_IDLE_5: state <= STATE_IDLE_4;
    STATE_IDLE_4: state <= STATE_IDLE_3;
    STATE_IDLE_3: state <= STATE_IDLE_2;
    STATE_IDLE_2: state <= STATE_IDLE_1;

    STATE_IDLE_1: begin
        state <= STATE_IDLE;
        if(DOREFRESH && (refreshcnt > cycles_per_refresh)) begin
            refreshcnt <= refreshcnt - cycles_per_refresh + 1;
            state <= STATE_RFSH;
        end
    end

    STATE_RFSH: state <= STATE_IDLE_5;

    default: state <= STATE_IDLE;

    endcase

end

endmodule
