"""
    Build script for test.py
    test-builder.py
"""

from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

def __getSize(size_type, env):
    # FIXME: i don't really know how to do this right. see:
    #        https://community.platformio.org/t/missing-integers-in-board-extra-flags-in-board-json/821
    return str(env.BoardConfig().get("build", {
        # defaults
        "size_heap": 1024,
    })[size_type])


def _parseSdccFlags(flags):
    assert flags
    if isinstance(flags, list):
        flags = " ".join(flags)
    flags = str(flags)
    parsed_flags = []
    unparsed_flags = []
    prev_token = ""
    for token in flags.split(" "):
        if prev_token.startswith("--") and not token.startswith("-"):
            parsed_flags.extend([prev_token, token])
            prev_token = ""
            continue
        if prev_token:
            unparsed_flags.append(prev_token)
        prev_token = token
    unparsed_flags.append(prev_token)
    return (parsed_flags, unparsed_flags)

env = DefaultEnvironment()
board_config = env.BoardConfig()

env.Replace(
    AR="sdar",
    AS="sdas8051",
    CC="sdcc",
    LD="sdld",
    RANLIB="sdranlib",
    OBJCOPY="sdobjcopy",
    OBJSUFFIX=".rel",
    LIBSUFFIX=".lib",
    SIZETOOL=join(env.PioPlatform().get_dir(), "builder", "size.py"),

    SIZECHECKCMD='$PYTHONEXE $SIZETOOL $SOURCES',
    SIZEPRINTCMD='"$PYTHONEXE" $SIZETOOL $SOURCES',
    SIZEPROGREGEXP=r"^ROM/EPROM/FLASH\s+[a-fx\d]+\s+[a-fx\d]+\s+(\d+).*",

    PROGNAME="firmware",
    PROGSUFFIX=".hex"
)

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],

    CFLAGS=[
        "--std-sdcc11"
    ],

    CCFLAGS=[
        "--opt-code-size",  # optimize for size
        "--peep-return",    # peephole optimization for return instructions
        "-mstm8"
    ],

    LINKFLAGS=[
        "-mstm8",
        "--out-fmt-ihx"
    ]
)

if int(ARGUMENTS.get("PIOVERBOSE", 0)):
    env.Prepend(UPLOADERFLAGS=["-v"])

# parse manually SDCC flags
if env.get("BUILD_FLAGS"):
    _parsed, _unparsed = _parseSdccFlags(env.get("BUILD_FLAGS"))
    env.Append(CCFLAGS=_parsed)
    env['BUILD_FLAGS'] = _unparsed

project_sdcc_flags = None
if env.get("SRC_BUILD_FLAGS"):
    project_sdcc_flags, _unparsed = _parseSdccFlags(env.get("SRC_BUILD_FLAGS"))
    env['SRC_BUILD_FLAGS'] = _unparsed

#
# Target: Build executable and linkable firmware
#

target_firm = env.BuildProgram()

if project_sdcc_flags:
    env.Import("projenv")
    projenv.Append(CCFLAGS=project_sdcc_flags)

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)

#
# Target: Print binary size
#

target_size = env.Alias(
    "size", target_firm,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Setup default targets
#

Default([target_buildprog, target_size])