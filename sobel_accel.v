module sobel_accel #
(
    parameter IMG_WIDTH  = 1000,
    parameter IMG_HEIGHT = 467,
    // Calculate counter widths
    parameter C_X_WIDTH = $clog2(IMG_WIDTH),
    parameter C_Y_WIDTH = $clog2(IMG_HEIGHT)
)
(
    input  wire                  clk,
    input  wire                  rst_n,
    input  wire [23:0]           in_pixel,
    input  wire                  in_valid,
    output reg  [23:0]           out_pixel,
    output reg                   out_valid
);

    // grayscale conversion
    wire [7:0] r = in_pixel[23:16];
    wire [7:0] g = in_pixel[15:8];
    wire [7:0] b = in_pixel[7:0];
    // Use 10 bits for intermediate precision
    wire [9:0] gray_wide = (r*30 + g*59 + b*11) / 100;
    wire [7:0] gray      = gray_wide[7:0];

    // Line buffers
    reg [7:0] linebuf1 [0:IMG_WIDTH-1];
    reg [7:0] linebuf2 [0:IMG_WIDTH-1];

    // 3x3 Window Shift Registers
    reg [7:0] pix0, pix1, pix2; // From linebuf2 (Row N-2)
    reg [7:0] pix3, pix4, pix5; // From linebuf1 (Row N-1)
    reg [7:0] pix6, pix7, pix8; // From gray (Row N)

    // Pixel counters
    reg [C_X_WIDTH-1:0] x_cnt;
    reg [C_Y_WIDTH-1:0] y_cnt;

    // Registers for Sobel calculation
    // Gx/Gy can range from -1020 to +1020 (4*255), needs 11 bits signed
    reg signed [10:0] gx, gy;
    // Mag is abs(Gx) + abs(Gy), can range from 0 to 2040, needs 11 bits
    reg [10:0] mag;
    
    // Integer for reset loop
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_cnt <= 0;
            y_cnt <= 0;
            out_pixel <= 0;
            out_valid <= 0;
            
            // Reset window registers
            pix0 <= 0; pix1 <= 0; pix2 <= 0;
            pix3 <= 0; pix4 <= 0; pix5 <= 0;
            pix6 <= 0; pix7 <= 0; pix8 <= 0;

            // *** FIX: Reset line buffers to 0 ***
            for (i = 0; i < IMG_WIDTH; i = i + 1) begin
                linebuf1[i] <= 8'h00;
                linebuf2[i] <= 8'h00;
            end

        end else if (in_valid) begin
            // --- 1. Update Line Buffers ---
            linebuf2[x_cnt] <= linebuf1[x_cnt];
            linebuf1[x_cnt] <= gray;

            // --- 2. Update 3x3 Window (Correct Shift Register) ---
            pix8 <= gray;
            pix7 <= pix8;
            pix6 <= pix7;
            
            pix5 <= linebuf1[x_cnt];
            pix4 <= pix5;
            pix3 <= pix4;

            pix2 <= linebuf2[x_cnt];
            pix1 <= pix2;
            pix0 <= pix1;

            // --- 3. Sobel Calculation ---
            // Gx = (p2 + 2*p5 + p8) - (p0 + 2*p3 + p6)
            gx <= (pix2 + (pix5 << 1) + pix8) - (pix0 + (pix3 << 1) + pix6);
            // Gy = (p6 + 2*p7 + p8) - (p0 + 2*p1 + p2)
            gy <= (pix6 + (pix7 << 1) + pix8) - (pix0 + (pix1 << 1) + pix2);

            // Magnitude (L1 norm: |Gx| + |Gy|)
            mag <= (gx < 0 ? -gx : gx) + (gy < 0 ? -gy : gy);
            
            // Clamp magnitude to 8-bit (0-255)
            if (mag > 255) begin
                out_pixel <= {24'hFFFFFF}; // {255, 255, 255}
            end else begin
                out_pixel <= {mag[7:0], mag[7:0], mag[7:0]};
            end

            // --- 4. Valid Output Logic ---
            // Output is valid only after the 3x3 window is full
            if (y_cnt >= 2 && x_cnt >= 2) begin
                out_valid <= 1'b1;
            end else begin
                out_valid <= 1'b0;
            end

            // --- 5. Counter Update ---
            if (x_cnt == IMG_WIDTH-1) begin
                x_cnt <= 0;
                y_cnt <= y_cnt + 1;
            end else begin
                x_cnt <= x_cnt + 1;
            end
            
        end else begin
            // If input is not valid, output is not valid
            out_valid <= 0;
        end
    end
endmodule