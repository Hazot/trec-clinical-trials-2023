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
    """
    Original primary tags from TREC 2023 CT:
    tags = [
        "required_header",
        "id_info"
        "brief_title",
        "acronym",
        "official_title",
        "sponsors",
        "source",
        "oversight_info",
        "brief_summary",
        "detailed_description",
        "overall_status",
        "last_known_status",
        "why_stopped",
        "start_date",
        "completion_date",
        "primary_completion_date",
        "phase",
        "study_type",
        "has_expanded_access",
        "expanded_access_info",
        "study_design_info",
        "target_duration",
        "primary_outcome",
        "secondary_outcome",
        "other_outcome",
        "number_of_arms",
        "number_of_groups",
        "enrollment",
        "condition",
        "arm_group",
        "intervention",
        "biospec_retention",
        "biospec_descr",
        "eligibility",
        "overall_official",
        "overall_contact",
        "overall_contact_backup",
        "location",
        "location_countries",
        "removed_countries",
        "link",
        "reference",
        "results_reference",
        "verification_date",
        "study_first_submitted",
        "study_first_submitted_qc",
        "study_first_posted",
        "results_first_submitted",
        "results_first_submitted_qc",
        "results_first_posted",
        "disposition_first_submitted",
        "disposition_first_submitted_qc",
        "disposition_first_posted",
        "last_update_submitted",
        "last_update_submitted_qc",
        "last_update_posted",
        "responsible_party",
        "keyword",
        "condition_browse",
        "intervention_browse",
        "patient_data",
        "study_docs",
        "provided_document_section",
        "pending_results",
        "clinical_results"
    """
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
    """
    Extracts data from the XML file recursively specified by the tag
    :param element: XML element
    :param tag: tag to extract
    :return: extracted data from the tag
    """
    data = []

    try:
        for child in element.iter(tag):
            content = extract_content(child)
            data.append(content)
        return data if len(data) > 1 else data[0]
    except:
        return None


def extract_content(element):
    """
    Extracts content from an XML tag, filters out unnecessary characters and returns the content
    :param element: XML element
    :return: extracted content from the element
    """
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

def find_xml_without_eligibility_tag(data_dir = 'data/raw'):
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


def preprocess_all_documents(raw_data_folder_path, output_path):
    """
    Preprocesses all the documents in the raw data folder and stores the data in a json file
    :param raw_data_folder_path: path to the raw data folder
    :param output_path: path to the output json file
    :return: None (stores the data in a json file)
    """
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

    # Specify the path to your XML file (RUN FROM PROJECT ROOT)
    raw_data_folder_path = os.path.normpath(os.getcwd() + '/data/raw/')
    output_path = os.path.normpath(os.getcwd() + '/data/processed/data.json')

    #######################
    # TEST: Parse the XML file and store the data in a dictionary
    file_path = os.path.normpath(os.getcwd() + '/data/raw/ClinicalTrials.2023-05-08.trials0/NCT0000xxxx/NCT00000102.xml')
    parsed_data_test = parse_xml(file_path)
    # Print the dictionary containing the parsed data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
    for key, value in parsed_data_test.items():
        print(f"{key}: {value}")
    ########################

    # Preprocess all the documents in the raw data folder and store the data in a json file
    preprocess_all_documents(raw_data_folder_path, output_path)

    print('Done')
    print('Output path: ' + output_path)
