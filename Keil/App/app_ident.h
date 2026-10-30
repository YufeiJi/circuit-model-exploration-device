/**
  ******************************************************************************
  * @file    app_ident.h
  * @brief   未知模型辨识：26 点扫频 + 四种二阶模型加权最小二乘 + 残差最小分类
  *
  * 为什么不用"找峰值判类型"：
  *   由 R∈[1,10]kΩ、L∈[1,10]mH、C∈[10,100]nF 可推得 Q∈[0.01,1]，
  *   Q ≤ 1 时带通根本没有谐振峰，形状判据在原理上就不可靠。
  *   改为把低通/高通/带通/带阻四种模型分别拟合，残差最小的既给类型也给参数。
  ******************************************************************************
  */
#ifndef APP_IDENT_H
#define APP_IDENT_H

#ifdef __cplusplus
extern "C" {
#endif

#define IDENT_NPTS   26          /* 扫频点数 */
#define IDENT_F_LO   200.0f      /* 起始频率 Hz */
#define IDENT_F_HI   100000.0f   /* 终止频率 Hz（f0 上限 50.3 kHz 的一个数量级以上） */

typedef enum {
    IDENT_LP = 0,
    IDENT_HP,
    IDENT_BP,
    IDENT_BR,
    IDENT_NONE
} ident_type_t;

typedef struct {
    ident_type_t type;
    float K;        /* 通带增益 */
    float f0_hz;    /* 特征频率 */
    float Q;        /* 品质因数 */
    float err;      /* 对数域归一化残差（越小越可信） */
} ident_result_t;

/**
  * @brief  对已测得的 (f, |H|) 序列做四模型拟合
  * @param  f_hz  频率数组
  * @param  mag   对应幅值（线性，非 dB）
  * @param  n     点数
  * @param  out   结果
  * @retval 0 成功
  */
int IDENT_Run(const float *f_hz, const float *mag, int n, ident_result_t *out);

/**
  * @brief  自主学习：自动扫频 26 点并拟合，结果同时回填到 freq/mag（可传 NULL）
  * @note   全程约 0.5~0.8 s（含等待稳定），满足题目 2 min 限制
  */
int IDENT_Learn(ident_result_t *out, float *freq_log, float *mag_log);

/* 类型名，用于串口/OLED 显示 */
const char *IDENT_TypeName(ident_type_t t);

#ifdef __cplusplus
}
#endif

#endif /* APP_IDENT_H */
