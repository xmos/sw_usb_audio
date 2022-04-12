volcontrol:
	gcc -framework AudioToolbox -framework CoreAudio -framework CoreFoundation -I . volcontrol.c volcontrol_impl.c -o volcontrol

.PHONY: clean
clean:
	rm -rf volcontrol
