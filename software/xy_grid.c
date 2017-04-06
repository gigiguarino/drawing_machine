#include "xy_grid.h"

void init_xy_grid(xy_grid_t* xy_grid, uint32_t x, uint32_t y, motor_t* x_motor, motor_t* y_motor, servo_t* servo){
    xy_grid->x = x;
    xy_grid->y = y;
    xy_grid->x_motor = x_motor;
    xy_grid->y_motor = y_motor;
    xy_grid->servo   = servo;
}

void move_abs(xy_grid_t* xy_grid, uint32_t x, uint32_t y){
    int32_t dx;
    int32_t dy;
    
    // Translate absolute position to relative position
    dx = ((int32_t) x) - ((int32_t) xy_grid->x);
    dy = ((int32_t) y) - ((int32_t) xy_grid->y);
    move_rel(xy_grid, dx, dy);
}

void move_rel(xy_grid_t* xy_grid, int32_t dx, int32_t dy){

    // Update software record of position
    xy_grid->x += dx;
    xy_grid->y += dy;
    
    // Software guard motors
    assert(!(xy_grid->x < X_MIN));
    assert(!(xy_grid->x > X_MAX));
    assert(!(xy_grid->y < Y_MIN));
    assert(!(xy_grid->y > Y_MAX));
    
    // Move motors
    if(dx){
    	motor_flag = 1;
        xy_grid->x_motor->cnt = dx;
    }
    if(dy){
    	motor_flag = 1;
        xy_grid->y_motor->cnt = dy;
    }
}

void up(xy_grid_t* xy_grid){
	// TODO change to rel (also down)
	set_angle_abs(xy_grid->servo, 45);
	wait(SERVO_MOVE_MS);
}
void down(xy_grid_t* xy_grid){
	set_angle_abs(xy_grid->servo, 90);
	wait(SERVO_MOVE_MS);

}
void dot(xy_grid_t* xy_grid){
	up(xy_grid);
	down(xy_grid);
}
