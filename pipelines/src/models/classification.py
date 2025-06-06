#!/usr/bin/env python3
"""
Module Docstring

"""

#TODO:from nltk.tokenize import word_tokenize 

import torch
#from transformers import AutoModel
from setfit import SetFitModel

from pathlib import Path
import copy


#load models
#config_env.config()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_path = Path("BAAI/bge-small-en-v1.5")
model = SetFitModel.from_pretrained(model_path)
model.to(device)




class Classifier:
    """..."""
    def __init__(self):
        pass
    
    def config(self, config):
        self.config = copy.deepcopy(config)
        self.models = [
            kw_classifier,
            phrase_classifier,
            #fs_classifier
        ]
        kw_lines = []
        for model_topic, data_dir in self.config['TRAINING_DATA_DIR'].items():
            with open( data_dir / 'pos_kw.txt', 'r') as file:
                kw_lines.extend( file.readlines() )
        self.config['KEYWORDS'] = [ ' ' + word.replace('\n','') + ' ' for word in kw_lines]      #ensure spacing around word
        
    def run(self, chunk):
        """Importable function to run assigned models."""
        result = []
        for model in self.models:
            result.append( model(self.config, chunk) )
        return result
    

TextClassifier = Classifier()



def kw_classifier(config, chunk):
    """Apply key word classifier to chunk."""
    result = {
        'search': 'KW',
        'target': None,
        'timestamp': None,
        'pred': None
        }
    hits = []
    for word in config['KEYWORDS']:
        word = word.strip()
        if word in chunk['text'].lower():
            hits.append(word)
    #words = word_tokenize(chunk['text'])
    if len(hits)>0:
            result['target'] = hits[0]       #TODO: provide formatted chunk['text'], previously: `' '.join(hits)`
            result['pred'] = len(hits) / len(chunk['text'])
            if 'timestamp' in chunk.keys():
                result['timestamp'] = chunk['timestamp']
            return result
    else:
        return None
    

def phrase_classifier(config, chunk):
    """Apply phrase classifiers to chunk."""
    return None


def fs_classifier(config, chunk):
    """Apply fs classifier to chunk."""
    result = {
        'search': 'FS',
        'target': None,
        'timestamp': None,
        'pred': None
        }
    if len(chunk['text']) > 40:
        probs = model.predict_proba(chunk['text'])
        pos_idx = model.labels.index('positive')
        prob_positive = probs.tolist()[pos_idx]
        if prob_positive > .5:
            result['target'] = chunk['text']
            result['pred'] = prob_positive
            if 'timestamp' in chunk.keys():
                result['timestamp'] = chunk['timestamp']
            return result
    return None