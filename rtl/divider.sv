
module divider #(
    parameter DIVIDEND_LENGTH = 44,
    parameter DIVISOR_LENGTH = 24,
    parameter QUOTIENT_LENGTH = 44,
    parameter REMAINDER_LENGTH = 24
)
(
    input logic clk,
    input logic start,
    output reg done,
    output reg busy,
    input logic [DIVIDEND_LENGTH-1:0] dividend,
    input logic [DIVISOR_LENGTH-1:0] divisor,
    output reg [QUOTIENT_LENGTH-1:0] quotient,
    output reg [REMAINDER_LENGTH-1:0] remainder
);

localparam integer bits_per_cycle = 1;
localparam QPOINTER_LENGTH = $clog2(QUOTIENT_LENGTH+1);
localparam XPOINTER_LENGTH = $clog2(DIVIDEND_LENGTH+1);

logic [DIVIDEND_LENGTH:0] dividend_u;
logic [DIVISOR_LENGTH:0] divisor_u;
logic [QUOTIENT_LENGTH:0] quotient_u = 0;
logic [DIVISOR_LENGTH:0] Akku;
logic [QPOINTER_LENGTH-1:0] QPointer;
logic done_buffer = 0;
logic sign_dividend = 0;
logic sign_divisor = 0;

logic [XPOINTER_LENGTH-1:0] XPointer;
logic [QPOINTER_LENGTH-1:0] QPointerNew;
logic [DIVISOR_LENGTH:0] AkkuNew;
logic Rdy_i;
logic [bits_per_cycle-1:0] Q_bits;
logic [DIVISOR_LENGTH:0] Diff;

integer i;

always_ff @(posedge clk) begin
    done_buffer <= 0;
    busy <= 0;
    // == Initialize loop ===============================================
    if(start) begin
        busy <= 1;
        dividend_u <= {1'b0, ($signed(dividend) >= 0 ? dividend : -dividend)};
        divisor_u <= {1'b0, ($signed(divisor) >= 0 ? divisor : -divisor)};

        sign_dividend <= dividend[DIVIDEND_LENGTH-1];
        sign_divisor <= divisor[DIVISOR_LENGTH-1];

        QPointerNew = QUOTIENT_LENGTH;
        XPointer = DIVIDEND_LENGTH;
        Rdy_i = 0;
        AkkuNew = 0;
    end else if(!Rdy_i) begin
        busy <= 1;
        AkkuNew = Akku;
        QPointerNew = QPointer;
        for (i = 1; i <= bits_per_cycle; i = i + 1) begin
            // Calculate output digit and new Akku ---------------------------
            Diff = AkkuNew - divisor_u;
            if(Diff[DIVISOR_LENGTH] == 0) begin // Does Y fit in Akku?
                Q_bits[bits_per_cycle-i] = 1; // YES: Digit is '1'
                AkkuNew = Diff << 1; // Diff -> Akku
            end else begin
                Q_bits[bits_per_cycle-i] = 0; // NO: Digit is '0'
                AkkuNew = AkkuNew << 1; // Shift Akku
            end
            // ---------------------------------------------------------------
            if (XPointer > 0) begin // divisor read completely?
                XPointer = XPointer - 1; // NO: Put next digit
                AkkuNew[0] = dividend_u[XPointer]; // in Akku
            end else begin
                AkkuNew[0] = 0; // YES: Read Zeros (post point)
            end
            // ---------------------------------------------------------------
            if (QPointerNew > 0 ) begin // Has this been the last cycle?
                QPointerNew = QPointerNew - 1; // NO: Prepare next cycle
            end else begin
                Rdy_i = 1; // YES: work done
                done_buffer <= 1;
            end
        end // for loop
        quotient_u[QPointer -: (bits_per_cycle)] <= Q_bits;
    end // !Rdy_i

    QPointer <= QPointerNew;
    Akku <= AkkuNew;

    if (sign_dividend ^ sign_divisor)
        quotient <= -quotient_u[QUOTIENT_LENGTH-1:0];
    else
        quotient <= quotient_u[QUOTIENT_LENGTH-1:0];

    if (sign_dividend)
        remainder <= -AkkuNew[REMAINDER_LENGTH:1];
    else
        remainder <= AkkuNew[REMAINDER_LENGTH:1];

    done <= done_buffer;

end // always_ff


endmodule
