#!/usr/bin/env python3
"""
StyledText singleton class with static methods for
exported text with style (font color, bold, etc.)
in different mediums.
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


#from IPython.display import display
#from IPython.core.display import HTML
import copy

import pandas as pd

from pathlib import Path






class StyledText:
    """Singleton with static methods for displaying / exported
    styled text.
    """


    def __init__(self):
        pass

    '''
    def text_to_notebook_output(text, highlighted_index=[()], verbose=False, jupyter=True):
        """Output text as styled html for use in jupyter notebook.

        txt = "This is a long sentence."
        text_to_notebook_output(txt,[(5,7),(8,9),(15,23)], True)

        <z style="color: gray;" >This <b style="color: black;">is</b> <b style="color: black;">a</b> long <b style="color: black;">sentence</b>.</z>
        This is a long sentence.
        """
        def wrap_text_in_tag(txt, tag):
            close1 = tag.split('<')[1]
            close2 = close1.split()[0] + '>' if ' ' in close1 else close1
            return tag + txt + '<' + tag.split('<')[0] + '/' + close2

        highlight_tag = '<b style="color: black;">'
        background_tag = '<z style="color: gray;" >'    #jupyter uses `div` so we can't use that tag

        text_sections = []
        mod_highlighted_index = copy.deepcopy(highlighted_index[:1])
        highlighted_index.append((len(text),len(text)))
        start = 0
        l = 0

        #prepare indices for changes to text position
        if len(highlighted_index)>1:
            for idx in highlighted_index[1:]:
                sub = text[start:idx[0]]
                start = idx[0]
                text_sections.append(sub)
                l = l + len(sub)
                mod_highlighted_index.append( (idx[0]-l, idx[1]-l) )    #<<< account for multiple text_sections
        else:
            mod_highlighted_index = highlighted_index
        mod_highlighted_index.pop(len(highlighted_index)-1)

        #append individual text pieces
        recs = []
        for idx, idx_grp in enumerate(mod_highlighted_index):
            sub_text = text_sections[idx]
            begin = sub_text[:idx_grp[0]]
            center = wrap_text_in_tag(sub_text[idx_grp[0]:idx_grp[1]], highlight_tag)
            end = sub_text[idx_grp[1]:]

            new_sub_text = begin + center + end
            recs.append(new_sub_text)

        sub_text = ('').join(recs)
        result = wrap_text_in_tag(sub_text, background_tag)

        if verbose:
            print(result)
        if jupyter:
            return display(HTML(result))
        else:
            return result
    '''

    def df_to_xlsx(df, output_path='./tests/tmp/TEST.xlsx', text_column='data', label_index_column='label', verbose=False):
        """Dataframe to xlsx workbook with Rich String Formatting around individual text.

        This is typically used from data exported from Doccano labeling application.

        TODO:text with overlapping highlighted indices will fail.
        """
        #supporting function
        def transform(workbook, result_obj, text_column='data'):
            """Transform the text record's result_obj into a list of Format(ted) text.
            """
            normal = workbook.add_format({'color': '#737880'})
            bold_red = workbook.add_format({'color': '#b41b1b', 'bold': True})
            #bold_blue = workbook.add_format({'color': '#005fcf', 'bold': True})

            text = result_obj[text_column]
            highlighted_index = copy.deepcopy(result_obj['label'])  

            highlight_tag = bold_red
            background_tag = normal

            #prepare indices
            mod_highlight_index = []
            l = len(highlighted_index)
            if l<1:
                highlighted_index.append([0,1,None])
                l=1
            for idx, item in enumerate(highlighted_index):
                if idx==0 and idx==l-1:
                    start=0
                    end=len(text)
                elif idx==0:
                    start=0
                    end=highlighted_index[idx][1]
                elif idx==l-1:
                    ml = len(mod_highlight_index)
                    start = mod_highlight_index[ml-1][0]
                    end = len(text)    #highlighted_index[idx][1]                
                else:
                    ml = len(mod_highlight_index)
                    start=mod_highlight_index[ml-1][0]
                    end=highlighted_index[idx][0]

                sub_index = [start,item[0], None], item, [item[1],end, None]
                mod_highlight_index.extend( sub_index )

            #prepare text substrings from indices
            result = []
            for idx, index in enumerate(mod_highlight_index):
                if index[2]=='True':
                    result.append(highlight_tag)
                    result.append( text[index[0]: index[1]] )
                else:
                    result.append(background_tag)
                    result.append( text[index[0]: index[1]] )

            #text formatting for excel
            missing_indices = [idx for idx, item in enumerate(result) if item=='']
            rm_missing_indices = []
            for idx in missing_indices:
                rm_missing_indices.append(idx-1) 
                rm_missing_indices.append(idx) 
            result_dups_removed = [item for idx, item in enumerate(result) if idx not in rm_missing_indices]

            return result_dups_removed


        #prerequisites
        df = df.copy(deep=True)
        col_list = df.columns.tolist()
        output_file = Path(output_path)
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        writer.book.use_zip64()

        #xlsxwriter workbook and worksheet objects
        workbook  = writer.book
        worksheet = workbook.add_worksheet('Sheet1')

        #formatting
        header_format = workbook.add_format({'bold': True, 
                                            'align': 'center',
                                            'valign': 'center' 
                                            })
        data_column_width = 75
        column_format = workbook.add_format({'text_wrap': True,
                                             'align': 'left',
                                             'valign': 'top'
                                            })
        
        #column headers with the defined format
        for p in range(len(col_list)):
            worksheet.set_column(1, p, 10, column_format)
            worksheet.write(0, p, col_list[p].capitalize(), header_format)
            
        data_column_index = col_list.index(text_column)
        worksheet.set_column(1, data_column_index, data_column_width, column_format)

        # Write the cell values for body
        transform_results = []
        for i, row in enumerate(df.to_dict('records')):
            for j, (col, val) in enumerate(row.items()):
                if col==text_column:
                    result = transform(workbook, row,  text_column)
                    if verbose:
                        reprs = []
                        for item in result:
                            tmp = item if type(item)==str else str(type(item))
                            reprs.append(tmp)
                        str_result = '|'.join(reprs)
                        transform_results.append(str_result)
                    worksheet.write_rich_string(i+1, j, *result)
                else:
                    try:
                        worksheet.write(i+1, j, val)
                    except:
                        pass

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()
        return transform_results
