import os
import shutil
import urbs
from Database_to_urbs import Database_to_urbs

# # User preferences

version = '1.92'
suffix = "_eu"
year = 2020
result_folder = 'v1.91_eu_2015-20191220T0951_dummy'

# Generate input file from database
#Database_to_urbs(version, suffix, year, result_folder)
year = str(int(year))

input_files = 'urbs_model_v' + version + suffix + '_' + year + '.xlsx'  # for single year file name, for intertemporal folder name
input_dir = 'Input'
input_path = os.path.join(input_dir, input_files)

result_name = 'v' + version + suffix + '_' + str(year)
result_dir = urbs.prepare_result_directory(result_name)  # name + time stamp


# detailed reporting commodity/sites
report_tuples = [(int(year), 'AT', 'Elec'),
                 (int(year), 'BE', 'Elec'),
                 (int(year), 'BG', 'Elec'),
                 (int(year), 'CH', 'Elec'),
                 (int(year), 'CZ', 'Elec'),
                 (int(year), 'DE', 'Elec'),
                 (int(year), 'DK', 'Elec'),
                 (int(year), 'EE', 'Elec'),
                 (int(year), 'EL', 'Elec'),
                 (int(year), 'ES', 'Elec'),
                 (int(year), 'FI', 'Elec'),
                 (int(year), 'FR', 'Elec'),
                 (int(year), 'HR', 'Elec'),
                 (int(year), 'HU', 'Elec'),
                 (int(year), 'IE', 'Elec'),
                 (int(year), 'IT', 'Elec'),
                 (int(year), 'LT', 'Elec'),
                 (int(year), 'LU', 'Elec'),
                 (int(year), 'LV', 'Elec'),
                 (int(year), 'NL', 'Elec'),
                 (int(year), 'NO', 'Elec'),
                 (int(year), 'PL', 'Elec'),
                 (int(year), 'PT', 'Elec'),
                 (int(year), 'RO', 'Elec'),
                 (int(year), 'SE', 'Elec'),
                 (int(year), 'SI', 'Elec'),
                 (int(year), 'SK', 'Elec'),
                 (int(year), 'UK', 'Elec'),
                 ]



# Export to output database
#urbs_to_Database(version, suffix, year, result_dir)