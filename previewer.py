"""
____   ____                                                       __  .__      __________                     .__                            
\   \ /   /____  ______   ____  __ _________  _________.__. _____/  |_|  |__   \______   \_______   _______  _|__| ______  _  __ ___________ 
 \   Y   /\__  \ \____ \ /  _ \|  |  \_  __ \/  ___<   |  |/    \   __\  |  \   |     ___/\_  __ \_/ __ \  \/ /  |/ __ \ \/ \/ // __ \_  __ \
  \     /  / __ \|  |_> >  <_> )  |  /|  | \/\___ \ \___  |   |  \  | |   Y  \  |    |     |  | \/\  ___/\   /|  \  ___/\     /\  ___/|  | \/
   \___/  (____  /   __/ \____/|____/ |__|  /____  >/ ____|___|  /__| |___|  /  |____|     |__|    \___  >\_/ |__|\___  >\/\_/  \___  >__|   
               \/|__|                            \/ \/         \/          \/                          \/             \/            \/       


Quickly preview a file or files using Vapoursynth with command line arguments
Uses 

"""


import sys
from pathlib import Path
#Add local packages/modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent.joinpath("packages").absolute()))

from screenutil import load_VS_files, replace_extension, path_exists, frame_info
from view import Preview
import vapoursynth as vs
from vapoursynth import core


"""
    Validate and parse input from global dictionary
"""

print(sys.path)
#print(str(Path(__file__).parents[0].joinpath("packages").absolute()))

def validate_input():
    args = dict()
    for key, value in dict(globals()).items():
        if key == "inputs":
            try:
                if "[" in value and "]" in value:
                    files = [x.strip() for x in value.strip('][').split(",")]
                elif "(" in value and ")" in value:
                    files = [x.strip() for x in value.strip(')(').split(",")]
                else:
                    files = [x.strip() for x in value.split(",")]
            except Exception as e:
                print("Something went wrong:", e.__class__)
                sys.exit(1)
            else:
                confirmed = list()
                for f in files:
                    if path_exists(f): confirmed.append(f)
                args["inputs"] = confirmed
                        
    
    return args


"""
    Main script logic
"""

args = validate_input()

lwi_files = replace_extension(args["inputs"])
clips = load_VS_files(lwi_files=lwi_files, in_files=args["inputs"])
Preview(clips[0])


# if len(clips) == 1:
#     clips[0].set_output()
# elif len(clips) > 1:
#     clips = list(clips)
#     out = core.std.Interleave(clips=clips)
#     out.set_output()
    
    