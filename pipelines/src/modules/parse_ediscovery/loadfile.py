import pandas as pd

from typing import List
import click
from colorama import Fore, init as init_colorama
import chardet
import re
import csv
import pathlib
import json
import sys
import io

from pathlib import PureWindowsPath, PurePosixPath, Path
from itertools import chain

init_colorama()


ASCII_MATCH = re.compile("[a-zA-Z0-9]")


def collect_workspace_files(cwdir):
    """Collect all relevant files, from all volumes, within a working directory."""
    base_dirs = [dir for dir in cwdir.iterdir() if dir.is_dir()]
    #add modification of .dat files
    data_index = {}
    for dirTgt in base_dirs:
        record = {}
        dats = [file for file in dirTgt.rglob('**/*.dat')]
        if len(dats)==1:
            record["dat"] = dats[0]
        else:
            raise Exception
        mdats = [file for file in dirTgt.rglob('**/*.mdat')]
        if len(mdats)==1:
            record["mdat"] = mdats[0]
        else:
            record["mdat"] = None
        native_dir = [dir for dir in dirTgt.rglob('**/*') if (dir.is_dir() and dir.stem=='NATIVES')]
        if len(native_dir)==1:
            record["native_dir"] = native_dir[0]
        else:
            raise Exception
        text_dir = [dir for dir in dirTgt.rglob('**/*') if (dir.is_dir() and dir.stem=='TEXT')]
        if len(text_dir)==1:
            record["text_dir"] = text_dir[0]
        else:
            raise Exception
        data_index[dirTgt.stem] = record
    return data_index


def get_linux_path_from_windows(win_path):
        if '\\' not in win_path:
            return win_path
        else:
            posix = str(PurePosixPath(PureWindowsPath(win_path)))
            return posix


def complete_path(p, vol_p):
    vol_key = vol_p.name
    lin_p = Path( get_linux_path_from_windows(p) )
    idx = lin_p.parents._parts.index(vol_key)
    end_path = '/'.join(lin_p.parents._parts[idx+1:])
    whole_path = vol_p / end_path
    return whole_path


def validate_files(
        dat_filepath,
        home_dirpath
        ):
    """Validate ediscovery file package.


    * Do files referend to by .dat links exist?
    *   ?Do the line counts match? ie: Documents = .dat; Pages = .opt
    *   ?Do the number of rows in the DAT match the number of files loaded? ie: .dat == VOL /IMAGES, /NATIVES, /TEXT
    * Do all msg documents have text? (If not, image and OCR)?
    * Is metadata reasonable?
    * Do the Custodian counts appear correct?

    TODO:make diagrammatic explanation of structure
    """
    checks = {}
    #load
    dfdat = get_table_rows_from_dat_file(dat_filepath, 'df', '\x14')
    dfdat['nativeExtension'] = dfdat['nativeLink'].map(lambda x: Path(x).suffix if type(x)==str else '')
    dat_rows = dfdat.to_dict('records')
    dfmsg = dfdat[dfdat['nativeExtension']=='.msg']


    #checks

    #unique values
    custodian_count = dfdat['custodian'].unique().tolist().__len__()
    check_custodian = custodian_count > 0
    checks['unique custodian'] = check_custodian

    doc_count = dfdat['documentID'].unique().tolist().__len__()
    msg_ext_count = dfmsg.shape[0]
    check_msg_count = doc_count >= msg_ext_count
    checks['unique msg_count'] = check_msg_count

    #parentids refer back to groupids
    lgroupids = dfdat['groupID'].unique().tolist()
    parentid_referenced = []
    parentids = dfdat['parentDocumentID'].dropna().tolist()
    for parentid in parentids:
        if parentid in lgroupids:
            parentid_referenced.append(parentid)
    check_parent_ids = len(parentid_referenced) == len(parentids)
    checks['parent ids'] = check_parent_ids

    #missing values
    subject_count = dfdat['subject'].unique().tolist().__len__()
    subject_not_missing = dfmsg[pd.isna(dfmsg['subject'])==False].shape[0]
    check_subject = subject_count >= subject_not_missing
    checks['missing subject'] = check_subject

    from_count = dfdat['from'].unique().tolist().__len__()
    from_not_missing = dfmsg[pd.isna(dfmsg['from'])==False].shape[0]
    check_from = from_count >= from_not_missing
    checks['missing from'] = check_from

    to_count = dfdat['to'].unique().tolist().__len__()
    to_not_missing = dfmsg[pd.isna(dfmsg['to'])==False].shape[0]
    check_to = to_count >= to_not_missing
    checks['missing to'] = check_to

    cc_count = dfdat['cc'].unique().tolist().__len__()
    cc_not_missing = dfmsg[pd.isna(dfmsg['cc'])==False].shape[0]
    check_cc = cc_count >= cc_not_missing
    checks['missing cc'] = check_cc

    #TEXT - message text
    text_dirpath = home_dirpath / 'TEXT'
    if text_dirpath.is_dir():
        txt_file_content = get_nested_dirs_files_lines(text_dirpath)
        extxt_files = set( [pathlib.Path(get_linux_path_from_windows(doc['textLink'])).stem for doc in dat_rows] )
        txt_paths = set( [pathlib.Path(txt).stem for txt in list(txt_file_content.keys())] )
        diff = extxt_files.difference(txt_paths)
        check_file_diff =  len(diff) == 0
        checks['file_diff text'] = check_file_diff

    #NATIVE - message files (.msg, attachments, etc.)
    native_dirpath = home_dirpath / 'NATIVES'
    if native_dirpath.is_dir():
        native_files = get_file_names(native_dirpath)
        dat_paths = [ str(pathlib.Path(get_linux_path_from_windows(doc['nativeLink']))) for doc in dat_rows if type(doc['nativeLink'])==str]
        native_paths = [str(file) for file in native_files]
        files_exist = []
        for dat_path in dat_paths:
            for txt_path in native_paths:
                if dat_path in txt_path:
                    files_exist.append(dat_path)
                else:
                    continue
        check_path_diff =  len(files_exist) == len(dat_paths)
        checks['file_diff native'] = check_file_diff

    return checks


