#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import shutil


HERE = Path(__file__).parent.resolve()
USER_C_MODULES= HERE / "user_mods" / "micropython.cmake"
LV_MOD = HERE / "user_mods" / "lvgl"
LV_CMAKE = LV_MOD / "lvgl.cmake"
LV_MANIFEST = LV_MOD / "manifest.py"
LV_LIB = LV_MOD / "lib"
BOARD="WS_ESP32S3_2.8LCD"


def prepare_env():
    os.environ['USER_C_MODULES'] = str(USER_C_MODULES)
    os.environ["BOARD"] = BOARD


def ensure_cmd(cmd, echo=True):
    if echo:
        print(cmd)
    r = os.system(cmd)
    if r != 0:
        exit(r)


def build(jobs):
    prepare_env()
    if not LV_CMAKE.exists():
        LV_CMAKE.touch()
    if not LV_MANIFEST.exists():
        LV_MANIFEST.touch()
    cwd = Path(os.environ["PWD"])  # different from os.getcwd()
    os.chdir(cwd.parent.parent)
    ensure_cmd(f"make -j{jobs}")


def gen_lvgl(lv_binding: Path, force=False):
    print("generating lv_mpy.c from", lv_binding)
    lvgl = lv_binding / "lvgl"
    lv_pp = LV_MOD / "lvgl.pp.c"
    lv_mpy = LV_MOD / "lv_mpy.c"
    lv_mpy_meta = LV_MOD / "lv_mpy.json"
    if not lv_mpy.exists() or force:
        ensure_cmd(f"cc -E -DPYCPARSER -I {lv_binding}/pycparser/utils/fake_libc_include {lvgl}/lvgl.h > {lv_pp}")
        cmd = (
            f"cd {lvgl} && "
            f"python3 {lv_binding}/gen/gen_mpy.py"
            f" "
            f"-M lvgl -MP lv -MD {lv_mpy_meta} -E {lv_pp} {lvgl}/lvgl.h"
        )
        print
        process = os.popen(
            cmd
        )
        content = process.read()
        # patch the content
        content = content.replace('mp_generic_unary_op', 'mp_unary_op')

        with open(lv_mpy, "w") as file:
            # STATIC is not defined, so add it
            file.write('#define STATIC static\n')
            file.write(content)

    if not LV_CMAKE.exists() or force:
        # generate makefile
        print(f"write to {LV_CMAKE}")
        with open(LV_CMAKE, "w") as file:
            file.writelines([
                f"file(GLOB_RECURSE ASRCS {lvgl}/src/*.S)\n",
                f"file(GLOB_RECURSE CSRCS {lvgl}/src/*.c)\n",
                f"file(GLOB_RECURSE CPPSRCS {lvgl}/src/*.cpp)\n",
                'target_sources(my_lvgl INTERFACE ${CMAKE_CURRENT_LIST_DIR}/lv_mpy.c ${CSRCS} ${CPPSRCS})\n',
                # Add the current directory as an include directory.
                f"target_include_directories(my_lvgl INTERFACE {lv_binding} {lvgl})\n"
            ])

    binding_lib = lv_binding / "lib"
    if not LV_LIB.exists() or force:
        print(f"copy {binding_lib}")
        if LV_LIB.exists():
            shutil.rmtree(LV_LIB)
        shutil.copytree(binding_lib, LV_LIB)
        # then prepare the manifest file
        with open(LV_MANIFEST, "w") as file:
            for one in LV_LIB.iterdir():
                if not one.suffix == '.py' or not one.is_file:
                    continue
                one = one.resolve()
                file.write(f'module({repr(one.name)}, base_path={repr(str(one.parent))})\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--without-lvgl", "-n", action='count', default=0,
                        help="if you are using the micropython repo by lvgl, please disable lvgl by this flag")
    parser.add_argument("--lv_binding", "-b", default=None,
                        help="path to https://github.com/lvgl/lv_binding_micropython")
    parser.add_argument("--force", "-f", action="count", default=0, help="force to generate the lv_mpy.py")
    parser.add_argument("--jobs", "-j", default="", help="jobs")

    args = parser.parse_args()
    jobs = args.jobs
    # prepare the lvgl dir
    # This is even before non-lvgl build because blank files are also needed for building
    LV_MOD.mkdir(exist_ok=True, parents=True)

    if args.without_lvgl:
        build(jobs)
        return
    # We must build the extensions
    lv_binding = args.lv_binding
    if lv_binding is None:
        lv_binding = os.environ.get("LV_BINDING", None)
    if lv_binding is None:
        lv_binding = HERE / "lv_binding_micropython"
        lv_binding.resolve()
    lv_binding = Path(lv_binding)
    if not lv_binding.exists() or not lv_binding.is_dir():
        print("Unable to locate lv_binding_micropython")
        parser.print_help()
        exit(-1)
    gen_lvgl(lv_binding, args.force)
    build(jobs)


if __name__ == "__main__":
    main()
