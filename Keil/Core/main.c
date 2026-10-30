/**
  ******************************************************************************
  * @file    main.c
  * @brief   电路模型探究装置 —— 主程序（STM32F407VET6，纯寄存器，无 HAL/无 CubeMX）
  *
  * 串口命令（USART2，PA2/PA3，115200 8N1）：
  *   ?       帮助
  *   F1000   设定频率 1000 Hz
  *   A2.0    设定激励峰峰值 2.0 V
  *   M       测量当前输出幅相
  *   H       打印当前频率下已知模型的 |H|
  *   K1.002  设定 1 kHz 校准系数
  *   C1.5    开环控制：让已知模型输出达到 1.5 Vpp
  *   L       未知模型自主学习（26 点扫频 + 分类 + 参数）
  ******************************************************************************
  */
#include "stm32f4xx.h"
#include "bsp.h"
#include "app_dds.h"
#include "app_meas.h"
#include "app_known.h"
#include "app_ident.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static float g_kcal = 1.0f;

/* ------------------------------------------------------- printf 重定向 */
int fputc(int ch, FILE *f)
{
    (void)f;
    while (!(USART2->SR & USART_SR_TXE)) { }
    USART2->DR = (uint8_t)ch;
    return ch;
}

/* ------------------------------------------------------------ 命令解析 */
static void cli_exec(char *line)
{
    char cmd = line[0];
    if (cmd >= 'a' && cmd <= 'z') cmd = (char)(cmd - 'a' + 'A');

    float arg = (float)atof(&line[1]);

    switch (cmd)
    {
        case '?':
            printf("\r\nF<f> 设频率 | A<vpp> 设幅度 | M 测量 | H 看 |H|\r\n");
            printf("K<kcal> 校准 | C<vout> 开环控制 | L 未知模型学习\r\n");
            break;

        case 'F':
            DDS_SetFreq(arg);
            printf("f = %.1f Hz\r\n", (double)DDS_GetFreq());
            break;

        case 'A':
            DDS_SetAmpVpp(arg);
            printf("Vin = %.3f Vpp\r\n", (double)DDS_GetAmpVpp());
            break;

        case 'K':
            g_kcal = (arg > 0.2f && arg < 5.0f) ? arg : 1.0f;
            printf("kcal = %.4f\r\n", (double)g_kcal);
            break;

        case 'H': {
            float f0 = DDS_GetFreq();
            printf("|H(%.1f Hz)| = %.4f (%.2f dB)\r\n",
                   (double)f0, (double)KNOWN_GainMag(f0),
                   20.0 * log10((double)KNOWN_GainMag(f0)));
            break;
        }

        case 'M': {
            float vpp = 0.0f, ph = 0.0f;
            if (MEAS_Capture(DDS_GetFreq(), &vpp, &ph) == 0)
                printf("Vout = %.4f Vpp, phase = %.1f deg\r\n", (double)vpp, (double)ph);
            else
                printf("measure timeout\r\n");
            break;
        }

        case 'C': {
            float target = (arg > 0.1f) ? arg : 1.0f;
            float vin = KNOWN_VinForVout(DDS_GetFreq(), target, g_kcal);

            DDS_SetAmpVpp(vin);
            delay_ms(10);

            float vpp = 0.0f, ph = 0.0f;
            if (MEAS_Capture(DDS_GetFreq(), &vpp, &ph) == 0)
            {
                float err = (target > 0.001f) ? (vpp - target) / target * 100.0f : 0.0f;
                printf("target %.3f -> Vin %.3f -> Vout %.3f Vpp (err %.2f%%)\r\n",
                       (double)target, (double)vin, (double)vpp, (double)err);
            }
            break;
        }

        case 'L': {
            ident_result_t r;
            printf("learning...\r\n");
            if (IDENT_Learn(&r, 0, 0) == 0)
            {
                printf("type = %s\r\n", IDENT_TypeName(r.type));
                printf("K = %.3f, f0 = %.1f Hz, Q = %.4f, err = %.5f\r\n",
                       (double)r.K, (double)r.f0_hz, (double)r.Q, (double)r.err);
            }
            else
            {
                printf("learn failed\r\n");
            }
            break;
        }

        default:
            printf("unknown cmd\r\n");
            break;
    }
}

static void cli_loop(void)
{
    static char buf[64];
    static int  len = 0;
    uint8_t ch = 0;

    if (uart2_getc(&ch, 20) != 0) return;

    if (ch == '\r' || ch == '\n')
    {
        if (len > 0)
        {
            buf[len] = '\0';
            cli_exec(buf);
            len = 0;
        }
        return;
    }

    if (len < (int)sizeof(buf) - 1) buf[len++] = (char)ch;
}

/* ------------------------------------------------------------------ main */
int main(void)
{
    bsp_clock_init();          /* 168 MHz + SysTick 1 ms */
    uart2_init(115200);

    printf("\r\n==== Circuit Model Explorer (STM32F407VET6, bare-metal) ====\r\n");
    printf("SYSCLK = %u Hz, DAC fs = %u SPS, ADC fs = %u SPS, N = %u\r\n",
           (unsigned)SYSCLK_HZ, (unsigned)DDS_FS_HZ,
           (unsigned)MEAS_FS_HZ, (unsigned)MEAS_N);

    DDS_Init();                /* 建表 → DAC DMA → TIM6 启动 */
    MEAS_Init();               /* ADC DMA → TIM3 启动 */

    DDS_SetFreq(1000.0f);
    DDS_SetAmpVpp(1.0f);

    printf("Ready. Type ? for help.\r\n");

    while (1)
    {
        cli_loop();
    }
}
