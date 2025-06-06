
from src.modules.parse_ediscovery.loadfile import (
    collect_workspace_files,
    copy_dat_file_with_fixed_format,
    get_linux_path_from_windows,
    complete_path
)

import pandas as pd
from pathlib import Path


REQUIRED_FIELDS = {
    'documentId', 'groupId', 'custodian', 
    'fileName', 'sentDt',
    'subject', 'from', 'to', 'cc', 'textLink'
    }





def combine_dats_to_pickle():
    p_home = Path(__file__).parent / 'data_ediscovery/extended_layout'
    dat_index = collect_workspace_files(p_home)

    df = pd.DataFrame()
    for vol in dat_index:
        dat = dat_index[vol]['dat']
        new_file = dat.parent / 'new_utf8_file.mdat'
        tmp_df = copy_dat_file_with_fixed_format(
            bom_file=dat,
            new_file=new_file,
            separator_str='|',
            remove_chars=[],
            new_separator='\x14',
            return_df=True
        )
        tmp_df['textLink'] =  tmp_df['textLink'].apply( 
            lambda x: complete_path(x, dat_index[vol]['text_dir'])
            )
        tmp_df['nativeLink'] = tmp_df['nativeLink'].apply( 
            lambda x: complete_path(x, dat_index[vol]['native_dir'])
            )
        tmp_df['srcFile'] = vol
        df = pd.concat([df, tmp_df], axis=0)
    df.reset_index(inplace=True, drop=True)
    #df['sentDt'] = pd.to_datetime(df['SentDate'] + ' ' + df['SentTime'])
    df['sentDt'] = pd.to_datetime(df['Date Sent'])
    
    col_set = set(df.columns.to_list())
    missing_fields = REQUIRED_FIELDS.difference(col_set)
    assert missing_fields.__len__() == 0

    fl = p_home / 'combined_dats.pickle'
    df.to_pickle(fl)
    return True