""" This script creates a source and binary release of sw_vocalfusion to match the
structure defined by the releases of VocalFusion Speaker available on xmos.com """

import datetime
import os
import sys
import sh
import shutil
from contextlib import contextmanager
from pathlib import Path

from zipfile import ZipFile

from sourcepackaging import (
    copy_source_tree,
    export_lib_if_needed,
    prepare_eclipse_files,
)

SW_VF = Path(__file__).parent.resolve()
XMOS_ROOT = (SW_VF / "..").resolve()
RELEASE_FOLDER = XMOS_ROOT / "Release"

# List of libraries to include in the release. These should be repos in the view
LIBS = [
    "lib_logging",
    "lib_mic_array",
    "lib_xassert"
]

# These have to be handled differently
SCS = [
    "sc_usb",
    "sc_adat",
    "sc_i2c",
    "sc_spdif",
    "sc_usb_audio",
    "sc_usb_device",
    "sc_xud",
    "sc_util"
]

# List of Software Reference Design repos. Should only contain sw_usb_audio
SW_REFS = [
    "sw_usb_audio",
]


@contextmanager
def pushd(new_dir):
    last_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(last_dir)


def copy_module(module_path, module_release_path):
    print(f"Processing module: {module_path.name}")

    export_lib_if_needed(module_path)

    print("Export finished")

    export_path = module_path / "export" / module_path.name
    # Prepare eclipse files (.project, .cproject, .xproject)
    if (module_path / ".cproject").is_file():
        # Copy .cproject to the export dir
        if export_path.is_dir():
            shutil.copy2(module_path / ".cproject", export_path)
        #prepare_eclipse_files(module_path)
        # Copy eclipse files back to the module dir
        if export_path.is_dir():
            for p in export_path.iterdir():
                if p.name.startswith(".") and p.is_file():
                    shutil.copy2(p, module_path)

    print("Eclipse files prepared")

    ignore_patterns = ["doc*", "*.metainfo", "*.buildinfo", ".build*", "export"]
    if module_path.name == "module_xud":
        # Specific rules for this module
        ignore_patterns += [
            "Makefile",
            "README*",
            "xud_conf_example.h",
            "libsrc",
        ]

    shutil.copytree(
        module_path,
        module_release_path,
        ignore=shutil.ignore_patterns(*ignore_patterns),
    )
    export_lib_path = module_path / "export" / module_path.name
    if export_lib_path.is_dir():
        shutil.copy2(
            export_lib_path / "module_build_info", module_release_path,
        )

    print("Module processing complete")

