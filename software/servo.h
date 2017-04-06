#ifndef __SERVO_H__
#define __SERVO_H__

#include <stdint.h>
#include <assert.h>

#define THETA_MIN 0
#define THETA_MAX 90
#define WIDTH_MIN 100000
#define WIDTH_MAX 200000
#define SERVO_MOVE_MS 1000

typedef struct {
	uint16_t theta;
    volatile uint32_t width;
} servo_t;

void set_angle_abs(servo_t* servo, uint16_t theta);
void set_angle_rel(servo_t* servo, int16_t d_theta);

#endif
