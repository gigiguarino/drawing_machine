module testbench;

reg clk;
reg reset;
reg sel;
reg enable;
reg ready = 1;
reg error = 0;
reg pwrite;
reg [31:0] paddr;
reg [31:0] pwdata;
reg [31:0] prdata;
reg [31:0] x_counter_in, x_counter_out;
reg x_dir_in, x_dir_out;
reg [31:0] y_counter_in, y_counter_out;
reg y_dir_in, y_dir_out;
reg fabint;


motor_mmio_handler m (
  clk,
  reset,
  sel,
  enable,
  ready,
  error,
  pwrite,
  paddr,
  pwdata,
  prdata,
  x_counter_in,
  x_dir_in,
  y_counter_in,
  y_dir_in,
  x_counter_out,
  x_dir_out,
  y_counter_out,
  y_dir_out,
  fabint
);

motor_driver mdx(
  clk,
  reset,
  x_counter_out,
  x_dir_out,
  hb_statex1,
  hb_statex2,
  x_counter_in,
  x_dir_in
);

motor_driver mdy(
  clk,
  reset,
  y_counter_out,
  y_dir_out,
  hb_statey1,
  hb_statey2,
  y_counter_in,
  y_dir_in
);

always begin
  #5
  clk = ~clk;
  print_everything;
end

task print_everything;
  $display("----------------------------");
  $display("INPUTS OF MMIO:"); 
  $display("----------------------------");
  $display("x_counter_in: %d", x_counter_in);
  $display("y_counter_in: %d", y_counter_in);
  $display("x_dir_in: %b", x_dir_in);
  $display("y_dir_in: %b", y_dir_in);
  $display("----------------------------");
  $display("OUTPUTS OF MMIO");
  $display("----------------------------");
  $display("x_counter_out: %d", x_counter_out);
  $display("y_counter_out: %d", y_counter_out);
  $display("x_dir_out: %b", x_dir_out);
  $display("y_dir_out: %b", y_dir_out);
  $display("fabint: %b", fabint);
  $display("----------------------------");
  $display("INSIDE MODULE");
  $display("----------------------------");
  $display("x_zero: %b", m.x_zero);
  $display("y_zero: %b", m.y_zero);
  $display("last_x_zero: %b", m.last_x_zero);
  $display("last_y_zero: %b", m.last_y_zero);
  $display("x_done: %b", m.x_done);
  $display("y_done: %b", m.y_done);
endtask



initial begin
  reset = 0;
  clk = 0;
  @(negedge clk);
  reset = 1;
  
  pwdata = 5;
  paddr = 4;
  pwrite = 1;
  psel = 1;
  penable = 1;

  @(negedge clk);

  psel = 0;
  penable = 0;

  @(posedge fabint);

  paddr = 0;
  psel = 1;
  penable = 1;

  @(negedge clk);

  psel = 0;
  penable = 0;

  @(posedge fabint);

  paddr = 4;
  psel = 1;
  penable = 1;

  @(negedge clk);

  psel = 0;
  penable = 0;

  
  $finish;
end


endmodule
