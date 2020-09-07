from argparse import ArgumentParser
from pathlib import Path

from infr_scripts_py.make_legacy_release import make_release

SW_VF = Path(__file__).parent.resolve()
XMOS_ROOT = (SW_VF / "..").resolve()

# Name used for release zips
RELEASE_NAME = "usb_audio"

# List of libraries to include in the release. These should be repos in the view
LIBS = [
    "lib_logging",
    "lib_mic_array",
    "lib_xassert",
]

# These have to be handled differently
SCS = [
    "sc_adat",
    "sc_i2c",
    "sc_spdif",
    "sc_usb",
    "sc_usb_audio",
    "sc_usb_device",
    "sc_util",
    "sc_xud",
]

# Software Reference Design repo. This is the name of the repo being released.
SW_REF = "sw_usb_audio"


# List of doc names that require explicit document number changes
# Used to do a find/replace on the exported PDFs
# Dictionary[doc_name] = (Old doc number, New doc number)
COGNIDOX_DOC_NUMBER_CHANGES = {}

# List of configs to build for the release
CONFIGS = [
]

# Name of the app to build
APP = "app_usb_aud_xk_216_mc"

# List of files that should be copied from this repo to the binary release zip
# (src_path, dst_path)
BINARY_RELEASE_FILES = [
]

def main():
    args = parse_args()
    viewname = args.view

    make_release(
        XMOS_ROOT,
        RELEASE_NAME,
        LIBS,
        SCS,
        SW_REF,
        CONFIGS,
        APP,
        BINARY_RELEASE_FILES,
        viewname=args.view,
        cognidox_doc_number_changes=COGNIDOX_DOC_NUMBER_CHANGES
    )

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--view",
        help="For CI, specify a viewname rather than reading from viewfile",
        default=None,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
