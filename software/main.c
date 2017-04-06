#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

#include "CMSIS/a2fxxxm3.h"
//#include // core??? (NVIC)


#include "motor.h"
#include "servo.h"
#include "xy_grid.h"

#define X_INIT 0
#define Y_INIT 0
#define X_MOTOR ((motor_t*) (FPGA_FABRIC_BASE + 0x0))
#define Y_MOTOR ((motor_t*) (FPGA_FABRIC_BASE + 0x4))
#define SERVO ((servo_t*)(FPGA_FABRIC_BASE + 0x100))


// TODO ENCAPSULATE
uint8_t motor_flag;
void wait_for_motor(){
	while(motor_flag){
		//asm("wfi");
	}
}

// FABINT triggers every time a motor finishes running
__attribute__ ((interrupt)) void Fabric_IRQHandler( void )
{
	int32_t x_cnt;
	int32_t y_cnt;

	x_cnt = X_MOTOR->cnt;
	y_cnt = Y_MOTOR->cnt;

	printf("FABINT!\n\r");
    printf("x_cnt: %ld\ty_cnt: %ld\n\r\n\r", x_cnt, y_cnt);

    if(!(x_cnt || y_cnt)){
    	motor_flag = 0;
    }
    NVIC_ClearPendingIRQ( Fabric_IRQn );
}

void move_square_dots(xy_grid_t* xy_grid, int32_t size) {
	move_rel(xy_grid, 0, size);
	wait_for_motor();
	dot(xy_grid);
	move_rel(xy_grid, size, 0);
	wait_for_motor();
	dot(xy_grid);
	move_rel(xy_grid, 0, -size);
	wait_for_motor();
	dot(xy_grid);
	move_rel(xy_grid, -size, 0);
	wait_for_motor();
	dot(xy_grid);
}

void move_test(xy_grid_t* xy_grid) {
	move_rel(xy_grid, 0, 50);    // 0,   50
	wait_for_motor();
	move_abs(xy_grid, 25, 25);   // 25,  25
	wait_for_motor();
	move_rel(xy_grid, 25, 25);   // 50,  50
	wait_for_motor();
	move_rel(xy_grid, -10, -20); // 40,  30
	wait_for_motor();
	move_abs(xy_grid, 0, 0);     // 0,   0
	wait_for_motor();
}

int main(){
    xy_grid_t xy_grid;

    // Initialize timer
	MSS_TIM1_init(MSS_TIMER_ONE_SHOT_MODE);
	MSS_TIM1_enable_irq();

    // Initialize grid
    init_xy_grid(&xy_grid, X_INIT, Y_INIT, X_MOTOR, Y_MOTOR, SERVO);

    // Enable FABINT
    NVIC_EnableIRQ(Fabric_IRQn);

    while(1){
    	move_square_dots(&xy_grid, 100);
    	//move_test(&xy_grid);
    }

    return 0;
}
