/**
  ******************************************************************************
  * @file    bsp.c
  * @brief   寄存器级板级驱动实现
  *
  * 时钟树：
  *   HSE 8 MHz → /M(8) = 1 MHz → ×N(336) = 336 MHz → /P(2) = 168 MHz
  *   AHB = 168 MHz，APB1 = 42 MHz（定时器 84 MHz），APB2 = 84 MHz
  ******************************************************************************
  */
#include "bsp.h"
#include "stm32f4xx.h"

volatile uint32_t g_ms_tick = 0;

/* ------------------------------------------------------------------ 时钟 */
void bsp_clock_init(void)
{
    /* 1. 打开 HSE */
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY)) { }

    /* 2. 打开 PWR 时钟，选电压调节器 Scale 1（168 MHz 必须） */
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    PWR->CR |= PWR_CR_VOS;

    /* 3. 配 PLL：M=8, N=336, P=2, Q=7, 源 = HSE */
    RCC->PLLCFGR = (8u   << RCC_PLLCFGR_PLLM_Pos)
                 | (336u << RCC_PLLCFGR_PLLN_Pos)
                 | (0u   << RCC_PLLCFGR_PLLP_Pos)   /* 00 = /2 */
                 | (7u   << RCC_PLLCFGR_PLLQ_Pos)
                 | RCC_PLLCFGR_PLLSRC_HSE;

    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY)) { }

    /* 4. Flash 等待周期：168 MHz 需要 5 WS，并开预取与 I/D Cache */
    FLASH->ACR = FLASH_ACR_LATENCY_5WS | FLASH_ACR_PRFTEN
               | FLASH_ACR_ICEN | FLASH_ACR_DCEN;

    /* 5. 总线分频：AHB /1，APB1 /4，APB2 /2 */
    RCC->CFGR = RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2;

    /* 6. 切换系统时钟到 PLL */
    RCC->CFGR |= RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) { }

    /* 7. 更新全局变量并起 1 ms 系统节拍 */
    SystemCoreClockUpdate();
    SystemCoreClock = SYSCLK_HZ;
    SysTick_Config(SYSCLK_HZ / 1000u);
}

void SysTick_Handler(void)
{
    g_ms_tick++;
}

void delay_ms(uint32_t ms)
{
    uint32_t t0 = g_ms_tick;
    while ((g_ms_tick - t0) < ms) { }
}

void delay_us(uint32_t us)
{
    /* 用 DWT 周期计数器做微秒级延时（比空循环准） */
    static uint8_t inited = 0;
    if (!inited)
    {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        inited = 1;
    }
    uint32_t start = DWT->CYCCNT;
    uint32_t ticks = us * (SYSCLK_HZ / 1000000u);
    while ((DWT->CYCCNT - start) < ticks) { }
}

/* ------------------------------------------------------------------ 串口 */
void uart2_init(uint32_t baud)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

    /* PA2 = TX, PA3 = RX，复用模式 AF7 */
    GPIOA->MODER &= ~((3u << (2u * 2u)) | (3u << (3u * 2u)));
    GPIOA->MODER |=  ((2u << (2u * 2u)) | (2u << (3u * 2u)));
    GPIOA->AFR[0] &= ~((0xFu << (2u * 4u)) | (0xFu << (3u * 4u)));
    GPIOA->AFR[0] |=  ((7u   << (2u * 4u)) | (7u   << (3u * 4u)));
    GPIOA->OSPEEDR |= (3u << (2u * 2u)) | (3u << (3u * 2u));

    /* BRR = PCLK1 / baud，含 4 位小数 */
    uint32_t div = (PCLK1_HZ + baud / 2u) / baud;
    USART2->BRR = div;

    USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
}

int uart2_getc(uint8_t *c, uint32_t timeout_ms)
{
    uint32_t t0 = g_ms_tick;
    while (!(USART2->SR & USART_SR_RXNE))
    {
        if ((g_ms_tick - t0) >= timeout_ms) return -1;
    }
    *c = (uint8_t)(USART2->DR & 0xFFu);
    return 0;
}

/* --------------------------------------------------------------- 定时器 */
void tim6_start(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_TIM6EN;
    TIM6->PSC = 0;
    TIM6->ARR = (TIM_CLK_HZ / 1000000u) - 1u;      /* 84-1 → 1 MHz */
    TIM6->CR2 = TIM_CR2_MMS_1;                     /* TRGO = 更新事件 */
    TIM6->EGR = TIM_EGR_UG;
    TIM6->SR  = 0;
    TIM6->CR1 = TIM_CR1_CEN;
}

void tim3_start(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
    TIM3->PSC = 0;
    TIM3->ARR = (TIM_CLK_HZ / 500000u) - 1u;       /* 168-1 → 500 kHz */
    TIM3->CR2 = TIM_CR2_MMS_1;
    TIM3->EGR = TIM_EGR_UG;
    TIM3->SR  = 0;
    TIM3->CR1 = TIM_CR1_CEN;
}

