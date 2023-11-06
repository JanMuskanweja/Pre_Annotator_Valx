import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import argparse

import pandas as pd
import numpy as np

import subprocess

# Check if psycopg2-binary is installed
try:
    import psycopg2
except ImportError:
    # If psycopg2 is not installed, install psycopg2-binary
    subprocess.run(['pip', 'install', 'psycopg2-binary'])

import psycopg2
from psycopg2 import Error
import datetime

import os

#PATH = 'data-1697389172633.csv'

#'/mnt/mdrive/ctti/Clinical-Trial-Parser-main/data/ner/medical_ner.tsv' ,sep='\t'


db_config = {
    'host': 'localhost',
    'port': '5432',  
    'database': 'doccano_db',
    'user': 'doccano_user',
    'password': 'abc357'
}

# function : determining what constitutes as one bullet point

def scrape_criteria_section_by_header(next,data,bound_condition):
    def bound_check(bound_condition,next):
        if bound_condition=="exc" and next and next.name=='p':
            return  not cond_to_check_for_exclusion_para_text(next.get_text().lower())
        return True
        
    def remove_style_attributes(tag):
        # Remove all style attributes from the tag
        if tag.has_attr('style'):
            del tag['style']

       # Recursively remove style attributes from all descendants
        for descendant in tag.descendants:
            if hasattr(descendant, 'attrs') and descendant.has_attr('style'):
                del descendant['style']

        return str(tag)

    while next:
        if  bound_check(bound_condition,next):
            if next.name=='p':
                res = ""
                if next.find_next_sibling() and next.find_next_sibling().name in ['ul','ol']:
                    res+=remove_style_attributes(next)
                    res+= remove_style_attributes(next.find_next_sibling())
                    data.append(res)
                    next = next.find_next_sibling()
                else:
                    data.append(next.text)
            # extract_incase_ul_ol_tags
            elif next.name in ['ul','ol']:
                for li in next.find_all('li',recursive=False):
                    if li.find_all():
                        data.append(remove_style_attributes(li))
                    else:
                        data.append(li.text)
            else:
                print('exception : a never before seen tag encountered')
            next= next.find_next_sibling()
        else:
            break

def add_to_words_to_exclude(words_to_exclude,lis):
    for s in lis:
        words_to_exclude.extend(s.replace(':','').lower().strip().split())
    return words_to_exclude

def cond_to_check_for_exclusion_para_text(para_text):
    para_text = para_text.lower()
    acceptable = ['exclusion criteria','The following persons will be excluded:','Criteria for Exclusion:','Exclusion Criterion:']
    return any(item.lower() in para_text for item in acceptable) or para_text == 'exclusion' or para_text == 'exclusion:' or para_text == 'exclusion :' or para_text == 'PATIENT INELIGIBILITY'.lower()


def cond_to_check_for_inclusion_para_text(para_text):
    para_text = para_text.lower()
    acceptable = ['inclusion criteria', 'ENTRY CRITERIA:', 'We will include persons that meet the following criteria:','Criteria for Inclusion:','Inclusion Criterion:']
    return any(item.lower() in para_text for item in acceptable) or para_text == 'inclusion'  or para_text == 'inclusion:'  or para_text == 'inclusion :' or para_text == 'PATIENT ELIGIBILITY'.lower()

def  handle_criteria_section_header(para,inclusion_data,exclusion_data):
    # NCT04134325
    para_text = para.get_text().lower()
    
    words_to_exclude = ["exclusion","inclusion", "criteria"]
    
    list_sentences = ['Patients with any of the following cannot be included in this study:',
                    'Subjects must meet the following criteria to participate in this study:',
                    'Subjects with any of the following exclusion criteria were not eligible for this trial:',
                      'PROTOCOL ENTRY CRITERIA:',
                      'We will include persons that meet the following criteria:',
                      'The following persons will be excluded:',
                      'Exclusion Criterion:',
                      'PATIENT INELIGIBILITY',
                      'PATIENT ELIGIBILITY']
    
    add_to_words_to_exclude(words_to_exclude,list_sentences)
    
    filtered_words = [word for word in para_text.replace(':','').strip().split() if word not in words_to_exclude ]
    
    if cond_to_check_for_inclusion_para_text(para_text) :
        if filtered_words:
            scrape_criteria_section_by_header(para, inclusion_data,"exc")
        else:
            scrape_criteria_section_by_header(para.find_next_sibling(), inclusion_data,"exc")

    if cond_to_check_for_exclusion_para_text(para_text):
        if filtered_words:
            scrape_criteria_section_by_header(para, exclusion_data,"")
        else:
            scrape_criteria_section_by_header(para.find_next_sibling(), exclusion_data,"")

