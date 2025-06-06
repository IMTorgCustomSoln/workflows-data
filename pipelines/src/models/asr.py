#!/usr/bin/env python3
"""
Module Docstring

"""

__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


import torch

import os
from pathlib import Path
import json
import time




def run_workflow(config, sound_files, intermediate_save_dir=None, infer_text_classify_only=False):
    """..."""
    #env
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    config['LOGGER'].info(f'asr using device: {device}')

    #prepare data
    from datasets import Dataset, Audio
    sound_filepath_strings = [str(file) for file in sound_files if file != None]

    if not infer_text_classify_only:
        #transcribe sample
        from transformers import pipeline
        from transformers.pipelines.pt_utils import KeyDataset

        audio_dataset = Dataset.from_dict({'audio': sound_filepath_strings}).cast_column('audio', Audio())

        asr_pipeline = pipeline(
            task='automatic-speech-recognition', 
            model='openai/whisper-base',
            device=device,
            generate_kwargs={"language": "english"},
            )
        #TODO: Whisper did not predict an ending timestamp,[ref](https://github.com/huggingface/transformers/issues/23231)
        """
        sample = audio_dataset[0]['audio']
        dialogues = asr_pipeline(
            inputs=sample.copy(),
            generate_kwargs={'max_new_tokens': 256},
            return_timestamps=True
            )
        """
        dialogues = []
        gen = asr_pipeline(KeyDataset(audio_dataset, 'audio'), 
                           #generate_kwargs={'max_new_tokens': 256}, 
                           return_timestamps=True,
                           chunk_length_s=30        #batch processing of single file, [ref](https://huggingface.co/blog/asr-chunking)
                           )
        for idx, file in enumerate( gen ):
            file_path = audio_dataset[idx]['audio']['path']
            file_name = os.path.basename( file_path )
            sampling_rate = audio_dataset[idx]['audio']['sampling_rate']
            record = {
                'file_name': file_name,
                'file_path': file_path, 
                'sampling_rate': sampling_rate, 
                'chunks': file['chunks'],
                'time_asr': time.time() - config['START_TIME']
                }
            config['LOGGER'].info(f'asr-processing completed for file {idx} - {file_name}')
            dialogues.append(record)
    
    else:
        dialogues = []
        for file in sound_files:
            with open(file, 'r') as f:
                dialogue = json.load(f)
                dialogues.append(dialogue)

    '''
    #run classification models on each: chunk,item
    from src.models.classification import classifier

    for idx, dialogue in enumerate(dialogues):
        dialogues[idx]['classifier'] = []
        for chunk in dialogue['chunks']:
            results = classifier(chunk)
            for result in results:
                if result != None:
                    dialogues[idx]['classifier'].append(result)
                else:
                    dialogues[idx]['classifier'].append({})
        dialogues[idx]['time_textmdl'] = time.time() - config['START_TIME']
        config['LOGGER'].info(f'text-classification processing for file {idx} - {dialogue["file_name"]}')
    '''
               

    #save
    from src.io import export

    save_json_paths = []
    if intermediate_save_dir:
        for idx, dialogue in enumerate(dialogues):
            save_path = Path(intermediate_save_dir) / f'{dialogue["file_name"]}.json'
            try:
                with open(save_path, 'w') as f:
                    json.dump(dialogue, f)
                save_json_paths.append( str(save_path) )
                config['LOGGER'].info(f'saved intermediate file {idx} - {save_path}')
            except Exception as e:
                print(e)
            #TODO:   dialogues.extend(processed_dialogues)   #combine records of previously processed dialogues
            
    return save_json_paths