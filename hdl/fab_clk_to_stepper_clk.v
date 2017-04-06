module fab_clk_to_stepper_clk(
        input PCLK,
        input PRESERN,
        output clk_out
    );
    reg [31:0] cnt;

    assign clk_out = cnt[18];
    
    always @(posedge PCLK) begin
        if(~PRESERN || clk_out) begin
            cnt = 32'b0;
        end
        else begin
            cnt = cnt + 1;
        end
    end
    

endmodule