def copy_dat_file_with_fixed_format(
    bom_file, 
    new_file, 
    separator_str='', 
    remove_chars=[], 
    new_separator='\x14', 
    rename_fields={
        #document control and source
        'Control Number':'documentId', 'DocID':'documentId',
        'Custodian':'custodian', 'All Custodians':'allCustodians', 'AllCustodians':'allCustodians', 
        #groupid
        'Group Identifier': 'groupId', 'groupID': 'groupId', 'GroupIdentifier': 'groupId', 
        'Parent Document ID': 'parentDocumentId', 'ParentID': 'parentId',
        #attachments
        'number of attachments': 'numberOfAttachments', 'Attachment ID':'attachmentId', 'AttachmentID':'attachmentId', 
        #doc / file info
        'Document Extension': 'documentExtension', 'Filename': 'fileName', 'filename': 'fileName', 'Filesize':'fileSize', 
        'Page Count':'pageCount', 'PageCount':'pageCount', 
        #msg info
        'Email Subject': 'emailSubject','EmailSubject': 'emailSubject',  'Subject':'subject',
        'Email From': 'from', 'Email To': 'to', 'Email CC': 'cc',
        'From':'from', 'To':'to', 'CC':'cc',
        #references
        'Extracted Text':'textLink', 'FILE_PATH':'nativeLink', 'TextLink':'textLink', 'NativeLink':'nativeLink'
        },
    return_df=True
    ):
    """Copy the dat file (in utf-8 with BOM format) to a new file using utf-8 only encoding.

    __Note:__ typical ediscovery separator characters include: thorn (þ) and pilcrow (\x14 or ¶)

    __Usage:__
    ```
    >>> original_file = dirHome / ''
    >>> new_file = dirHome / 'new_file.dat'
    >>> fields = {'Group Identifier': 'groupID'}
    >>> copy_dat_file_with_fixed_format(original_file, new_file, 'þ\x14þ', ['þ'], fields)
    >>> df = pd.read_csv(new_file, sep='\x14')
    ```
    """
    s = open(bom_file, mode='r', encoding='utf-8-sig').read()
    s = s.replace(separator_str, new_separator)
    if len(remove_chars) > 0:
        for char in remove_chars:
            s = s.replace(char, '')
    open(new_file, mode='w', encoding='utf-8').write(s)
    try:
        dfdat = pd.read_csv(new_file, sep=new_separator)
        dfdat.rename(columns=rename_fields, inplace=True)
        dfdat.to_csv(new_file, sep=new_separator, index=False)
    except Exception as e:
        scols = set(dfdat.columns)
        snew_cols = set(rename_fields.keys())
        col_keys_not_available_in_dat_file = snew_cols.difference(scols)
        print('dfdat columns not available')
        print(col_keys_not_available_in_dat_file)
        print('dfdat columns')
        print(dfdat.columns)
        print(e)
    if return_df:
        return dfdat
    else:
        return True



def get_file_names(dir_path):
    """..."""
    p_dir_path = pathlib.Path(dir_path)
    if p_dir_path.is_dir():
        files = [item for item in p_dir_path.glob('**/*') if item.is_file()]
    else:
        raise TypeError
    return files


def get_file_lines(file_path):
    """..."""
    if pathlib.Path(file_path).is_file():
        lines = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
    else:
        raise TypeError
    return lines


def get_nested_dirs_files_lines(dir_path):
    """..."""
    files_lines = {}
    try:
        if pathlib.Path(dir_path).is_dir():
            dirs = [dir for dir in dir_path.iterdir() if dir.is_dir()]
            for dir in dirs:
                files = [file for file in dir.iterdir() if file.is_file()]
                for file_path in files:
                    try:
                        with open(file_path, 'r') as f:
                            file_lines = f.readlines()
                            files_lines[str(file_path)] = file_lines
                    except Exception as e:
                        print(e)
    except:
        raise TypeError
    return files_lines


