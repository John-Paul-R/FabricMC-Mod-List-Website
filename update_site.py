
import subprocess
from gen_mod_data import run as run_gen_data
run_gen_data(True)

# import glob
# import os
# list_of_files = glob.glob('./public/data/*')
# latest_file = max(list_of_files, key=os.path.getctime)
# print(latest_file)

print("Restarting fibermc.com.service...")
subprocess.run("systemctl restart fibermc.com.service", shell=True, check=True)
print("Finish service restart.")

print("Purging Cloudfare cache...")
from cf_zone_purge import purgeAll
purgeAll()

import mod_list_maker
from dotenv import load_dotenv
import os
load_dotenv()
OUTPUT_DIR = str(os.getenv("OUTPUT_DIR"))
mod_list_maker.run(False, os.path.join(OUTPUT_DIR, "mod_list-text_response.json"), False, False, True)
