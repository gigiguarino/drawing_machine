#ifndef __XY_GRID_H__
#define __XY_GRID_H__

#include <assert.h>
#include <stdint.h>

#include "motor.h"
#include "servo.h"
#include "timer.h"

extern uint8_t motor_flag;

#define X_MIN 0
#define X_MAX 300
#define Y_MIN 0
#define Y_MAX 300

typedef struct {
    uint32_t x;
    uint32_t y;
    motor_t* x_motor;
    motor_t* y_motor;
    servo_t* servo;
} xy_grid_t;

void init_xy_grid(xy_grid_t* xy_grid, uint32_t x, uint32_t y, motor_t* x_motor, motor_t* y_motor, servo_t* servo);
void move_abs(xy_grid_t* xy_grid, uint32_t x, uint32_t y);
void move_rel(xy_grid_t* xy_grid, int32_t dx, int32_t dy);

void up(xy_grid_t* xy_grid);
void down(xy_grid_t* xy_grid);
void dot(xy_grid_t* xy_grid);

#endif
