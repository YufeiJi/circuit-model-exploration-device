/**
  ******************************************************************************
  * @file    app_dds.c
  * @brief   DDS 正弦合成：1024 点 Q15 表 + 线性插值 + DMA 双缓冲
  *
  * 数据流：
  *   TIM6(1 MHz TRGO) → DAC1_CH1 → DMA1_Stream5 循环搬运 s_buf[2048]
  *   每搬完一半进 DMA 中断，把刚空出来的那一半重新算好
  ******************************************************************************
  */
#include "stm32f4xx.h"          /* 中断里要直接操作 DMA1 寄存器 */
#include "app_dds.h"
#include "bsp.h"
#include <math.h>

#define TWO_PI 6.283185307179586f

static int16_t  s_tab[DDS_TAB_LEN];
static uint16_t s_buf[DDS_BUF_LEN];

static volatile uint32_t s_phase = 0;
static volatile uint32_t s_dphi  = 0;
static volatile uint16_t s_amp   = 2047;
static volatile float    s_freq  = 1000.0f;
static volatile float    s_vpp   = 2.70f;

static void tab_build(void)
{
    for (uint32_t i = 0; i < DDS_TAB_LEN; i++)
    {
        float v = sinf(TWO_PI * (float)i / (float)DDS_TAB_LEN);
        s_tab[i] = (int16_t)(v * 32767.0f);
    }
}

/* 生成 n 个采样点，写入 dst */
static void dds_fill(uint16_t *dst, uint32_t n)
{
    uint32_t phase = s_phase;
    uint32_t dphi  = s_dphi;
    int32_t  amp   = (int32_t)s_amp;

    for (uint32_t i = 0; i < n; i++)
    {
        phase += dphi;

        uint32_t idx  = phase >> 22;                        /* 高 10 位 → 表地址 */
        int32_t  frac = (int32_t)((phase >> 6) & 0xFFFFu);  /* 次 16 位 → 插值 */

        int32_t a = s_tab[idx];
        int32_t b = s_tab[(idx + 1u) & (DDS_TAB_LEN - 1u)];

        int32_t v    = a + (((b - a) * frac) >> 16);
        int32_t code = 2048 + ((v * amp) >> 15);

        if (code < 0)    code = 0;
        if (code > 4095) code = 4095;

        dst[i] = (uint16_t)code;
    }

    s_phase = phase;
}

void DDS_Init(void)
{
    tab_build();
    s_phase = 0;

    DDS_SetFreq(s_freq);
    DDS_SetAmpVpp(s_vpp);

    dds_fill(&s_buf[0], DDS_TAB_LEN);
    dds_fill(&s_buf[DDS_TAB_LEN], DDS_TAB_LEN);

    dac_dma_start(s_buf, DDS_BUF_LEN);   /* 配好 DMA 与 DAC，但还没有触发 */
    tim6_start();                        /* 触发源启动，开始出波 */
}

void DDS_SetFreq(float f_hz)
{
    if (f_hz < 100.0f)    f_hz = 100.0f;
    if (f_hz > 100000.0f) f_hz = 100000.0f;

    s_freq = f_hz;
    s_dphi = (uint32_t)((double)f_hz / (double)DDS_FS_HZ * 4294967296.0);
}

void DDS_SetAmpWord(uint16_t amp)
{
    if (amp > 2047u) amp = 2047u;
    s_amp = amp;
    s_vpp = (float)amp / 2047.0f * DDS_DAC_FULL_VPP;
}

void DDS_SetAmpVpp(float vpp)
{
    if (vpp < 0.0f) vpp = 0.0f;
    float code = vpp / DDS_DAC_FULL_VPP * 2047.0f;
    if (code > 2047.0f) code = 2047.0f;
    DDS_SetAmpWord((uint16_t)(code + 0.5f));
}

float DDS_GetFreq(void)       { return s_freq; }
float DDS_GetAmpVpp(void)     { return s_vpp;  }
uint16_t DDS_GetAmpWord(void) { return s_amp;  }

/* --------------------------------------------- DMA1 Stream5 中断（DAC） */
/* 注意：Stream5 的 5 个标志位在 HISR 的 bit6~bit11
 *       FEIF5=6、DMEIF5=8、TEIF5=9、HTIF5=10、TCIF5=11
 *       （LISR 只放 Stream0~3，HISR 放 Stream4~7，每流占 6 位） */
void DMA1_Stream5_IRQHandler(void)
{
    uint32_t isr = DMA1->HISR;

    if (isr & (1u << 11))                 /* TCIF5：整块搬完 → 后半段刚播完，重填后半段 */
    {
        DMA1->HIFCR = (1u << 11);
        dds_fill(&s_buf[DDS_TAB_LEN], DDS_TAB_LEN);
    }

    if (isr & (1u << 10))                 /* HTIF5：搬完一半 → 前半段刚播完，重填前半段 */
    {
        DMA1->HIFCR = (1u << 10);
        dds_fill(&s_buf[0], DDS_TAB_LEN);
    }

    if (isr & (1u << 9))                  /* TEIF5：传输错误，清掉避免中断风暴 */
    {
        DMA1->HIFCR = (1u << 9);
    }
}
