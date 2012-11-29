/*
 * Copyright (C) XMOS Limited 2008 - 2012
 * 
 * The copyrights, all other intellectual and industrial property rights are
 * retained by XMOS and/or its licensors.
 *
 * The code is provided "AS IS" without a warranty of any kind. XMOS and its
 * licensors disclaim all other warranties, express or implied, including any
 * implied warranty of merchantability/satisfactory quality, fitness for a
 * particular purpose, or non-infringement except to the extent that these
 * disclaimers are held to be legally invalid under applicable law.
 *
 */


#include "trim_code.h"

unsigned write_data_bit (core c, unsigned curr_val, unsigned bit)
{
  unsigned wdata;
  wdata = (curr_val & DIN_MASK) | ((bit&1)<<4);    
  write_node_config_reg(c,XS1_SU_CFG_PMU_TEST_MODE_ADRS,wdata);
  wdata |= ~(CLK_MASK);
  write_node_config_reg(c,XS1_SU_CFG_PMU_TEST_MODE_ADRS,wdata);
  wdata &=  CLK_MASK;
  write_node_config_reg(c,XS1_SU_CFG_PMU_TEST_MODE_ADRS,wdata);
  return wdata;
  
}

void write_test_register ( core c, unsigned pmu_add, unsigned pmu_data)
{
  int bc;
  unsigned curr_val;
  
  read_node_config_reg(c, XS1_SU_CFG_PMU_TEST_MODE_ADRS, curr_val);
  for (bc=11;bc>=0;bc--) {
    curr_val = write_data_bit(c, curr_val,(pmu_add >> bc));
  }
  curr_val = write_data_bit(c, curr_val, 1);
  for (bc=0;bc<3;bc++) {
    curr_val = write_data_bit(c, curr_val,0);
  }  
  for (bc=7;bc>=0;bc--) {
    curr_val = write_data_bit(c, curr_val,(pmu_data >> bc));    
  }  
  for (bc=0;bc<8;bc++) {
    curr_val = write_data_bit(c, curr_val,0);
  }
  
}

#ifdef ENABLE_PG2_PRINT_CONFIRM  
unsigned read_test_register ( core c, unsigned pmu_add)
{
  
  int bc;
  unsigned bit;
  unsigned tmp_rdata; 
  unsigned curr_val;
  unsigned pmu_rdata;
  
  pmu_rdata = 0;
  read_node_config_reg(c, XS1_SU_CFG_PMU_TEST_MODE_ADRS, curr_val);
  for (bc=11;bc>=0;bc--) {
    curr_val = write_data_bit(c, curr_val,(pmu_add >> bc));
  }
  curr_val = write_data_bit(c, curr_val,0);
  for (bc=0;bc<3;bc++) {
    curr_val = write_data_bit(c, curr_val,0);
  }
 
  for (bc=7;bc>=0;bc--) {
    curr_val = write_data_bit(c, curr_val,0);
    read_node_config_reg(c, XS1_SU_CFG_PMU_TEST_MODE_ADRS, tmp_rdata);
    pmu_rdata |= (((tmp_rdata>>8)&1) << bc);
  }
  for (bc=0;bc<8;bc++) {
    curr_val = write_data_bit(c, curr_val,0);
  }
  return pmu_rdata;
}
#endif


void set_PG2_trim (core c)
{

#define GTI_REG_OFFSET 32

  unsigned int data_u[1];
  unsigned char trim_addr[3] = {GTI_REG_OFFSET+24  , GTI_REG_OFFSET+26  , GTI_REG_OFFSET+32};
  unsigned int  trim_data[3] = {0x02, 0x14, 0x02};
  
  read_periph_32 (c, XS1_SU_PERIPH_PWR_ID, XS1_SU_PWR_PMU_CTRL_ADRS, 1, data_u);
  
  if ((data_u[0] & ~XS1_SU_PWR_DCDC_CLK_DIVS_MASK) != (0x3 << XS1_SU_PWR_VOUT2_CLK_DIV_BASE | 
                                                       0x3 << XS1_SU_PWR_VOUT1_CLK_DIV_BASE) ) {

#ifdef ENABLE_PG2_PRINT_CONFIRM  
  printstr("Applying PG2 TRIM Settings\n");
#endif  

  write_node_config_reg(c, XS1_SU_CFG_PMU_TEST_MODE_ADRS, 0x4);
  for (int i=0 ; i<3; i++) {
    write_test_register(c, trim_addr[i], trim_data[i]);

#ifdef ENABLE_PG2_PRINT_CONFIRM  
    printstr("PMU R"); printint((trim_addr[i]-GTI_REG_OFFSET)); 
    printstr(" 0x"); printhexln(trim_data[i]);

#endif

  }
 
  data_u[0] &= XS1_SU_PWR_DCDC_CLK_DIVS_MASK;
  data_u[0] |= (0x3 << XS1_SU_PWR_VOUT2_CLK_DIV_BASE | 
                0x3 << XS1_SU_PWR_VOUT1_CLK_DIV_BASE) ;
  write_periph_32(c, XS1_SU_PERIPH_PWR_ID, XS1_SU_PWR_PMU_CTRL_ADRS, 1, data_u);

  } 
  

#ifdef ENABLE_PG2_PRINT_CONFIRM  
  printstr("\nConfirming PG2 TRIM Settings\n");

  write_test_register(c,0x21,1);

  for (int i=0 ; i<3; i++) {
    int tmp = read_test_register(c, trim_addr[i]);
    printstr("PMU R"); printint((trim_addr[i]-GTI_REG_OFFSET)); 
    printstr(" 0x"); printhex(tmp);

    if (tmp !=  trim_data[i]) {
      printstrln(" -> Error Trim not correct");
    } else {
      printstrln("");
    }

  }
  read_periph_32 (c, XS1_SU_PERIPH_PWR_ID, XS1_SU_PWR_PMU_CTRL_ADRS, 1 , data_u);
  printstr("XS1_GLX_PWR_PMU_CTRL_ADRS: 0x"); printhexln(data_u[0]);

#endif

}

void trimcode()
{
    set_PG2_trim(xs1_su);
}


