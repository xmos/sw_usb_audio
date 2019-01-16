USB Audio 6.15.3 maintenance release
====================================

.. To render, place in a directory alongside xdoc.conf with XMOSNEWSTYLE=1
   and name outer directory by what you want the top right corner label to be.
   Run xdoc upload_issue to set Cognidox ID in bottom right corner. Render with
   xdoc xmospdf. Scripted.

USB Audio 6.15.3 maintenance release
....................................

Test plan
~~~~~~~~~

Manual testing completed:

   * listening/loopback on all analogue I/O, every build config
   * spot check mic array board 1V4 with VBUS disconnected, both build configs
   * disable input volume control to exercise DFU bug
   * soak test DFU (40 download/revert iterations)
   * Windows playback and DFU using Thesycon utility
   * stream format change on Linux (issue not recreated)
   * S/PDIF output in hifi configuration
   * TDM slave sync checking unit test
   * native DSD operation to verify clocking fix
   * check USB version number
   * DFU pre-reboot delays on symbolic names now (compare .i)
   * build all configurations of enabled applications (non-MFi)
   * Windows xTIMEcomposer import and build

Unless stated otherwise, the MC AUDIO application in the i2s_slave build
configuration is tested against a Mac host (macOS 10.14). On Windows, Thesycon
driver 4.11.0 is installed. Windows 7 SP1 and 10 are tested. MC AUDIO board
configurations are all USB audio class 2.0. Mic array board has one class 1.0
and one class 2.0. Highest sample rate for given build config is used. Analogue
listening/loopback done on channels 1 to 8 (physical connectors). Where tests
target particular bug fixes, the issue is first reproduced with unmodified
6.15.2 firmware.

|newpage|

Notes
~~~~~

   * Linux stream format change always working (waive)
   * Windows endpoint 0 trap with 6.15.2, only intermittent reoccurence (waive)

There has been a suggestion that the trap issue could be bug 16942::

  ***** Call Stack *****
  #0  XUD_GetData_DataEnd () at /Users/larry/6152/sc_xud/module_xud/src/XUD_EpFuncs.S:296
  #1  0x00040c88 in XUD_DoGetRequest (ep_out=300472, ep_in=<value optimized out>, buffer=<value optimized out>, length=<value optimized out>, requested=<value optimized out>) at /Users/larry/6152/sc_xud/module_xud/src/XUD_EpFunctions.xc:101
  #2  0x00000000 in ?? ()
  Current language:  auto; currently asm

  ***** Disassembly *****
  0x43752 <XUD_GetData_DataEnd+2>:	int (2r)        r11, res[r10] *
  0x43754 <XUD_GetData_DataEnd+4>:	shr (2rus)      r11, r11, 0x3
  0x43756 <XUD_GetDataCalcDataLength>:	shl (2rus)      r3, r3, 0x2
  0x43758 <XUD_GetDataCalcDataLength+2>:	add (3r)        r3, r11, r3
  0x4375a <XUD_GetData_CheckPid>:	ldw (2rus)      r11, r0[0x6]

  ***** Registers *****
  r0             0x495b8	300472
  r1             0x7f830	522288
  r2             0x7f82c	522284
  r3             0x0	0
  r4             0x495b8	300472
  r5             0x49838	301112
  r6             0x198	408
  r7             0x100	256
  r8             0xffffffff	-1
  r9             0x45b30	285488
  r10            0x80030802	-2147284990
  r11            0x0	0
  cp             0x45858	284760
  dp             0x45b30	285488
  sp             0x7f810	522256
  lr             0x40c88	265352	 XUD_DoGetRequest + 116
  pc             0x43752	276306	 XUD_GetData_DataEnd + 2
  sr             0x51	81
  spc            0x43752	276306	 XUD_GetData_DataEnd + 2
  ssr            0x0	0
  et             0x4	4
  ed             0x80030802	-2147284990
  sed            0x0	0
  kep            0x40080	262272
  ksp            0x400aa	262314
