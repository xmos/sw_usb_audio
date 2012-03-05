#include "devicedefines.h"

#ifdef DFU

#include <xs1.h>
#include <xclib.h>
#include <flashlib.h>
#include <print.h>

#define settw(a,b) {__asm__ __volatile__("settw res[%0], %1": : "r" (a) , "r" (b));}
#define setc(a,b) {__asm__  __volatile__("setc res[%0], %1": : "r" (a) , "r" (b));}
#define setclk(a,b) {__asm__ __volatile__("setclk res[%0], %1": : "r" (a) , "r" (b));}
#define portin(a,b) {__asm__  __volatile__("in %0, res[%1]": "=r" (b) : "r" (a));}
#define portout(a,b) {__asm__  __volatile__("out res[%0], %1": : "r" (a) , "r" (b));}


#ifdef DFU_CUSTOM_FLASH_DEVICE
fl_DeviceSpec flash_devices[] = {DFU_FLASH_DEVICE};
#endif

fl_PortHolderStruct p_flash = {
    XS1_PORT_1A,
    XS1_PORT_1B,
    XS1_PORT_1C,
    XS1_PORT_1D,
    XS1_CLKBLK_2
};

int flash_cmd_enable_ports() {
  int result = 0;
  setc(p_flash.spiMISO, XS1_SETC_INUSE_OFF);
  setc(p_flash.spiCLK, XS1_SETC_INUSE_OFF);
  setc(p_flash.spiMOSI, XS1_SETC_INUSE_OFF);
  setc(p_flash.spiSS, XS1_SETC_INUSE_OFF);
  setc(p_flash.spiClkblk, XS1_SETC_INUSE_OFF);

  setc(p_flash.spiMISO, XS1_SETC_INUSE_ON);
  setc(p_flash.spiCLK, XS1_SETC_INUSE_ON);
  setc(p_flash.spiMOSI, XS1_SETC_INUSE_ON);
  setc(p_flash.spiSS, XS1_SETC_INUSE_ON);
  setc(p_flash.spiClkblk, XS1_SETC_INUSE_ON);

  setclk(p_flash.spiMISO, XS1_CLKBLK_REF);
  setclk(p_flash.spiCLK, XS1_CLKBLK_REF);
  setclk(p_flash.spiMOSI, XS1_CLKBLK_REF);
  setclk(p_flash.spiSS, XS1_CLKBLK_REF);

  setc(p_flash.spiMISO, XS1_SETC_BUF_BUFFERS);
  setc(p_flash.spiMOSI, XS1_SETC_BUF_BUFFERS);

  settw(p_flash.spiMISO, 8);
  settw(p_flash.spiMOSI, 8);

#ifndef DFU_CUSTOM_FLASH_DEVICE
  result = fl_connect(&p_flash);
#else
  result = fl_connectToDevice(&p_flash, flash_devices, 1);
#endif
  
  if (!result) {
    return 1;
  } else {
    return 0;
  }
}

int flash_cmd_disable_ports() {
  fl_disconnect();

  setc(p_flash.spiMISO, XS1_SETC_INUSE_OFF);
  setc(p_flash.spiCLK, XS1_SETC_INUSE_OFF);
  setc(p_flash.spiMOSI, XS1_SETC_INUSE_OFF);
  setc(p_flash.spiSS, XS1_SETC_INUSE_OFF);

  return 1;
}
#endif
