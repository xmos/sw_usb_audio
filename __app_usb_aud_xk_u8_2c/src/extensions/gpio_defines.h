
/* General output port bit definitions (port 32A) */
#define P_GPIO_SS_EN_CTRL       0x001    /* SPI Slave Select Enable. 0 - SPI SS Enabled, 1 - SPI SS Disabled. */
#define P_GPIO_MCLK_SEL         0x002    /* MCLK frequency select. 0 - 22.5792MHz, 1 - 24.576MHz. */
#define P_GPIO_5VA_EN           0x004    /* Enable 5v power for DAC/ADC */
#define P_GPIO_LEDB             0x008
#define P_GPIO_LEDA             0x010
#define P_GPIO_USB_SEL1         0x020
#define P_GPIO_USB_SEL2         0x040
#define P_GPIP_CPR_RST_N        0x080    /* Apple CoProcessor Reset */
#define P_GPIO_ACC_DET_EN       0x100
#define P_GPIO_AUD_MUTE         0x200
#define P_GPIO_VBUS_OUT_EN      0x400
#define P_GPIO_RST_DAC          (1<<28)
#define P_GPIO_RST_ADC          (1<<29)
#define P_GPIO_DSD_EN           (1<<30)


#define P_GPI_DEVDET_SHIFT      0x0
#define P_GPI_DEVDET_MASK       (1<<P_GPI_DEVDET_SHIFT)
#define P_GPI_BUTA_SHIFT        0x01
#define P_GPI_BUTA_MASK         (1<<P_GPI_BUTA_SHIFT)
#define P_GPI_BUTB_SHIFT        0x02
#define P_GPI_BUTB_MASK         (1<<P_GPI_BUTB_SHIFT)
#define P_GPI_SW1_SHIFT         0x03
#define P_GPI_SW1_MASK          (1<<P_GPI_SW1_SHIFT)