def main():
    try:
        RELEASE_FOLDER.mkdir(exist_ok=True)
    except FileExistsError:
        print(f'Error: Remove the file at "{RELEASE_FOLDER.resolve()}" and re-run')
        sys.exit(1)

    with open(SW_VF / "CHANGELOG.rst") as f:
        version = f.readlines()[3].strip()

    time_str = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

    vf_release_path = RELEASE_FOLDER / f"sw_usb_audio-[sw]_{version}"
    vf_src_release_path = vf_release_path / "source_release"
    vf_bin_release_path = vf_release_path / "binary_release"

    if vf_release_path.exists():
        answer = input(f"Release path {vf_release_path} already exists, remove it?")
        if "y" in answer:
            shutil.rmtree(vf_release_path)
        else:
            print("Exiting...")
            sys.exit(1)

    vf_src_release_path.mkdir(parents=True)
    vf_bin_release_path.mkdir(parents=True)

    for lib_name in LIBS:
        print(f"Processing lib: {lib_name}")
        # Create a release for each lib

        lib_path = XMOS_ROOT / lib_name
        lib_release_path = vf_src_release_path / lib_name
        lib_release_path.mkdir()

        ## Create PDF
        #doc_path = lib_path / lib_name / "doc"
        #print_fn = lambda a: print(a, end="")
        #if not "pdf" in [p.name for p in doc_path.iterdir()]:
        #    # Run xdoc
        #    with pushd(doc_path):
        #        sh.xdoc("xmospdf", _out=print_fn, _err=print_fn)

        # Prepare eclipse files (.project, .cproject, .xproject)
        if (lib_path / ".cproject").is_file():
            prepare_eclipse_files(module_path)

        # Find any app notes
        app_notes = [p.name for p in lib_path.iterdir() if p.name.startswith("AN")]

        copy_source_tree(
            lib_path,
            lib_release_path,
            exclude_subdirs=[lib_name, "tests", "examples"] + app_notes,
            silent_excludes=[lib_name],
        )
        # Copy the library folder separately in case it is a binary library export
        copy_source_tree(lib_path / lib_name, lib_release_path)

        # Copy the CHANGELOG and README to the root release folder
        os.remove(lib_release_path / lib_name / "CHANGELOG.rst")
        os.remove(lib_release_path / lib_name / "README.rst")

        shutil.copy2(
            str((lib_path / "CHANGELOG.rst").resolve()),
            str(lib_release_path.resolve()),
        )
        shutil.copy2(
            str((lib_path / "README.rst").resolve()), str(lib_release_path.resolve()),
        )
        # Copy the license to the root release folder
        shutil.copy2(
            (lib_path / "LICENSE.txt").resolve(), lib_release_path.resolve(),
        )

    for sc_name in SCS:
        print(f"Processing sc: {sc_name}")
        # Create a release for each sc

        sc_path = XMOS_ROOT / sc_name
        sc_release_path = vf_src_release_path / sc_name
        sc_release_path.mkdir()

        # Find any modules
        modules = [p for p in sc_path.iterdir() if p.name.startswith("module")]

        print("module : ", modules)

        for module_path in modules:
            copy_module(module_path, sc_release_path / module_path.name)

    for sw_name in SW_REFS:
        print(f"Processing sw: {sw_name}")

        sw_path = XMOS_ROOT / sw_name
        sw_release_path = vf_src_release_path / sw_name
        sw_release_path.mkdir()

        # Create PDFs
        doc_paths = [
            p for p in sw_path.iterdir() if p.is_dir() and p.name.startswith("doc")
        ]
        print_fn = lambda a: print(a, end="")
        for doc_path in doc_paths:
            doc_release_path = sw_release_path / doc_path.name
            out_pdf_path = doc_path / "_build" / "xlatex" / "index.pdf"
            if not out_pdf_path.is_file():
                # Run xdoc
                with pushd(doc_path):
                    sh.xdoc("xmospdf", _out=print_fn, _err=print_fn)
            pdf_name = sw_name
            variant = doc_path.name[len("doc_") :]
            if len(variant) > 0:
                pdf_name += "_" + variant
            pdf_release_path = doc_release_path / (pdf_name + ".pdf")
            pdf_release_path.parent.mkdir()
            shutil.copy2(out_pdf_path, pdf_release_path)

        # Prepare eclipse files (.project, .cproject, .xproject)
        if (sw_path / ".cproject").is_file():
            prepare_eclipse_files(module_path)

        # Find any app notes
        app_notes = [p.name for p in sw_path.iterdir() if p.name.startswith("AN")]
        # Find any excluded apps
        excluded_apps = [p.name for p in sw_path.iterdir() if p.name.startswith("__")]
        # Find any doc folder names
        doc_names = [p.name for p in doc_paths]

        excluded_subdirs = (
            [sw_name, "tests", "examples", ".venv"]
            + app_notes
            + excluded_apps
            + doc_names
        )

        copy_source_tree(
            sw_path,
            vf_src_release_path,
            exclude_subdirs=excluded_subdirs,
            silent_excludes=[sw_name],
        )

        # Remove all FILES from the sw release dir
        for p in sw_release_path.iterdir():
            if p.is_file():
                p.unlink()
        # Copy only the CHANGELOG, Makefile, and README
        shutil.copy2(
            str((sw_path / "CHANGELOG.rst").resolve()), str(sw_release_path.resolve()),
        )
        shutil.copy2(
            str((sw_path / "README.rst").resolve()), str(sw_release_path.resolve()),
        )
        shutil.copy2(
            str((sw_path / "Makefile").resolve()), str(sw_release_path.resolve()),
        )

        ## Copy any files in the root
        #for path in sw_path.iterdir():
        #    if path.name == "Makefile" or path.suffix in [".rst", ".txt"]:
        #        shutil.copy2(path, sw_release_path)

        # Find any modules
        modules = [p for p in sw_path.iterdir() if p.name.startswith("module")]

        # Prepare eclipse files
        if (module_path / ".cproject").is_file():
            prepare_eclipse_files(module_path)

    print("Release created.")

    # Package zip
    zip_name = vf_release_path.name + ".zip"
    zip_path = RELEASE_FOLDER / zip_name
    if zip_path.is_file():
        zip_path.unlink()
    with ZipFile(zip_path, 'w') as release_zip:
        with pushd(vf_src_release_path):
            # Write all files in release folder
            for root, dirs, files in os.walk("."):
                for f in files:
                    release_zip.write(os.path.join(root, f))
    print("Created {}".format(zip_name))




if __name__ == "__main__":
    main()