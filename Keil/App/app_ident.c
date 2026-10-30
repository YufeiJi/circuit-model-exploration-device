/**
  ******************************************************************************
  * @file    app_ident.c
  * @brief   四模型复频域（对数幅值域）加权最小二乘拟合 + 分类
  *
  * 算法结构：
  *   1) 26 点对数扫频，得到 (f_i, |H_i|)
  *   2) 对每种模型，在对数网格 (f0 × Q) 上粗搜，残差定义
  *        r_i = ln|H_i| − ln h_model(f_i; f0, Q)
  *        err = Σ(r_i − mean(r))²        ← 增益 K 已被解析消去
  *   3) 在最优格点附近做 3 轮 7×7 局部细化，跨度每轮减半
  *   4) 取 err 最小的模型，K = exp(mean(r))
  ******************************************************************************
  */
#include "app_ident.h"
#include "app_dds.h"
#include "app_meas.h"
#include "bsp.h"
#include <math.h>
#include <stdio.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define GRID_NF   120      /* f0 网格数（对数分布 5.0k~50.3k） */
#define GRID_NQ   80       /* Q  网格数（对数分布 0.01~1.0）   */
#define F0_MIN    5000.0f
#define F0_MAX    50300.0f
#define Q_MIN     0.010f
#define Q_MAX     1.000f

/* --------------------------------------------------- 归一化幅频（K=1） */
static float model_norm(ident_type_t t, float u, float q)
{
    float u2 = u * u;
    float t1 = 1.0f - u2;
    float t2 = u / q;
    float d  = t1 * t1 + t2 * t2;

    if (d < 1e-24f) {
        return 1e-12f;
    }
    float root = sqrtf(d);

    switch (t) {
        case IDENT_LP: return 1.0f / root;
        case IDENT_HP: return u2 / root;
        case IDENT_BP: return t2 / root;
        case IDENT_BR: return fabsf(t1) / root;
        case IDENT_NONE: return 0.0f;
    }
}

/* ------------------------------------------- 给定 (f0,Q) 的残差与增益 */
static float eval_fit(ident_type_t t, const float *lf, const float *lm, int n,
                      float f0, float q, float *K_out)
{
    float sum = 0.0f, sum2 = 0.0f;

    for (int i = 0; i < n; i++) {
        float h = model_norm(t, lf[i] / f0, q);
        if (h < 1e-9f) {
            h = 1e-9f;
        }
        float r = lm[i] - logf(h);
        sum  += r;
        sum2 += r * r;
    }

    float c   = sum / (float)n;
    float err = sum2 - sum * c;      /* = Σ(r−c)²，数值上更稳 */

    if (K_out) {
        *K_out = expf(c);
    }
    return (err < 0.0f) ? 0.0f : err;
}

/* ------------------------------------------------------ 单模型拟合 */
static float fit_one(ident_type_t t, const float *lf, const float *lm, int n,
                     float *f0_best, float *q_best, float *K_best)
{
    float best_err = 1e30f, bf0 = F0_MIN, bq = 0.5f;

    /* ---- 1) 对数网格粗搜 ---- */
    float rf = powf(F0_MAX / F0_MIN, 1.0f / (float)(GRID_NF - 1));
    float rq = powf(Q_MAX / Q_MIN,  1.0f / (float)(GRID_NQ - 1));

    for (int i = 0; i < GRID_NF; i++) {
        float f0 = F0_MIN * powf(rf, (float)i);
        for (int j = 0; j < GRID_NQ; j++) {
            float q   = Q_MIN * powf(rq, (float)j);
            float err = eval_fit(t, lf, lm, n, f0, q, 0);
            if (err < best_err) {
                best_err = err; bf0 = f0; bq = q;
            }
        }
    }

    /* ---- 2) 三轮局部细化，跨度每轮减半 ---- */
    float sf = 0.03f * bf0;      /* 初始跨度 ±3% */
    float sq = 0.15f * bq;

    for (int round = 0; round < 3; round++) {
        float cf0 = bf0, cq = bq;

        for (int i = -3; i <= 3; i++) {
            float f0 = cf0 + sf * (float)i / 3.0f;
            if (f0 < F0_MIN * 0.5f || f0 > F0_MAX * 1.5f) continue;

            for (int j = -3; j <= 3; j++) {
                float q = cq + sq * (float)j / 3.0f;
                if (q < 0.005f || q > 2.0f) continue;

                float err = eval_fit(t, lf, lm, n, f0, q, 0);
                if (err < best_err) {
                    best_err = err; bf0 = f0; bq = q;
                }
            }
        }
        sf *= 0.5f;
        sq *= 0.5f;
    }

    *f0_best = bf0;
    *q_best  = bq;
    eval_fit(t, lf, lm, n, bf0, bq, K_best);   /* 回代求 K */
    return best_err;
}

/* ------------------------------------------------------------ 对外接口 */
int IDENT_Run(const float *f_hz, const float *mag, int n, ident_result_t *out)
{
    if (!f_hz || !mag || !out || n < 6) {
        return -1;
    }

    float lf[IDENT_NPTS], lm[IDENT_NPTS];
    int   m = 0;

    for (int i = 0; i < n; i++) {
        if (mag[i] > 1e-6f) {
            lf[m] = f_hz[i];
            lm[m] = logf(mag[i]);
            m++;
        }
    }
    if (m < 6) {
        return -1;
    }

    ident_result_t best;
    best.type = IDENT_NONE;
    best.err  = 1e30f;

    for (int t = IDENT_LP; t <= IDENT_BR; t++) {
        float f0, q, K;
        float err = fit_one((ident_type_t)t, lf, lm, m, &f0, &q, &K);

        if (err < best.err) {
            best.type  = (ident_type_t)t;
            best.f0_hz = f0;
            best.Q     = q;
            best.K     = K;
            best.err   = err;
        }
    }

    *out = best;
    return 0;
}

int IDENT_Learn(ident_result_t *out, float *freq_log, float *mag_log)
{
    float f[IDENT_NPTS], mg[IDENT_NPTS];
    float vin = DDS_GetAmpVpp();

    if (vin < 0.05f) {
        return -1;                       /* 激励太小，信噪比不够 */
    }

    for (int i = 0; i < IDENT_NPTS; i++) {
        float t  = (float)i / (float)(IDENT_NPTS - 1);
        float fh = IDENT_F_LO * powf(IDENT_F_HI / IDENT_F_LO, t);

        DDS_SetFreq(fh);

        /* 稳定时间：max(20/f, 5 ms)，低频段多等几个周期 */
        float settle = 20.0f / fh * 1000.0f;
        if (settle < 5.0f) settle = 5.0f;
        delay_ms((uint32_t)(settle + 0.5f));

        float vpp = 0.0f, ph = 0.0f;
        if (MEAS_Capture(fh, &vpp, &ph) != 0) {
            f[i]  = fh;
            mg[i] = 0.0f;
            continue;
        }

        f[i]  = fh;
        mg[i] = vpp / vin;

        if (freq_log) freq_log[i] = fh;
        if (mag_log)  mag_log[i]  = mg[i];

        printf("  %6.0f Hz  |H| = %8.4f\r\n", (double)fh, (double)mg[i]);
    }

    return IDENT_Run(f, mg, IDENT_NPTS, out);
}

const char *IDENT_TypeName(ident_type_t t)
{
    switch (t) {
        case IDENT_LP: return "Low-pass";
        case IDENT_HP: return "High-pass";
        case IDENT_BP: return "Band-pass";
        case IDENT_BR: return "Band-reject";
        case IDENT_NONE: return "Unknown";
    }
}
