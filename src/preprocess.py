import json
import xml.etree.ElementTree as ET
import os
import pandas as pd
from tqdm import tqdm


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {}

    # Store tags and their subtags
    tags = [
        'nct_id',
        'link_text',
        'url',
        'id_info',
        'brief_title',
        'sponsors',
        'brief_summary',
        'detailed_description',
        'primary_purpose',
        'intervention',
        'eligibility',
        'gender',
        'minimum_age',
        'maximum_age',
        'healthy_volunteers',
        'keyword',
        'condition_browse'
    ]

    for tag in tags:
        data[tag] = extract_data(root, tag)

    return data


def extract_data(element, tag):
    data = []

    try:
        for child in element.iter(tag):
            content = extract_content(child)
            data.append(content)
        return data if len(data) > 1 else data[0]
    except:
        return None


def extract_content(element):
    if len(element) > 0:
        content = {}
        for child in element:
            content[child.tag] = extract_content(child)
        if content.get('textblock', None):
            content = content[list(content.keys())[0]]
    else:
        content = ' '.join(element.text.strip().split()).replace(': ', ' ').replace(' - ', ' ')  # Remove unnecessary characters

    return content


def get_file_names(raw_data_folder_path):
    file_paths = []
    for splits in os.scandir(raw_data_folder_path):
        if splits.is_dir():
            for nct_dir in os.scandir(splits.path):
                for file in os.scandir(nct_dir.path):
                    if file.is_file():
                        file_paths.append(file.path)
    return file_paths

def find_xml_without_eligibility_tag(data_dir = 'data/raw'):
    """
    Find all the XML files without eligibility tag in TREC 2023 CT
    """
    xml_files = get_file_names(data_dir)
    xml_withuot_eligibility = set()
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Check if <eligibility> tag exists as an immediate child of root
        eligibility_tag = root.find('eligibility')
        if not eligibility_tag:
            xml_withuot_eligibility.add(xml_file)
    return list(xml_withuot_eligibility)


def preprocess_all_documents(raw_data_folder_path, output_path):
    file_paths = get_file_names(raw_data_folder_path)

    dict_list = []
    for file_path in tqdm(file_paths, desc='Parsing XML files to json:', disable=False, position=0, leave=True):
        parsed_data = parse_xml(file_path)
        dict_list.append(parsed_data)

    df = pd.DataFrame.from_dict(dict_list)


    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(df.to_dict(), file, ensure_ascii=False, indent=4)

    return None


if __name__ == '__main__':

    # Specify the path to your XML file
    raw_data_folder_path = os.path.normpath(os.getcwd() + '/..' + '/data/raw/')
    output_path = os.path.normpath(os.getcwd() + '/..' + '/data/processed/data.json')

    ###
    # TEST: Parse the XML file and store the data in a dictionary
    file_path = os.path.normpath(os.getcwd()  + '/..' + '/data/raw/ClinicalTrials.2023-05-08.trials0/NCT0000xxxx/NCT00000102.xml')
    parsed_data_test = parse_xml(file_path)
    # Print the dictionary containing the parsed data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
    for key, value in parsed_data_test.items():
        print(f"{key}: {value}")
    ###

    preprocess_all_documents(raw_data_folder_path, output_path)
    print('Done')
    print('Output path: ' + output_path)
