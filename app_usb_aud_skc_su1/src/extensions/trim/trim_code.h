
#include <xs1.h>
#include <xs1_su.h>
#include <platform.h>



#ifndef _trim_code_h
#define _trim_code_h

//#define ENABLE_PG2_PRINT_CONFIRM

#ifdef ENABLE_PG2_PRINT_CONFIRM 
#include <print.h>
#endif

// #if ( defined XVBGX1 )
// #define SLINK_DEF XS1_SSWITCH_SLINK_3_NUM
// #define XLINK_DEF XS1_SSWITCH_XLINK_3_NUM
// #else
#define SLINK_DEF XS1_SSWITCH_SLINK_5_NUM
#define XLINK_DEF XS1_SSWITCH_XLINK_5_NUM
// #endif

//Defines for XSSC registers & fields
#define XS1_SU_PWR_VOUT1_CLK_DIV_SIZE 0x5
#define XS1_SU_PWR_VOUT1_CLK_DIV_BASE 0x0
#define XS1_SU_PWR_VOUT2_CLK_DIV_SIZE 0x5
#define XS1_SU_PWR_VOUT2_CLK_DIV_BASE 0x8
#define XS1_SU_PWR_VOUT2_CLK_DIV_SIZE 0x5
#define XS1_SU_PWR_VOUT2_CLK_DIV_BASE 0x8
#define XS1_SU_PERIPH_PWR_ID          0x6
#define XS1_SU_CFG_PMU_TEST_MODE_ADRS 0x54
#define XS1_SU_PWR_PMU_CTRL_ADRS      0x2c 
#define XS1_SU_CFG_LINK_CTRL_ADRS     0x80
#define XS1_SU_CFG_SYS_CLK_FREQ_ADRS  0x51

#define XS1_SU_PWR_DCDC_CLK_DIVS_MASK ~((((1<<XS1_SU_PWR_VOUT2_CLK_DIV_SIZE)-1) << XS1_SU_PWR_VOUT2_CLK_DIV_BASE ) | \
                                   (((1<<XS1_SU_PWR_VOUT1_CLK_DIV_SIZE)-1) << XS1_SU_PWR_VOUT1_CLK_DIV_BASE) )

//Masking for trim interface              
#define DIN_MASK 0xffffffef 
#define CLK_MASK 0xfffffff7

#endif

extern void set_PG2_trim (core c);

