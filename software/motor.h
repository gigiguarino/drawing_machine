#ifndef __MOTOR_H__
#define __MOTOR_H__

#include <stdint.h>

typedef struct {
    volatile int32_t cnt;
} motor_t;

#endif
