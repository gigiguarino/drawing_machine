#ifndef __TIMER_H__
#define __TIMER_H__

#include <stdint.h>

#include "mss_timer.h"

#define HW_CLOCK_HZ 100000000
#define MS_PER_SEC  1000

uint8_t timer_flag;
uint32_t ms_to_count(uint32_t ms);
void wait(uint32_t ms);
void timer(uint32_t ms);
void Timer1_IRQHandler( void );

#endif
