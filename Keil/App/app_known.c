/**
  ******************************************************************************
  * @file    app_known.c
  * @brief   已知模型电路 H(s) 的数值计算与开环幅度反算
  *
  * 注意：这里用 double 计算，因为 1e-8·ω² 在 10 kHz 时已达 4e-2，
  *       float 的 7 位有效数字在 100 kHz 附近仍够用，但为了与报告数值逐位对齐，统一用 double。
  ******************************************************************************
  */
#include "app_known.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* 分母系数：1e-8·s² + 3e-4·s + 1 */
#define A2  1.0e-8
#define A1  3.0e-4
#define K0  5.0

float KNOWN_GainMag(float f_hz)
{
    double w  = 2.0 * M_PI * (double)f_hz;
    double w2 = w * w;

    double re = 1.0 - A2 * w2;   /* 实部 */
    double im = A1 * w;          /* 虚部 */

    double den = sqrt(re * re + im * im);
    if (den < 1e-12) {
        return 0.0f;
    }
    return (float)(K0 / den);
}

float KNOWN_GainPhaseDeg(float f_hz)
{
    double w  = 2.0 * M_PI * (double)f_hz;
    double re = 1.0 - A2 * w * w;
    double im = A1 * w;

    /* H = K / (re + j·im) → 相位 = −atan2(im, re) */
    double ph = -atan2(im, re) * 180.0 / M_PI;
    return (float)ph;
}

float KNOWN_VinForVout(float f_hz, float vout_vpp, float kcal)
{
    float g = KNOWN_GainMag(f_hz) * kcal;
    if (g < 1e-6f) {
        return 0.0f;
    }
    return vout_vpp / g;
}
