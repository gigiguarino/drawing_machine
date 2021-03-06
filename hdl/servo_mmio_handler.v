module servo_mmio_handler(
		/*** APB3 BUS INTERFACE ***/
		input PCLK,               // clock
		input PRESERN,            // system reset
		input PSEL,               // peripheral select
		input PENABLE,            // distinguishes access phase
		output wire PREADY,       // peripheral ready signal
		output wire PSLVERR,      // error signal
		input PWRITE,             // distinguishes read and write cycles
		input [31:0] PADDR,       // I/O address
		input wire [31:0] PWDATA, // data from processor to I/O device (32 bits)
		output reg [31:0] PRDATA, // data to processor from I/O device (32-bits)

		/*** I/O PORTS DECLARATION ***/	
		output reg [31:0] WIDTH
	); 

	assign PSLVERR = 0;
	assign PREADY  = 1;

	wire write = PWRITE && PSEL && PENABLE;
	
	always @(posedge PCLK)
	begin
		PRDATA <= WIDTH;
	end

	always @(posedge PCLK)
	begin
		if(!PRESERN)
			WIDTH <= 32'd240000;
		else if(write)
			WIDTH <= PWDATA[31:0];
		else
			WIDTH <= WIDTH;
	end
endmodule