/* ------------------------------------------------------------ DAC + DMA */
void dac_dma_start(uint16_t *buf, uint32_t len)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_DMA1EN;
    RCC->APB1ENR |= RCC_APB1ENR_DACEN;

    /* PA4 设为模拟模式（DAC 输出） */
    GPIOA->MODER |= (3u << (4u * 2u));

    /* DMA1 Stream5 Channel7 = DAC1_CH1 的固定请求线（硬件连线，不可改）
     * 内存 → 外设，半字，循环，半满/全满中断 */
    DMA1_Stream5->CR &= ~DMA_SxCR_EN;
    while (DMA1_Stream5->CR & DMA_SxCR_EN) { }
    DMA1->HIFCR = (0x3Fu << 6);                    /* 清 Stream5 全部标志（bit6~11） */

    DMA1_Stream5->PAR  = (uint32_t)&DAC->DHR12R1;
    DMA1_Stream5->M0AR = (uint32_t)buf;
    DMA1_Stream5->NDTR = len;
    DMA1_Stream5->FCR  = 0;

    DMA1_Stream5->CR = (7u << DMA_SxCR_CHSEL_Pos)
                     | DMA_SxCR_MSIZE_0 | DMA_SxCR_PSIZE_0
                     | DMA_SxCR_MINC | DMA_SxCR_CIRC
                     | DMA_SxCR_HTIE | DMA_SxCR_TCIE
                     | DMA_SxCR_DIR_0;             /* 内存→外设 */

    NVIC_SetPriority(DMA1_Stream5_IRQn, 1);
    NVIC_EnableIRQ(DMA1_Stream5_IRQn);

    DMA1_Stream5->CR |= DMA_SxCR_EN;
    while (!(DMA1_Stream5->CR & DMA_SxCR_EN)) { }

    /* DAC 通道 1：TSEL=000（TIM6 TRGO），使能触发、DMA、通道 */
    DAC->CR = DAC_CR_TEN1 | DAC_CR_DMAEN1 | DAC_CR_EN1;
}

/* ------------------------------------------------------------ ADC + DMA */
static uint32_t s_adc_len = 0;
static uint16_t *s_adc_buf = 0;
volatile uint8_t g_adc_done = 0;

void adc_dma_init(uint16_t *buf, uint32_t len)
{
    s_adc_buf = buf;
    s_adc_len = len;

    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_DMA2EN;
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    /* PA0 模拟输入 */
    GPIOA->MODER |= (3u << 0);

    /* ADC 时钟 = PCLK2 / 4 = 21 MHz（不超过 36 MHz） */
    ADC->CCR = ADC_CCR_ADCPRE_0;

    ADC1->CR1 = 0;
    ADC1->CR2 = (8u << ADC_CR2_EXTSEL_Pos)   /* TIM3_TRGO */
              | ADC_CR2_EXTEN_0              /* 上升沿触发 */
              | ADC_CR2_DMA | ADC_CR2_DDS;
    ADC1->SMPR2 = (2u << 0);                 /* 通道 0 采样 15 周期 */
    ADC1->SQR1  = 0;                         /* 规则序列长度 1 */
    ADC1->SQR3  = 0;                         /* 第 1 个转换 = 通道 0 */

    /* DMA2 Stream0 Channel0：外设 → 内存，半字，普通模式 */
    DMA2_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA2_Stream0->CR & DMA_SxCR_EN) { }
    DMA2->LIFCR = 0x3Fu;

    DMA2_Stream0->PAR  = (uint32_t)&ADC1->DR;
    DMA2_Stream0->M0AR = (uint32_t)buf;
    DMA2_Stream0->NDTR = len;
    DMA2_Stream0->FCR  = 0;
    DMA2_Stream0->CR = (0u << DMA_SxCR_CHSEL_Pos)
                     | DMA_SxCR_MSIZE_0 | DMA_SxCR_PSIZE_0
                     | DMA_SxCR_MINC | DMA_SxCR_TCIE;

    NVIC_SetPriority(DMA2_Stream0_IRQn, 2);
    NVIC_EnableIRQ(DMA2_Stream0_IRQn);
}

void adc_dma_arm(void)
{
    DMA2_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA2_Stream0->CR & DMA_SxCR_EN) { }

    DMA2->LIFCR = 0x3Fu;
    DMA2_Stream0->M0AR = (uint32_t)s_adc_buf;
    DMA2_Stream0->NDTR = s_adc_len;

    ADC1->SR = 0;                            /* 清 OVR / EOC */
    g_adc_done = 0;

    /* 先开 DMA 再开 ADC：否则 tSTAB 期间的转换会因无人搬运而置 OVR */
    DMA2_Stream0->CR |= DMA_SxCR_EN;
    ADC1->CR2 |= ADC_CR2_ADON;
    delay_us(10);                            /* tSTAB，datasheet 最大 3 us，留 10 us 余量 */
}

void adc_dma_stop(void)
{
    DMA2_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA2_Stream0->CR & DMA_SxCR_EN) { }
    ADC1->CR2 &= ~ADC_CR2_ADON;
}

/* --------------------------------------------------------------- 中断入口 */
void DMA2_Stream0_IRQHandler(void)
{
    if (DMA2->LISR & (1u << 5))              /* TCIF0 */
    {
        DMA2->LIFCR = (1u << 5);
        g_adc_done = 1;
    }
}
