from datasets import load_dataset, disable_caching
from transformers import AutoTokenizer
from torch.utils.data import DataLoader
from typing import Union, List
import tqdm
import torch
import random
import copy
import re
import pytorch_lightning as pl

# disable_caching()

class PretrainDataModule(pl.LightningDataModule):
    """
    data module for pre-training tasks
    pre-training data loader has columns: input_ids, token_type_ids, attention_mask, labels
    """

    task_text_field_map = {
        "cr": ["sentence"],
        "bcr": ["sentence", "concept"],
        "ceg": ["sentence", "concept"],
    }

    loader_columns = [
        "datasets_idx",
        "input_ids",
        "token_type_ids",
        "attention_mask",
        "start_positions",
        "end_positions",
        "labels",
    ]

    def __init__(self, model_name_or_path: str,
                 train_dataset_path: Union[str, List], task_name: str,
                 eval_dataset_path: str = None, test_dataset_path: str = None,
                 max_seq_length: int = 512, train_batch_size: int = 32,
                 eval_batch_size: int = 32, num_workers: int = 0):
        print(f"initializing concept recognition data module")
        super().__init__()

        self.model_name_or_path = model_name_or_path
        self.train_dataset_path = train_dataset_path
        self.task_name = task_name
        self.max_seq_length = max_seq_length

        self.train_batch_size = train_batch_size
        self.text_fields = self.task_text_field_map[task_name]
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path,
                                                       use_fast=True)
        self.num_workers = num_workers

    def setup(self, stage: str):
        self.dataset = load_dataset("csv", data_files={"train": self.train_dataset_path})
        for split in self.dataset.keys():
            self.dataset[split] = self.dataset[split].map(
                self.convert_to_features,
                batched=True,
            )
            self.columns = [c for c in self.dataset[split].column_names if
                            c in self.loader_columns]
            self.dataset[split].set_format(type="torch", columns=self.columns)


    def prepare_data(self):
        self.dataset = load_dataset("csv",
                                    data_files={"train": self.train_dataset_path})
        AutoTokenizer.from_pretrained(self.model_name_or_path, use_fast=True)

    def train_dataloader(self):
        return DataLoader(self.dataset["train"], batch_size=self.train_batch_size,
                          shuffle=True, num_workers=self.num_workers)

    def convert_to_features(self, example_batch, indices=None):
        # Either encode single sentence or sentence pairs
        if len(self.text_fields) > 1:
            texts_or_text_pairs = list(zip(example_batch[self.text_fields[0]],
                                           example_batch[self.text_fields[1]]))
        else:
            texts_or_text_pairs = example_batch[self.text_fields[0]]

        # Tokenize the text/text pairs
        features = self.tokenizer.batch_encode_plus(texts_or_text_pairs,
                                                    max_length=self.max_seq_length,
                                                    padding='max_length',
                                                    truncation=True)

        # Rename label to labels to make it easier to pass to model forward

        features["labels"] = example_batch["label"]

        return features
