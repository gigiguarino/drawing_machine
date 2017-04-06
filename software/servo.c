#include "servo.h"

void set_angle_abs(servo_t* servo, uint16_t theta){
    uint32_t d_theta;

    // Translate absolute angle to relative angle
    d_theta = ((int32_t) theta) - ((int32_t) servo->theta);
    set_angle_rel(servo, d_theta);
}

void set_angle_rel(servo_t* servo, int16_t d_theta){

    // Update software record of angle
    servo->theta += d_theta;

    // Software guard servo
    assert(!(servo->theta < THETA_MIN));
    assert(!(servo->theta > THETA_MAX));

    // Move servo
    servo->width = WIDTH_MIN + (servo->theta * (WIDTH_MAX - WIDTH_MIN)) / THETA_MAX;
}