def get_encoding(filepath) -> str:
    with open(filepath, "rb") as readfile:
        raw = readfile.read()
    det = chardet.detect(raw)
    return det["encoding"]


def get_lines(filepath, encoding) -> List[str]:
    try:
        with open(filepath, encoding=encoding, errors="backslashreplace") as txt_file:
            lines: List[str] = list(txt_file.readlines())
        return lines
    except UnicodeDecodeError as e:
        click.echo(f"Error decoding {filepath}: {e}")
    raise Exception("Could not parse file")


def remove_empty_lines(lines):
    new_lines = []
    for line in lines:
        if len(line) > 1:
            new_lines.append(line)
    return new_lines


def get_table_rows_from_dat_file(dat_file, type='rows', sep='\x14', rename_fields={}):
    """Get table rows from .dat file (leverage pandas).

    __Usage__
    ```
    >>> dat_rows = get_table_rows_from_dat_file(dat_filepath)
    ```
    """
    df = None
    dat_file = pathlib.Path(dat_file)
    if dat_file.is_file():
        df = pd.read_csv(dat_file, sep=sep, encoding='utf-8')
    df.rename(columns=rename_fields, inplace=True)
    df['textLink'] = df['textLink'].apply(get_linux_path_from_windows)
    df['nativeLink'] = df['nativeLink'].apply(get_linux_path_from_windows)
    if type == 'rows':
        return df.to_dict('records')
    if type == 'df':
        return df


def get_table_rows_from_lines(lines, field_list_or_first_row_header=[]):
    """Get table rows from .dat from ingested lines (BASIC CODE).

    __Usage__
    ```
    >>> dat_lines = get_file_lines(dat_filepath)
    >>> dat_rows = get_table_rows(dat_lines)
    ```
    """
    #support
    def split_cells_on_chars(ln):
        chars = ["þþ", "þ\x14þ", "þ\n", "þ", "|", "\n"]
        tmp_line = [ln]
        idx = 0
        while len(tmp_line) == 1 and idx < len(chars):
            nested_list = [item.split(chars[idx]) for item in tmp_line]
            tmp_line = list(chain(*nested_list))
            idx = idx + 1
            if idx == len(chars):
                raise TypeError
        
        if len(tmp_line) > 1:
            for char in chars:
                tmp_line = [item.strip(char) for item in tmp_line]
        
        return tmp_line

    #main
    new_lines = []
    for line in lines:
        new_line = split_cells_on_chars(line)
        new_line = [i.strip("þ") for i in new_line]
        new_line = [i.strip("þ\n") for i in new_line]
        new_line = [i.strip("|") for i in new_line]
        cell_per_line = len(new_line)
        assert cell_per_line > 1
        new_lines.append(new_line)
    new_lines = remove_empty_lines(new_lines)
    assert all([len(l) == cell_per_line for l in new_lines])

    if field_list_or_first_row_header==[]:
        fields = new_lines.pop(0)
    else:
        fields = field_list_or_first_row_header
    rows = []
    for line in new_lines:
        row = {}
        for i, field_name in enumerate(fields):
            row[field_name] = line[i]
        rows.append(row)

    assert len(rows) == len(new_lines)
    return rows


def make_csv(rows, filepath: pathlib.Path):
    with open(str(filepath), "wt") as writefile:
        writer = csv.DictWriter(writefile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def make_json(cells, filepath: pathlib.Path):
    with open(str(filepath), "wt") as writefile:
        write_text = json.dumps(cells, sort_keys=True, indent=4)
        writefile.write(write_text)


@click.command()
@click.argument("source")
@click.argument("dest")
@click.option(
    "-j",
    "--json",
    is_flag=True,
    help="Whether to convert to JSON, rather than CSV (the default)",
)
def loadfile(source, dest, json):
    """
    Converts a .DAT formatted loadfile to CSV or JSON.

    SOURCE: the the file you wish to convert

    DEST: the directory where the converted file will be created.

    The converted file will have the same name as the original file, with either .csv or
    .json added at the end.
    """

    src_path: pathlib.Path = pathlib.Path(source)
    if json:
        dest_path = pathlib.Path(dest) / f"{src_path.name}.json"
    else:
        dest_path = pathlib.Path(dest) / f"{src_path.name}.csv"
    if src_path.is_file():
        enc = get_encoding(src_path)
        lines = get_lines(src_path, enc)
        rows = get_table_rows(lines)
        if json:
            make_json(rows, dest_path)
        else:
            make_csv(rows, dest_path)
        click.echo(Fore.GREEN + f"Success: output saved to {dest_path}")
    else:
        click.echo(Fore.RED + f"Oops, {source} is a directory")


if __name__ == "__main__":
    loadfile()
