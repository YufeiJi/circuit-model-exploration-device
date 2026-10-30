/**
  ******************************************************************************
  * @file    app_dds.h
  * @brief   32 位相位累加 DDS：DAC + DMA 双缓冲，TIM6 触发，fs = 1 MSPS
  ******************************************************************************
  */
#ifndef APP_DDS_H
#define APP_DDS_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

#define DDS_FS_HZ        1000000u            /* DAC 更新率，与 TIM6 一致 */
#define DDS_TAB_LEN      1024u               /* 正弦表点数（2 的幂） */
#define DDS_BUF_LEN      (DDS_TAB_LEN * 2u)  /* DMA 双缓冲 */

#define DDS_DAC_FULL_VPP 2.70f               /* DAC 可用满幅峰峰值（实测标定） */

void  DDS_Init(void);
void  DDS_SetFreq(float f_hz);
void  DDS_SetAmpVpp(float vpp);
void  DDS_SetAmpWord(uint16_t amp);
float DDS_GetFreq(void);
float DDS_GetAmpVpp(void);
uint16_t DDS_GetAmpWord(void);

/* 中断服务函数（向量表里已固定，必须有原型，否则 -Wmissing-prototypes 报警） */
void DMA1_Stream5_IRQHandler(void);

#ifdef __cplusplus
}
#endif

#endif /* APP_DDS_H */
