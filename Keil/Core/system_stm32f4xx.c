/**
  ******************************************************************************
  * @file    system_stm32f4xx.c
  * @brief   最小的系统初始化文件（替代 CubeMX / HAL 的同名文件）
  *
  * 只有两件事：使能 FPU、提供 SystemCoreClock 与 SystemCoreClockUpdate()。
  * 时钟树本身在 bsp_clock_init() 里配置，不在这里做。
  *
  * 注意：如果你的 Keil 工程里 RTE 已经自动带入了官方的 system_stm32f4xx.c，
  *       请把本文件从工程中移除，否则会报重复定义。
  ******************************************************************************
  */
#include "stm32f4xx.h"

uint32_t SystemCoreClock = 16000000u;   /* 复位后默认 HSI 16 MHz，时钟配置后由 bsp 更新 */

const uint8_t AHBPrescTable[16] = {0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 6, 7, 8, 9};
const uint8_t APBPrescTable[8]  = {0, 0, 0, 0, 1, 2, 3, 4};

void SystemInit(void)
{
    /* 使能 CP10/CP11，允许访问 FPU（Cortex-M4F 上电默认关闭） */
    SCB->CPACR |= (0xFu << 20);
    __DSB();
    __ISB();
}

void SystemCoreClockUpdate(void)
{
    uint32_t cfgr = RCC->CFGR;
    uint32_t pllcfgr = RCC->PLLCFGR;

    uint32_t pllM = (pllcfgr >> RCC_PLLCFGR_PLLM_Pos) & 0x3Fu;
    uint32_t pllN = (pllcfgr >> RCC_PLLCFGR_PLLN_Pos) & 0x1FFu;
    uint32_t pllP = (pllcfgr >> RCC_PLLCFGR_PLLP_Pos) & 0x3u;
    uint32_t sysclk;

    pllP = (pllP == 0u) ? 2u : (pllP == 1u) ? 4u : (pllP == 2u) ? 6u : 8u;

    switch (cfgr & RCC_CFGR_SWS)
    {
        case RCC_CFGR_SWS_HSE: sysclk = 8000000u; break;
        case RCC_CFGR_SWS_PLL:
            sysclk = (8000000u / pllM) * pllN / pllP;
            break;
        default:               sysclk = 16000000u; break;
    }

    SystemCoreClock = sysclk;
}
