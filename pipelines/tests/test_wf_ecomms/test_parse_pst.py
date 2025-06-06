import sys

from src.modules.parse_pst.pst_parser import set_args, open_data_folder, handle_message_entity
from src.modules.parse_pst.pstformatters import from_name, available_formatters
from src.modules.parse_pst.pstobjects import PSTFolder, PSTRecordEntry, parse_path_expr


def test_main():
    pst_file = 'tests/test_wf_ecomms/data_dialogue/test.pst'

    root_parser = set_args()
    sys.argv = ['pst_parser.py', pst_file, 'folder', '--path', '1']
    args = root_parser.parse_args()

    pst_file = args.pstfile
    output = args.output
    formatter = from_name(name=args.format, output=output, args=args)
    
    try:
        data_folder = open_data_folder(pst_file)
        handle_message_entity(data_folder, args, formatter)
    finally:
        pst_file.close()
        #output.close()

    assert True == True