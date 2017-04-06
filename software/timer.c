#include "timer.h"

uint32_t ms_to_count(uint32_t ms){
	return HW_CLOCK_HZ / MS_PER_SEC * ms;
}

void timer(uint32_t ms){
	timer_flag = 1;
	MSS_TIM1_load_immediate(ms_to_count(ms));
	MSS_TIM1_start();
}

void Timer1_IRQHandler( void ){
	timer_flag = 0;
	MSS_TIM1_start();
	MSS_TIM1_clear_irq();
}

void wait(uint32_t ms){
	timer(ms);
	while(timer_flag){
		//asm("wfi");
	}
}
