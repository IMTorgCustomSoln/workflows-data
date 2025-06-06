#!/usr/bin/env python3
"""
Prepare all models used in workflow

Perform the following tasks:
* validate exact-term search items
* finetune models
* obtain results applyig system to test dataset
* log progress and results

"""
from src.Files import File

import torch

from pathlib import Path
import sys
import json

#from src.modules import config_env

#sys.path.append(Path('config').absolute().as_posix() )
from config._constants import (
    logger
)
#TODO: logger.info("Begin prepare_models")


def validate_key_terms(config, model_topic):
    """..."""
    wdir = config['TRAINING_DATA_DIR'][model_topic]
    path_pos_keywords = wdir / 'pos_kw.txt'  
    path_neg_keywords = wdir / 'neg_kw.txt'   
    if path_pos_keywords.is_file():
        pos_file = File(path_pos_keywords, 'txt')
        pos_kw = [line.rstrip() for line in pos_file.load_file(return_content=True)]
        logger.info(f'positive keywords found: {len(pos_kw)}')
    else:
        logger.info(f'no positive keywords found at path: {path_pos_keywords}')
    if path_neg_keywords.is_file():
        neg_file = File(path_neg_keywords, 'txt')
        neg_kw = [line.rstrip() for line in neg_file.load_file(return_content=True)]
        logger.info(f'negative keywords found: {len(neg_kw)}')
    else:
        logger.info(f'no negative keywords found at path: {path_neg_keywords}')
    return True


def finetune_classification_model(config, model_topic):
    """..."""

    #config_env.config()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f'finetune() using device: {device}')
    wdir = config['TRAINING_DATA_DIR'][model_topic]
    if not wdir.is_dir():
        logger.info(f'model data working dir is not available: {wdir}')
        return False

    #get records for train / test 
    from datasets import load_dataset, Dataset
    path_tng_records = wdir / 'train.json'
    path_tng_pos_sent = wdir / 'pos_sentence.txt'
    path_tng_neg_sent = wdir / 'neg_sentence.txt'
    path_test_records = wdir / 'test.json'
    file_paths = [
        path_tng_records,
        path_tng_pos_sent,
        path_tng_neg_sent,
        path_test_records
    ]
    checks = [path.is_file() for path in file_paths]
    if not all(checks):
        logger.info(f'no classification model data available, so no models trained')
        return True

    #load model
    from setfit import SetFitModel
    load_foundation_model_path = "BAAI/bge-small-en-v1.5"
    save_finetuned_model_path = f"pretrained_models/finetuned--BAAI-{model_topic}"
    if Path(save_finetuned_model_path).is_dir():
        logger.info(f'model is cached and previously refined: {save_finetuned_model_path}')
        return True
    model = SetFitModel.from_pretrained(load_foundation_model_path)
    model.to(device)
    model.labels = ["negative", "positive"]
    if path_tng_records.is_file():
        with open(path_tng_records, 'r') as file:
            train_records = json.load(file)['records']
        #train_dataset = load_dataset(records)         #<<<FAILS HERE, maybe use this: Dataset.from_dict(
    else:
        logger.info(f'no training records available to refine model: {path_tng_records}')
        return False
    
    if path_tng_pos_sent:
        with open(path_tng_pos_sent, 'r') as file:
            train_lines = file.readlines()
        recs = [{'text':line.replace('\n',''), 'label':'positive'} for line in train_lines]
        train_records.extend(recs)

    if path_tng_neg_sent.is_file():
        with open(path_tng_neg_sent, 'r') as file:
            train_lines = file.readlines()
        recs = [{'text':line.replace('\n',''), 'label':'negative'} for line in train_lines]
        train_records.extend(recs)
    train_dataset = Dataset.from_list(train_records)        #[:10])     #<<<for testing

    if path_test_records.is_file():
        with open(path_test_records, 'r') as file:
            test_records = json.load(file)['records']
        test_dataset = Dataset.from_list(test_records)

    #train model
    from setfit import Trainer, TrainingArguments
    args = TrainingArguments(
        batch_size=25,
        num_epochs=10,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
    )
    trainer.train()

    #test model
    metrics = trainer.evaluate(test_dataset)
    print(metrics)
    '''
    preds = model.predict([
        "I got the flu and felt very bad.",
        "I got a raise and feel great.",
        "This bank is awful.",
        ])
    print(f'predictions: {preds}')
    '''

    #save model
    model_path = Path(save_finetuned_model_path)
    model.save_pretrained(model_path )
    model2 = SetFitModel.from_pretrained(model_path )
    result = True
    if not model2:
        result = False
    return result