def remove_duplicates_ordered(input_list):
    seen = set()
    result = []
    for item in input_list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def save_to_db(nctid,criterias,eligtype):

    for i,criteria in enumerate(criterias):
        cursor = conn.cursor()
        sql = """INSERT INTO miimansa.criteria_inventory (nctid, projectid, complexity, eligtype, criterion, status, createdon, remark, criterion_text, simplicity_score,seq_no)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        if eligtype == 'generic':
            i = -1
        values = (nctid, None, None, eligtype, criteria, None, datetime.date.today(),None,None,None,i+1)
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()

# using beautifulSoup scrape eleigibility section from clinicaltrials webpage

def scrape_and_save_to_db(nct_id, conn, data_dictionary):

    url = f"https://classic.clinicaltrials.gov/ct2/show/{nct_id}"
    response = requests.get(url)
    
    inclusion_data = []
    exclusion_data = []
    table_data = []
    all_data = []

    if response.status_code == 200:
    
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            
            for section in soup.find_all("div",class_ = "tr-indent1"):
                for header in section.find_all("div",class_ = "ct-header2"):
                    if header and "Eligibility Criteria" in header.get_text():
                        
                        # parse table setion to inclusion
                        table = section.find("table")
                        for row in table.find_all("tr"):
                            cells = row.find_all("td")
                            row_data = [cell.text.strip() for cell in cells]
                            if row_data:
                                table_data.append(" ".join(row_data))
                
                        #parse eleigibility section to get inclusion and exclusion criterias
                        for para in section.select("div.tr-indent2 > p"):
                            handle_criteria_section_header(para,inclusion_data,exclusion_data)
                
                        if not section.select("div.tr-indent2 > p") or exclusion_data == []:# or len(inclusion_data)==3 :
                            for para in section.select("div.tr-indent2 > ul > li > p"):
                                handle_criteria_section_header(para,inclusion_data,exclusion_data)

                        if inclusion_data == [] and exclusion_data == [] :
                            if section.select("div.tr-indent2 > ul,div.tr-indent2 > ol, div.tr-indent2 > p"):
                                x=section.select("div.tr-indent2 > ul,div.tr-indent2 > ol, div.tr-indent2 > p")[0]
                                if x.get_text() == "Eligibility Criteria:" or x.get_text() == "All participants must meet the following criteria:":
                                    x = x.find_next_sibling()
                
                                scrape_criteria_section_by_header(x, all_data,"")
              
                            else:
                                all_data.append(section.select('div.tr-indent2 > div.tr-indent2')[0].get_text())
                                
                        inclusion_data = remove_duplicates_ordered(inclusion_data)
                        exclusion_data = remove_duplicates_ordered(exclusion_data)
                
                        # data_dictionary['id'].append(nct_id)
                        # data_dictionary['inc'].append(inclusion_data)
                        # data_dictionary['exc'].append(exclusion_data)
                        # data_dictionary['all_data'].append(all_data)
                        # data_dictionary['table'].append(exclusion_data)
                
                        #save to db
                        save_to_db(nct_id,inclusion_data,'inclusion')
                        save_to_db(nct_id,exclusion_data,'exclusion')
                        save_to_db(nct_id,table_data,'generic')
                        save_to_db(nct_id,all_data,None)
                
        except Exception as e:
            with open('log.txt', 'a') as log_file:
                log_file.write(f"For {nct_id}: Exception {e} occured\n")
        
    else:
        with open('log.txt', 'a') as log_file:
            log_file.write(f"API request for {nct_id} failed with status code: {response.status_code}\n")
    
    #break
    # don't wanna spam
    time.sleep(5)
    
    #data_dictionary
    #prob_ids

def connect_to_database():
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Reads a CSV file with 'nct_ids' as column name to scrape data from clinicaltrials.gov")
    parser.add_argument("PATH", help="Path to CSV file")
    
    args = parser.parse_args()

    nct_ids = pd.read_csv(args.PATH)['nct_ids'].drop_duplicates().values

    conn = connect_to_database()

    if conn:
        data_dictionary = {'id':[],'inc':[],'exc':[],'all_data':[],'table':[]}

        for nct_id in tqdm(nct_ids):
            scrape_and_save_to_db(nct_id, conn, data_dictionary)

        conn.close()

        # Saves to csv id,criteria
        # df = pd.DataFrame.from_dict(data_dictionary)
        # inc_criterias =  df[['id','inc']].explode('inc')
        # exc_criterias = df[['id','exc']].explode('exc')
        
        # exc_criterias.to_csv('exc_cart_criterias_preserving_relationship.csv', index=False)
        # inc_criterias.to_csv('inc_cart_criterias_preserving_relationship.csv', index=False)







