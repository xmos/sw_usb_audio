.. _usb_audio_sec_mixer:

Digital Mixer
-------------

The mixer core(s) take outgoing audio from the decoupler core and incoming
audio from the audio driver core. It then applies the volume to each
channel and passes incoming audio on to the decoupler and outgoing
audio to the audio driver. The volume update is achieved using the
built-in 32bit to 64bit signed multiply-accumulate function
(``macs``). The mixer is implemented in the file 
``mixer.xc``.

The mixer takes two cores and can perform eight mixes with
up to 18 inputs at sample rates up to 96kHz and two mixes with up to 18
inputs at higher sample rates. The component automatically moves
down to two mixes when switching to a higher rate.

The mixer can take inputs from either:

   * The USB outputs from the host---these samples come from the decoupler core.
   * The inputs from the audio interface on the device---these
     samples come from the audio driver.

Since the sum of these inputs may be more then the 18 possible mix
inputs to each mixer, there is a mapping from all the
possible inputs to the mixer inputs.

After the mix occurs, the final outputs are created. There are two
output destinations:

   * The USB inputs to the host---these samples are sent to the decoupler core.

   * The outputs to the audio interface on the device---these samples
     are sent to the audio driver.

For each possible output, a mapping exists to tell the mixer what its
source is. The possible sources are the USB outputs from the host, the
inputs for the audio interface or the outputs from the mixer units.

As mentioned in :ref:`usb_audio_sec_audio-requ-volume`, the mixer can also
handle volume setting. If the mixer is configured to handle volume but
the number of mixes is set to zero (so the component is solely doing
volume setting) then the component will use only one core.

Control
~~~~~~~

The mixers can receive the following control commands from the Endpoint 0 core via a channel: 

.. list-table:: Mixer Component Commands
 :header-rows: 1

 * - Command
   - Description

 * - ``SET_SAMPLES_TO_HOST_MAP``
   - Sets the source of one of the audio streams going to the host.

 * - ``SET_SAMPLES_TO_DEVICE_MAP``
   - Sets the source of one of the audio streams going to the audio
     driver.

 * - ``SET_MIX_MULT``
   - Sets the multiplier for one of the inputs to a mixer.

 * - ``SET_MIX_MAP``
   - Sets the source of one of the inputs to a mixer.

 * - ``SET_MIX_IN_VOL``
   - If volume adjustment is being done in the mixer, this command
     sets the volume multiplier of one of the USB audio inputs.

 * - ``SET_MIX_OUT_VOL``
   - If volume adjustment is being done in the mixer, this command
     sets the volume multiplier of one of the USB audio outputs.

Host Control
~~~~~~~~~~~~

The mixer can be controlled from a host PC by sending requests to Endpoint 0. XMOS provides a simple 
command line based sample application demonstrating how the mixer can be controlled. 

For details, consult the README file in the host_usb_mixer_control directory.

The main requirements of this control are to

  * Set the mapping of input channels into the mixer
  * Set the coefficients for each mixer output of each input
  * Set the mapping for physical outputs which can either come
    directly from the inputs or via the mixer.

There is enough flexibility within this configuration that there will often
be multiple ways of creating the required solution.

Whilst using the XMOS Host control example application, consider setting the
mixer to perform a loop-back from analogue inputs 1 and 2 to analogue
outputs 1 and 2. 

First consider the inputs to the mixer::

  ./xmos_mixer --display-aud-channel-map 0

displays which channels are mapped to which mixer inputs::

  ./xmos_mixer --display-aud-channel-map-sources 0

displays which channels could possibly be mapped to mixer inputs. Notice
that analogue inputs 1 and 2 are on mixer inputs 10 and 11.

Now examine the audio output mapping::

  ./xmos_mixer --display-aud-channel-map 0

displays which channels are mapped to which outputs. By default all
of these bypass the mixer. We can also see what all the possible
mappings are::

  ./xmos_mixer --display-aud-channel-map-sources 0

So now map the first two mixer outputs to physical outputs 1 and 2::

  ./xmos_mixer --set-aud-channel-map 0 26
  ./xmos_mixer --set-aud-channel-map 1 27

You can confirm the effect of this by re-checking the map::

  ./xmos_mixer --display-aud-channel-map 0

This now makes analogue outputs 1 and 2 come from the mixer, rather
than directly from USB. However the mixer is still mapped to pass
the USB channels through to the outputs, so there will still be no
functional change yet.

The mixer nodes need to be individually set. They can be displayed
with::

  ./xmos_mixer --display-mixer-nodes 0

To get the audio from the analogue inputs to outputs 1 and 2, nodes 80
and 89 need to be set::

  ./xmos_mixer --set-value 0 80 0
  ./xmos_mixer --set-value 0 89 0

At the same time, the original mixer outputs can be muted::

  ./xmos_mixer --set-value 0 0 -inf
  ./xmos_mixer --set-value 0 9 -inf

Now audio inputs on analogue 1/2 should be heard on outputs 1/2. 

As mentioned above, the flexibility of the mixer is such that there
will be multiple ways to create a particular mix. Another option to
create the same routing would be to change the mixer sources such that
mixer 1/2 outputs come from the analogue inputs. 

To demonstrate this, firstly undo the changes above::

  ./xmos_mixer --set-value 0 80 -inf
  ./xmos_mixer --set-value 0 89 -inf
  ./xmos_mixer --set-value 0 0 0
  ./xmos_mixer --set-value 0 9 0

The mixer should now have the default values. The sources for mixer
1/2 can now be changed::

  ./xmos_mixer --set-mixer-source 0 0 10
  ./xmos_mixer --set-mixer-source 0 1 11

If you rerun::

  ./xmos_mixer --display-mixer-nodes 0

the first column now has AUD - Analogue 1 and 2 rather than DAW (Digital Audio Workstation i.e. the
host) - Analogue 1 and 2 confirming the new mapping. Again, by playing audio into analogue inputs 
1/2 this can be heard looped through to analogue outputs 1/2.




