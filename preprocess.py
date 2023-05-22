import logging
import xml.etree.ElementTree as ET
import os

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {}

    # Store tags and their subtags
    tags = [
        'required_header',
        # 'link_text',
        # 'url',
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
    else:
        content = element.text.strip()

    return content

def preprocess_all_documents(logger: logging.Logger):
    return None


if __name__ == '__main__':
    # Specify the path to your XML file
    # file_path = os.path.normpath(os.path.abspath() + '/data/raw/ClinicalTrials.2023-05-08.trials0/NCT0000xxxx/NCT00000102.xml')
    file_path = os.path.normpath(os.getcwd() + '/data/raw/ClinicalTrials.2023-05-08.trials0/NCT0000xxxx/NCT00000102.xml')
    print(file_path)
    # Parse the XML file and store the data in a dictionary
    parsed_data = parse_xml(file_path)

    # Print the dictionary containing the parsed data
    print(json.dump)
    for key, value in parsed_data.items():
        print(f"{key}: {value}")
    # logger = logging.getLogger(__name__)
    # preprocess_all_documents(logger)
