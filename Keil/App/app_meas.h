/**
  ******************************************************************************
  * @file    app_meas.h
  * @brief   单频 DFT 幅相测量：ADC + DMA 采集，Hann 窗抑制泄漏
  ******************************************************************************
  */
#ifndef APP_MEAS_H
#define APP_MEAS_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

#define MEAS_FS_HZ     500000u   /* ADC 采样率，与 TIM3 一致 */
#define MEAS_N         4096u     /* 每次采集点数，窗口 8.192 ms */
#define MEAS_VREF      3.30f     /* ADC 参考电压 */
#define MEAS_ATTEN     1.0f      /* 前端衰减倍数：×1 档填 1.0，×4 档填 4.0 */

void MEAS_Init(void);

/**
  * @brief  在频率 f 处测量被测电路的输出幅相
  * @param  f_hz       激励频率
  * @param  amp_vpp    返回峰峰值（V）
  * @param  phase_deg  返回相位（°，以采集窗口起点为参考）
  * @retval 0 成功，-1 采集超时
  */
int MEAS_Capture(float f_hz, float *amp_vpp, float *phase_deg);

int MEAS_CaptureRaw(uint16_t *buf);

#ifdef __cplusplus
}
#endif

#endif /* APP_MEAS_H */
