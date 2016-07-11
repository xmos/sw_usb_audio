//This is factory reset code execueted at startup by the second stage loader
//Allows revert to factory image by holding buttons at power on reset
//Half of this source is compiled into the bootloader and the other half
//is compiled into the main application. This is guarded by XUD_SERIES_SUPPORT

#include <xs1.h>
#include <platform.h>
#include "gpio_defines.h"

#define DBG 0


// Defines which button(s) must be pressed to trigger factory revert in bootloader
// And for how long (seconds)
#define BUTTON_MASK_REVERT   P_GPIO_VOL_DOWN
#define BUTTON_HOLD_TIME_S   3

/* Address of flag set by bootloader if factory revert is required */
/* Note range 0x7FFC8 - 0x7FFFF guarenteed to be untouched by tools */
#define FLAG_ADDRESS       0x7ffc8
#define MAGIC_NUMBER       0xdeadb007

static void storeflag(unsigned x)
{
    asm("stw %0, %1[0]" :: "r"(x), "r"(FLAG_ADDRESS));
}

#if DBG
on tile[0]: out port p_debug = XS1_PORT_4D;  //Mic ports, used for debug
#endif

#if !defined(XUD_SERIES_SUPPORT)    //Only compile this for the stage 2 bootloader


/* The xCORE loader first calls the function init, and then iterates
 * over each image in the boot partition. For each image, it calls
 * checkCandidateImageVersion with the image version number and,
 * if this function returns non-zero and its CRC is validated, it calls
 * recordCandidateImage with the image version number and address.
 * Finally, the loader calls reportSelectedImage to obtain the address
 * of the selected image. */


/* Buttons are on bit 0..2. Active high */
on tile[0]: in port p_buttons = XS1_PORT_8C;

int selected_idx;   //Index to firmware version we want to boot
unsigned imgAdr;    //Address of firmware image
int revert_flag = 0;//Set to non-zero to force factory revert

void init(void)
{
    int buttons_val;
    int counter = 0;
#if DBG
    int toggle = 0;      //Debug for port
#endif
    selected_idx =  1;   //Choose boot image (always index zero)

    set_port_pull_down(p_buttons);
    delay_microseconds(10); // Allow pull downs to kick in

    p_buttons :> buttons_val;

    //Stay in this loop until buttons released so we don't keep reverting
    while(buttons_val & BUTTON_MASK_REVERT)
    {
        delay_milliseconds(1);
        p_buttons :> buttons_val;
        counter++;

#if DBG
        p_debug <: toggle;
        toggle ^= 0b1;
#endif
    }

    if (counter > (BUTTON_HOLD_TIME_S * 1000))
    {
        storeflag(MAGIC_NUMBER);
        revert_flag = 1;
#if DBG
        p_debug <: 0b10;
#endif
    }
    else
    {
        storeflag(0);   //Clear down flag to ensure we do not accidentally revert by random
    }
}

int checkCandidateImageVersion(int version)
{
    //Take largest image index unless we want to revert
    if (selected_idx > -1 && selected_idx == version && !revert_flag)
      return 1;
    else
      return 0;
}

void recordCandidateImage(int v, unsigned adr)
{
      imgAdr = adr;
}

//This returns the address of the final image we will boot
unsigned reportSelectedImage(void)
{
      return imgAdr;
}

#else
#include "flash_interface.h"
#include "dfu_interface.h"
#include "dfu_types.h"

void device_reboot(chanend spare);

static unsigned loadflag(void)
{
    unsigned x;
    asm("ldw %0, %1[0]" : "=r"(x) : "r"(FLAG_ADDRESS));
    return x;
}

//This is called by EP0 at startup to check to see if we need to do the revert
void revert_flash_if_flag_set(client interface i_dfu i_dfu, chanend spare){
    unsigned data_buffer[8];
    unsigned data_buffer_len = 8;
    unsigned dfuState;
    USB_SetupPacket_t sp;

    if (loadflag() == MAGIC_NUMBER){
        storeflag(0);   //Clear down flag to avoid repeat revert next time around
#if DBG
        static int i = 0;
        while(i < 0x10000){
            p_debug <: i;
            i ^= 1;
        }
#endif
        sp.bRequest = XMOS_DFU_REVERTFACTORY;

        //Do the request to the DFU task
        i_dfu.HandleDfuRequest(sp, data_buffer, data_buffer_len, dfuState);
        delay_milliseconds(1500);   //Wait for flash to complete
        device_reboot(spare);       //Restart from factory image
    }
}

#endif

