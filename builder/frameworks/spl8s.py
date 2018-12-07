from os.path import isdir, isfile, join
from string import Template

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-spl8s")
assert isdir(FRAMEWORK_DIR)

cpppaths = ['.']

cpppaths.append(
    join(FRAMEWORK_DIR, "STM8S_StdPeriph_Lib", "Libraries", "STM8S_StdPeriph_Driver", "inc")
)
cpppaths.append(
    join(FRAMEWORK_DIR, "STM8S_StdPeriph_Lib", "Libraries", "STM8S_StdPeriph_Driver", "src")
)
cpppaths.append(
    join(FRAMEWORK_DIR, "STM8S_StdPeriph_Lib", "Project", "STM8S_StdPeriph_Template")
)

env.Append(CPPPATH=cpppaths)