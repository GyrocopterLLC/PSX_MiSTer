module sdram_test(
    input clk,
    input reset,
    
    output reg sdram_rst_n,

    input dram_init_done, // finished initialization routine

    output reg [26:0] dram_addr,

    output test_wr_en,
    output [31:0] dram_wdat,
    input dram_write_complete,

    output test_rd_en,
    input [31:0] dram_rdat,
    input dram_read_ready,

    output reg [31:0] passcount,
    output reg [31:0] failcount
);

localparam WRITES_PER_PASS = 4096;
// localparam WRITES_PER_PASS = 2097152; // RUN IT ALLLLL

reg [15:0] rw_counter;

reg rnd_save = 0, rnd_restore = 0;
wire [15:0] rnd_out;

assign dram_wdat = {rnd_out, rnd_out};

rnd_vec_gen u_rndgen(
    .clk(clk),
    .next(dram_write_complete | dram_read_ready),
    .save(rnd_save),
    .restore(rnd_restore),
    .out(rnd_out)
);


reg dram_start = 0, dram_rnw = 0;

assign test_wr_en = (dram_start && (!dram_rnw));
assign test_rd_en = (dram_start && dram_rnw);

// FSM states and registers
reg [3:0] curr_state,next_state;

localparam RESET        = 4'h0;
localparam INIT1        = 4'h1;
localparam INIT2        = 4'h2;
localparam BEGIN_WRITE1 = 4'h3;
localparam BEGIN_WRITE2 = 4'h4;
// localparam BEGIN_WRITE3 = 4'h5;
// localparam BEGIN_WRITE4 = 4'h6;
localparam WRITE        = 4'h7;
localparam BEGIN_READ1  = 4'h8;
localparam BEGIN_READ2  = 4'h9;
// localparam BEGIN_READ3  = 4'hA;
// localparam BEGIN_READ4  = 4'hB;
localparam READ         = 4'hC;
localparam END_READ     = 4'hD;
localparam INC_PASSES   = 4'hE;

always @* begin
	case( curr_state )

		RESET:   next_state <= INIT1;
		INIT1:
				if( dram_init_done )
					next_state <= INIT2;
				else
					next_state <= INIT1;

		INIT2:        next_state <= BEGIN_WRITE1;
		BEGIN_WRITE1: next_state <= BEGIN_WRITE2;
		BEGIN_WRITE2: next_state <= WRITE;
		WRITE:
				if( dram_write_complete ) begin
                    if(rw_counter == (WRITES_PER_PASS - 1))
                        next_state <= BEGIN_READ1;
                    else
                        next_state <= BEGIN_WRITE2;
                end
				else
					next_state <= WRITE;

		BEGIN_READ1: next_state <= BEGIN_READ2;
		BEGIN_READ2: next_state <= READ;
		READ:
				if( dram_read_ready ) begin
                    if(rw_counter == (WRITES_PER_PASS - 1))
                        next_state <= END_READ;
                    else
                        next_state <= BEGIN_READ2;
                end
				else
				  next_state <= READ;

		END_READ:    next_state <= INC_PASSES;
		INC_PASSES:  next_state <= BEGIN_WRITE1;

		default: next_state <= RESET;
	endcase
end
	reg        check_in_progress; // when 1 - enables errors checking
	reg        reset_req = 1;
	reg [31:0] rst_cnt;
// FSM controller
always @(posedge clk) begin


	if (check_in_progress & dram_read_ready & (dram_rdat!={rnd_out,rnd_out})) failcount <= failcount + 1;
	 
	curr_state <= ( reset_req ) ? RESET : next_state;
	if(reset) begin
		reset_req <= 1;
		rst_cnt <= 0;
	end
	
	if(reset || reset_req) begin
		check_in_progress <= 0;
		passcount <= 0;
		failcount <= 0;
	end

	case( curr_state )

	//////////////////////////////////////////////////
	RESET: begin
		// various initializings begin

		check_in_progress <= 0;

		rnd_save <= 0;
		rnd_restore <= 0;

        dram_addr <= 0;
		dram_rnw <= 0;

        rw_counter <= 0;

		dram_start <= 0;
		reset_req <= 0;
		sdram_rst_n <= 0;
		rst_cnt <= 0;
		if(rst_cnt < 50000) begin
			rst_cnt <= rst_cnt + 1;
			curr_state <= RESET;
		end
	end

	INIT1: begin
		dram_start  <= 0; // end dram start
		sdram_rst_n <= 1;
	end

	//////////////////////////////////////////////////
	BEGIN_WRITE1: begin
		rnd_save <= 1;
		dram_rnw <= 0;
        dram_addr <= 0;
        rw_counter <= 0;
	end

	BEGIN_WRITE2: begin
		rnd_save   <= 0;
		dram_start <= 1;
	end

    WRITE: begin
		dram_start <= 0;
        if(dram_write_complete) begin
            dram_addr <= dram_addr + 4;
            rw_counter <= rw_counter + 1;
        end
    end

	//////////////////////////////////////////////////
	BEGIN_READ1: begin
		rnd_restore <= 1;
		dram_rnw <= 1;
        dram_addr <= 0;
        rw_counter <= 0;
	end

	BEGIN_READ2: begin
		rnd_restore <= 0;
		dram_start <= 1;
		check_in_progress <= 1;
	end

    READ: begin
		dram_start <= 0;
        if(dram_read_ready) begin
            dram_addr <= dram_addr + 4;
            rw_counter <= rw_counter + 1;
        end
    end

	END_READ: begin
		check_in_progress <= 0;
	end

	INC_PASSES: begin
		passcount <= passcount + 1;
	end

	endcase
end


endmodule
