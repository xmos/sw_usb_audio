
#include <xs1.h>
#include <xs1_su.h>
#include <platform.h>


#define VOLT_TWEAK 20 //mV reduction

//Code to set the voltage (voltage is set to 10 * X + 600 mV):
#ifdef VOLT_TWEAK
void do_volt_tweak(void)
{
    int vout1LevelReg = 0x34;
    int powerUnit = 6;
    int time;
    unsigned writeval[1];
    unsigned char writevalc[1];



    for (unsigned count=0;count<(VOLT_TWEAK/10);count++)
    {
        writeval[0] = (39 - count);
write_periph_32(usb_tile, powerUnit, vout1LevelReg, 1, writeval); // 990 mV
for(int pw=0;pw<100;pw++);  // Wait approx 1us per step.
}
write_node_config_reg(stdcore[0], 7, 0x08); //set switch prescaler down to 1/8 (fast enough for galaxian)
        writeval[0] = 0x33;
write_periph_32(usb_tile, 6, 0x18, 1, writeval); //both DC-DCs in PWM mode, I/O and PLL supply on, Analogue & core on
        writeval[0] = 0x40;
write_periph_32(usb_tile, 6, 0x0, 1, writeval);//USB suspend off, voltage adjustable, sleep clock 32KHz
        writevalc[0] = 2;
write_periph_8(usb_tile, 4, 0x1, 1, writevalc); //Turn off on chip oscilator (20MHz or 32KHz)
writeval[0] = 0x000;
write_periph_32(usb_tile, 6, 0x2c, 1, writeval);//303 = 1.2MHz for DC-DCs, 000 for 0.9MHz DCDCs (default = 1MHz)
}
#endif //VOLT_TWEAK
