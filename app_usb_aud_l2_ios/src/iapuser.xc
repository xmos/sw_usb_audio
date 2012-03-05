/* Functions that must be implemented by vendor for board support purposes 
 * 
 * Implementation for demo on L2 USB Audio board - No real iDevice support!
 *
 */

/* Enable/Power-on/Reset etc coProcessor - called before authentication */
void CoProcessorEnable(void)
{

}

/* Disable co-processor - Called at end of authentication */
void CoProcessorDisable(void)
{
}

/* Select Apple 30 pin connector */
void SelectUSBDock(void)
{

}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{

}

/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
    return 0;
}
