import argparse
from pydantic import BaseModel

from ast import literal_eval

from extraction_tools import *
from pymodels import *

# =============================================================

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description = "")
    
    # Add arguments
    parser.add_argument('--input_file', help = "Input file path", type = check_pdf)
    parser.add_argument('--print_res', help = "Print results", type = str)
    parser.add_argument('--save_csv', help = "Save results [csv]", type = str)
    parser.add_argument('--save_json', help = "Save results [json]", type = str)
    
    args = parser.parse_args()
        
    input_file = args.input_file
    
    save_json = args.save_json
    save_json_bool = literal_eval(save_json)
    
    save_csv = args.save_csv
    save_csv_bool = literal_eval(save_csv)
    
    print_ = args.print_res
    print_bool = literal_eval(print_)
    
    extract_t2(input_file, save_csv_bool, save_json_bool, print_bool)
    print('Done!')
    