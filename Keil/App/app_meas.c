/**
  ******************************************************************************
  * @file    app_meas.c
  * @brief   单频 DFT 幅相提取（寄存器版）
  ******************************************************************************
  */
#include "app_meas.h"
#include "bsp.h"
#include <math.h>
#include <string.h>

#define PI_F 3.14159265358979f

static uint16_t s_adc[MEAS_N];

void MEAS_Init(void)
{
    adc_dma_init(s_adc, MEAS_N);
    tim3_start();                 /* 500 kHz 触发 ADC */
}

int MEAS_CaptureRaw(uint16_t *buf)
{
    adc_dma_arm();

    uint32_t t0 = g_ms_tick;
    while (!g_adc_done)
    {
        if ((g_ms_tick - t0) > 100u)     /* 8.2 ms 正常，100 ms 必超时 */
        {
            adc_dma_stop();
            return -1;
        }
    }

    adc_dma_stop();

    if (buf) memcpy(buf, s_adc, sizeof(s_adc));
    return 0;
}

int MEAS_Capture(float f_hz, float *amp_vpp, float *phase_deg)
{
    if (MEAS_CaptureRaw(0) != 0) return -1;

    /* 1. 去直流 */
    float sum = 0.0f;
    for (uint32_t i = 0; i < MEAS_N; i++) sum += (float)s_adc[i];
    float mean = sum / (float)MEAS_N;

    /* 2. Hann 窗 + 单频 DFT */
    float re = 0.0f, im = 0.0f, wsum = 0.0f;
    float dw = 2.0f * PI_F * f_hz / (float)MEAS_FS_HZ;

    for (uint32_t n = 0; n < MEAS_N; n++)
    {
        float x = (float)s_adc[n] - mean;
        float w = 0.5f - 0.5f * cosf(2.0f * PI_F * (float)n / (float)(MEAS_N - 1u));
        float xw = x * w;
        float arg = dw * (float)n;

        re += xw * cosf(arg);
        im -= xw * sinf(arg);
        wsum += w;
    }

    /* 3. 幅度与相位 */
    float mag = sqrtf(re * re + im * im);
    float peak_v = 2.0f * mag / wsum * (MEAS_VREF / 4095.0f) * MEAS_ATTEN;

    if (amp_vpp)   *amp_vpp   = 2.0f * peak_v;
    if (phase_deg) *phase_deg = atan2f(im, re) * 180.0f / PI_F;

    return 0;
}
