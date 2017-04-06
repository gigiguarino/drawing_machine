`define min_width  100000
`define max_width  200000
`define period    2000000
module servo_driver(
        input clk,
        input [31:0] width,
        output reg pwm
    );
    reg [31:0] count;
    reg [31:0] safe_width;
 
    always @* begin
        safe_width = width;
        if (width > `max_width)
            safe_width = `max_width;
        if (width < `min_width)
            safe_width = `min_width;
    end
 
    always @(posedge clk) begin
        if (count == `period)
            count <= 0;
        else
            count <= count + 1;
 
        if (count < safe_width)
            pwm <= 1;
        else
            pwm <= 0;
 
    end
endmodule