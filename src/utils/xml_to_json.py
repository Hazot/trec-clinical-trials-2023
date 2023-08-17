import xmltodict
import json
import os
from tqdm import tqdm
import pandas as pd
from pathlib import Path


def get_file_names(raw_data_folder_path):
    file_paths = []
    for splits in os.scandir(raw_data_folder_path):
        if splits.is_dir():
            for nct_dir in os.scandir(splits.path):
                for file in os.scandir(nct_dir.path):
                    if file.is_file():
                        file_paths.append(file.path)
    return file_paths

def xml_files_from_one_folder_to_json(raw_data_folder_path, output_path):

    path = Path(raw_data_folder_path)
    file_paths = [file for folder in path.iterdir() for file in folder.iterdir()]

    dict_list = []
    for file_path in tqdm(file_paths, desc='Parsing XML files to json:', disable=False, position=0, leave=True):
        with open(file_path, 'r') as f:
            xml_string = f.read()
        json_data = xmltodict.parse(xml_string)
        dict_list.append(json_data)

    df = pd.DataFrame.from_dict(dict_list)

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(df.to_dict(), file, ensure_ascii=False, indent=4)

    return None


def main():
    # Specify the folder to export in JSON
    trial_folder_number = 'trials0'
    raw_data_folder_path = os.path.normpath(os.getcwd() + '/data/raw/ClinicalTrials.2023-05-08.' + trial_folder_number)
    output_path = os.path.normpath(os.getcwd() + '/data/processed/data_' + trial_folder_number + '.json')
    # output_path = os.path.normpath(os.getcwd() + '/data/processed/data.json')

    xml_files_from_one_folder_to_json(raw_data_folder_path, output_path)

    print('Done')
    print('Output path: ' + output_path)


if __name__ == '__main__':
    main()
