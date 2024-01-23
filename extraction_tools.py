import numpy as np
import pandas as pd
from typing import Dict, List

import argparse

import re 

from pdfminer.high_level import extract_text

from datetime import date

from pydantic import BaseModel
from pymodels import *
# --------------------------------------------------------------------------------------------------------

def cell_BN(txt: str) -> Dict[str, str]:
    """
    """
    p0 = r'\(BN\)(.*?)[A-Z]{2}\d{4}'

    p1 = r'[A-Z]{2}\d{4}'

    p2 = r'\d{5} \d{4}'

    res_tmp0 = re.search(p0, txt)

    idx00, idx01 = res_tmp0.span()

    res_tmp1 = txt[idx00: idx01]

    idx10, idx11 = re.search(p1, res_tmp1).span()
    idx20, idx21 = re.search(p2, res_tmp1).span()

    cell_ = Cell(cell_number='001',
                 cell_value=res_tmp1[idx20: idx21] + '-' + res_tmp1[idx10: idx11])

    return {cell_.cell_number: cell_.cell_value}


def cell_002(txt: str) -> Dict[str, str]:
    """
    """
    # line 002
    idx0, idx1 = re.search(r'002(.*?)Ad', txt).span()

    value_ = txt[idx0: idx1][len('002'): -len('Ad')].strip()
    key_ = '002'

    return {key_: value_}


def cell_011_012(txt: str) -> Dict[str, str]:
    """
    """
    idx0, idx1 = re.search(r'018.(.*?)011', txt).span()
    idx2, idx3 = re.search(r'011(.*?)012', txt[idx0:]).span()

    value_0 = txt[idx0: idx1][len(
        '018.'): -len('011')].replace('\n', ' ').strip()
    value_1 = txt[idx0:][idx2: idx3][len(
        '011'): -len('012')].replace('\n', ' ').strip()

    key_ = '011_012'

    return {key_: value_0 + ' ' + value_1}


def cell_015(txt: str) -> Dict[str, str]:
    """
    """
    idx0, idx1 = re.search(r'015(.*?)Province', txt).span()

    key_ = '015'
    value_ = txt[idx0: idx1][len(
        '015'): -len('Province')].replace('\n', ' ').strip()

    return {key_: value_}


def cell_016(txt: str) -> Dict[str, str]:
    """
    """
    idx0, idx1 = re.search(r'016(.*?)Country', txt).span()

    key_ = '016'
    value_ = txt[idx0: idx1][len('015'): -len('Country')].strip()

    return {key_: value_}


def cell_017(txt: str) -> Dict[str, str]:
    """
    """
    idx0, idx1 = re.search(r'017(.*?)Mail', txt).span()

    key_ = '017'
    value_ = txt[idx0: idx1][len('015'): -len('Province')].strip()

    return {key_: value_}


def cell_018(txt: str) -> Dict[str, str]:
    """
    Zipcode
    """
    idx0, idx1 = re.search(r'ZIP code(.*?)Yes', txt).span()

    key_ = '018'
    value_ = txt[idx0: idx1][len('ZIP code'): -
                                 len('Yes')].replace('\n', ' ').strip()

    return {key_: value_}


def cell_040(txt: str) -> Dict[str, str]:
    """
    """
    cell_040_opts = {'1': 'Canadian-controlled private corporation (CCPC)',
                     '2': 'Other private corporation',
                     '3': 'Public corporation',
                     '4': 'Corporation controlled by a public corporation',
                     '5': 'Other corporation'}

    idx0, idx1 = re.search(r'tax year \((.*?) If the', txt).span()
    s_tmp = txt[idx0: idx1][len('tax year (tick one)  081'):
                            -len('If the')].strip()

    idx_x = s_tmp.find('X ')
    # to choose which one to return
    num_tmp = re.findall(r'\b\d\b', s_tmp[idx_x: idx_x + 5])[0]

    key_ = '040'
    value_ = cell_040_opts.get(num_tmp)

    return {key_: value_}


def cell_060(txt: str) -> Dict[str, str]:
    """
    """
    idx0, idx1 = re.search(
        r'Tax year start Year Month Day (.*?) 060', txt).span()

    key_ = '060'
    value_ = txt[idx0: idx1][len('Tax year start Year Month Day'):
                             -len('060')].replace('\n', ' ').strip()

    return {key_: value_}


def cell_061(txt: str) -> Dict[str, str]:
    """
    """
    idx0, idx1 = re.search(
        r'Tax year-end Year Month Day (.*?) 061', txt).span()

    key_ = '061'
    value_ = txt[idx0: idx1][len('Tax year-end Year Month Day'):
                            -len('061')].replace('\n', ' ').strip()

    return {key_: value_}


def check_pdf(file: str) -> None:
    """_summary_

    Args:
        file (str): _description_

    Returns:
        str: _description_
    """
    if '.pdf' not in file:
        
        raise argparse.ArgumentTypeError("Wrong format! Use a PDF file!!!")
    
    return file
    
    
def extract_t2(uploaded_file: str,
               save_csv: bool,
               save_json: bool,
               print_res: bool) -> None:
    
    """_summary_

    Returns:
        _type_: _description_
    """
    CELL_DICT = {'001': cell_BN,
            '002': cell_002,
            '011-012': cell_011_012,
            '015': cell_015,
            '016': cell_016,
            '017': cell_017,
            '018': cell_018,
            '040': cell_040,
            '060': cell_060,
            '061': cell_061}
    
    if uploaded_file is not None:
        
        try:
            
            today = date.today()
            
            text = extract_text(uploaded_file)
            text = text.replace('\n', ' ')
            
            file_name = uploaded_file.split('/')[-1].replace('.pdf', '')
            file_name_save = file_name + '_' + str(today)

            T2 = 'T2 Corporation Income Tax Return'

            form = T2 if T2 in text else 'Unkown form!'

            if form == T2:

                res_tmp = {}

                for k, v in CELL_DICT.items():

                    res_tmp[k] = v(text)

                df_tmp = pd.DataFrame(
                    [(list(v.keys())[0], list(v.values())[0]) for v in res_tmp.values()])
                df_tmp.columns = ['Cell', 'Cell Value']
                
                if print_res:
                    
                    print(df_tmp)
                    
                if save_csv:
                    
                    df_tmp.to_csv(file_name_save + '.csv')
                    
                    
                if save_json:
                    
                    df_tmp.to_json(file_name_save + '.json')
                
            else:
                
                print(f'Detected form: {form}')
            
        except:
            
            pass
        
    else:
        
        return 'Wrong file'

