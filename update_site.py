
# import subprocess
from gen_mod_data import run as run_gen_data
run_gen_data(True)

# import glob
# import os
# list_of_files = glob.glob('./public/data/*')
# latest_file = max(list_of_files, key=os.path.getctime)
# print(latest_file)

from cf_zone_purge import purgeAll
purgeAll()
