# This variable should contain a space separated list of all
# the directories containing buildable applications (usually
# prefixed with the app_ prefix)
BUILD_SUBDIRS =  ./app_usb_aud_xk_evk_xu316_extrai2s \
				 ./app_usb_aud_xk_216_mc \
				 ./app_usb_aud_xk_316_mc \
				 ./app_usb_aud_xk_evk_xu316

# This variable should contain a space separated list of all
# the directories containing buildable plugins (usually
# prefixed with the plugin_ prefix)
PLUGIN_SUBDIRS =

# This variable should contain a space separated list of all
# the directories containing applications with a 'test' make target
TEST_SUBDIRS =

# Provided that the above variables are set you shouldn't need to modify
# the targets below here.

%.all:
	cd $* && xmake BUILD_TEST_CONFIGS=1 all

%.clean:
	cd $* && xmake BUILD_TEST_CONFIGS=1 clean

all: $(foreach x, $(BUILD_SUBDIRS), $x.all)
plugins: $(foreach x, $(PLUGIN_SUBDIRS), $x.all)
clean: $(foreach x, $(BUILD_SUBDIRS), $x.clean)
clean_plugins: $(foreach x, $(PLUGIN_SUBDIRS), $x.clean)
test: $(foreach x, $(TEST_SUBDIRS), $x.test)
