/**
  ******************************************************************************
  * @file    app_known.h
  * @brief   已知模型电路的传递函数与开环幅度控制
  *
  * H(s) = 5 / (1e-8·s² + 3e-4·s + 1)
  *      → K = 5，ωn = 1e4 rad/s，Q = 1/3（过阻尼，实极点 −3819.7 / −26180.3）
  ******************************************************************************
  */
#ifndef APP_KNOWN_H
#define APP_KNOWN_H

#ifdef __cplusplus
extern "C" {
#endif

/* 已知模型的幅频特性 |H(j2πf)| */
float KNOWN_GainMag(float f_hz);

/* 已知模型的相频特性，单位度 */
float KNOWN_GainPhaseDeg(float f_hz);

/**
  * @brief  开环反算激励幅度：题目要求输出端无反馈，只能"预先算好"输入
  * @param  f_hz      工作频率
  * @param  vout_vpp  目标输出峰峰值（1.0~2.0 V）
  * @param  kcal      1 kHz 单点校准系数 = 实测增益 / 理论增益，标称 1.0
  * @retval 需要的激励峰峰值（V）
  */
float KNOWN_VinForVout(float f_hz, float vout_vpp, float kcal);

#ifdef __cplusplus
}
#endif

#endif /* APP_KNOWN_H */
