#ifndef _PORTS_H_
#define _PORTS_H_

/* Additional ports used in this application instance */

/* For this design the USB reset port is on port 32A, this port is also used for some GPIO items.\
 * We can't simply declare it here as we would like to i.e:
 *
 * on stdcore[0] : out port p_gpio = XS1_PORT_32A;
 * 
 * since the compiler would issue an error.  We'll use some assembly magic to work around this.
 */
#endif 
