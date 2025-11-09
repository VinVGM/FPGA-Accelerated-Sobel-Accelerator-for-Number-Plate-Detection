// File: tb_sobel_accel.v
`timescale 1ns / 1ps

module tb_sobel_accel;

    // Match parameters in the DUT
    localparam IMG_WIDTH  = 1000;
    localparam IMG_HEIGHT = 467;
    localparam IMG_SIZE   = IMG_WIDTH * IMG_HEIGHT;

    // --- Clock and Reset ---
    reg clk;
    reg rst_n;

    // --- DUT Wires ---
    wire [23:0] in_pixel;
    wire        in_valid;
    wire [23:0] out_pixel;
    wire        out_valid;

    initial begin
        $dumpfile("waveform.vcd"); // The name of the output waveform file
        $dumpvars(0, tb_sobel_accel); // Dump all signals in this module and below
    end

    // --- Testbench Internals ---
    reg  [23:0] image_mem [0:IMG_SIZE-1]; // Memory to hold the input image
    integer     pixel_idx;
    integer     out_file_handle;

    // Instantiate the Device Under Test (DUT)
    sobel_accel #(
        .IMG_WIDTH(IMG_WIDTH),
        .IMG_HEIGHT(IMG_HEIGHT)
    ) DUT (
        .clk(clk),
        .rst_n(rst_n),
        .in_pixel(in_pixel),
        .in_valid(in_valid),
        .out_pixel(out_pixel),
        .out_valid(out_valid)
    );
    
    // Assign streaming inputs based on pixel index
    assign in_pixel = image_mem[pixel_idx];
    // Input is valid as long as we are within the image bounds
    assign in_valid = (pixel_idx < IMG_SIZE); 

    // Clock generator
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 10ns period
    end

    // Main simulation sequence
    initial begin
        $display("--- Simulation Started ---");
        
        // 1. Load image data from hex file
        $readmemh("image.hex", image_mem);
        $display("Input image 'image.hex' loaded.");

        // 2. Open output file
        out_file_handle = $fopen("output.hex", "w");
        if (out_file_handle == 0) begin
            $display("ERROR: Could not open output.hex for writing.");
            $finish;
        end

        // 3. Reset the DUT
        rst_n = 1'b0;
        pixel_idx = 0;
        repeat(2) @(posedge clk);
        rst_n = 1'b1;
        @(posedge clk);
        $display("Reset released. Streaming pixels...");

        // 4. Stream pixels
        while (pixel_idx < IMG_SIZE) begin
            @(posedge clk);
            pixel_idx = pixel_idx + 1;
        end
        
        // 5. Wait for a few more clocks for pipeline to empty
        // (though this design is single-clock)
        repeat(10) @(posedge clk);

        // 6. Clean up
        $fclose(out_file_handle);
        $display("--- Simulation Finished ---");
        $display("Output written to 'output.hex'");
        $finish;
    end
    
    // Output writer
    always @(posedge clk) begin
        if (out_valid) begin
            // Write only the Red channel (since all are R=G=B=Magnitude)
            $fdisplay(out_file_handle, "%h", out_pixel[23:16]);
        end
    end

endmodule