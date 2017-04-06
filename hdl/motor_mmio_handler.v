module motor_mmio_handler(

        /*** APB3 BUS INTERFACE ***/
        input              PCLK,    // clock
        input              PRESERN, // system reset
        input              PSEL,    // peripheral select
        input              PENABLE, // distinguishes access phase
        output wire        PREADY,  // peripheral ready signal
        output wire        PSLVERR, // error signal
        input              PWRITE,  // distinguishes read and write cycles
        input       [31:0] PADDR,   // I/O address
        input       [31:0] PWDATA,  // data from processor to I/O device (32 bits)
        output reg  [31:0] PRDATA,  // data to processor from I/O device (32-bits)

        input [31:0] x_counter_in,
        input        x_dir_in,
        input [31:0] y_counter_in,
        input        y_dir_in,

        output reg  [31:0] x_counter_out,
        output reg         x_dir_out,
        output reg  [31:0] y_counter_out,
        output reg         y_dir_out,

        output wire FABINT
    );
    wire x_zero;
    reg last_x_zero;
    wire y_zero;
    reg last_y_zero;
    wire x_done;
    wire y_done;

    assign x_zero = (x_counter_in == 0);
    assign y_zero = (y_counter_in == 0);

    assign x_done = (x_zero & ~last_x_zero);
    assign y_done = (y_zero & ~last_y_zero);

    assign FABINT = x_done | y_done;

    assign PSLVERR = 0;
    assign PREADY  = 1;
	
    // APB3 write control
    always @(posedge PCLK) begin
        if(!PRESERN) begin
            last_x_zero   <= 1;
            last_y_zero   <= 1;
            x_dir_out     <= 1;
            y_dir_out     <= 1;
            x_counter_out <= 0;
            y_counter_out <= 0;
        end
        else begin
            if(PSEL & PENABLE) begin
                // On a write, convert signed count to dir and count
                if(PWRITE) begin
                    if(~PADDR[2]) begin
                        x_dir_out     <= ~PWDATA[31];
                        x_counter_out <= (~PWDATA[31])? PWDATA : ~PWDATA + 1;
                    end
                    else begin
                        y_dir_out     <= ~PWDATA[31];
                        y_counter_out <= (~PWDATA[31])? PWDATA : ~PWDATA + 1;
                    end
                end
                // On a read, provide a signed count
                else begin
                    if(~PADDR[2]) begin
                        PRDATA <= (x_dir_in)? x_counter_in : ~x_counter_in + 1;
                    end
                    else begin
                        PRDATA <= (y_dir_in)? y_counter_in : ~y_counter_in + 1;
                    end
                end
            end
            else begin
                if(x_done) begin
                    x_dir_out     <= 0;
                    x_counter_out <= 0;
                end
                if(y_done) begin
                    y_dir_out     <= 0;
                    y_counter_out <= 0;
                end
            end
        end
        last_x_zero <= x_zero;
        last_y_zero <= y_zero;
    end
endmodule
