/**
  ******************************************************************************
  * @file    bsp.h
  * @brief   板级驱动：时钟、延时、串口、定时器、DAC+DMA、ADC+DMA
  *
  * 全部直接操作寄存器，不依赖 HAL / CubeMX，只依赖 CMSIS（stm32f4xx.h）。
  ******************************************************************************
  */
#ifndef BSP_H
#define BSP_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

/* ---- 时钟：HSE 8 MHz → SYSCLK 168 MHz ---- */
#define SYSCLK_HZ     168000000u
#define PCLK1_HZ       42000000u   /* APB1，定时器时钟 84 MHz */
#define PCLK2_HZ       84000000u   /* APB2，ADC 时钟 = PCLK2/4 = 21 MHz */
#define TIM_CLK_HZ     84000000u   /* TIM2~7、12~14 的计数时钟 */

extern volatile uint32_t g_ms_tick;

void bsp_clock_init(void);          /* PLL 168 MHz + SysTick 1 ms */
void delay_ms(uint32_t ms);
void delay_us(uint32_t us);

void uart2_init(uint32_t baud);     /* PA2/PA3，AF7 */
int  uart2_getc(uint8_t *c, uint32_t timeout_ms);   /* 0 成功，-1 超时 */

void tim6_start(void);              /* 1 MSPS 更新，TRGO 给 DAC */
void tim3_start(void);              /* 500 kSPS 更新，TRGO 给 ADC */

void dac_dma_start(uint16_t *buf, uint32_t len);    /* PA4，DMA1_Stream5_Ch7，循环 */
void adc_dma_init(uint16_t *buf, uint32_t len);     /* PA0，DMA2_Stream0_Ch0，普通模式 */
void adc_dma_arm(void);             /* 每次采集前重新武装 */
void adc_dma_stop(void);

extern volatile uint8_t g_adc_done; /* 采满 N 点后由 DMA 中断置 1 */

/* 中断服务函数（向量表里已固定，必须有原型） */
void SysTick_Handler(void);
void DMA2_Stream0_IRQHandler(void);

#ifdef __cplusplus
}
#endif

#endif /* BSP_H */
