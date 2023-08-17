import os
import xmltodict
import json
import pandas as pd
from tqdm import tqdm
import xml.etree.ElementTree as ET


def get_file_names(raw_data_folder_path):
    """
    Get all the file paths in a list
    :param raw_data_folder_path: path to the raw data folder
    :return: list of file paths
    """
    file_paths = []
    for splits in os.scandir(raw_data_folder_path):
        if splits.is_dir():
            for nct_dir in os.scandir(splits.path):
                for file in os.scandir(nct_dir.path):
                    if file.is_file():
                        file_paths.append(file.path)
    return file_paths


def find_xml_without_eligibility_tag(data_dir='data/raw'):
    """
    Find all the XML files without eligibility tag in TREC 2023 CT
    :param data_dir: path to the raw data folder
    :return: list of file paths without eligibility tag
    """
    xml_files = get_file_names(data_dir)
    xml_without_eligibility = set()
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Check if <eligibility> tag exists as an immediate child of root
        eligibility_tag = root.find('eligibility')
        if not eligibility_tag:
            xml_without_eligibility.add(xml_file)
    return list(xml_without_eligibility)


def get_xml_full_path_from_nct_ids(indexes, raw_data_folder_path):
    """
    Get the full path of the XML files from a list of NCT IDs and a path to the raw data folder
    :param indexes: list of NCT IDs
    :param raw_data_folder_path: path to the raw data folder
    :return: list of full paths of the XML files
    """
    file_paths = get_file_names(raw_data_folder_path)
    indexes_set = set(indexes)
    res_paths = [file_path for file_path in file_paths if file_path[-15:-4] in indexes_set]
    return res_paths


def make_json_dump_from_xml_file_paths(file_paths, output_file_name='data_none'):
    """
    Dumps all the contente from a specific XML file in a json file
    :param file_paths: list of XML file paths
    :param output_file_name: name of the output file
    :return: None (stores the data in a json file)
    """
    output_path = os.path.normpath(os.getcwd() + '/..' + '/data/processed/' + output_file_name + '.json')

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


def make_json_dump_from_df(df, output_path):
    """
    Dumps all the contents from a specific dataframe in a json file
    :param df: dataframe
    :param output_path: path to the output json file
    :return: None (stores the data in a json file)
    """
    df = pd.DataFrame.from_dict(dict_list)['eligibility']

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(df.to_dict(), file, ensure_ascii=False, indent=4)

    return None
