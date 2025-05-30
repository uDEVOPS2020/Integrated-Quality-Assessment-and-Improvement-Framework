from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_dataset
from transformers import DataCollatorForSeq2Seq
from transformers import AutoTokenizer
import evaluate
import numpy as np
import Levenshtein




# Load the dataset
dataset = load_dataset("json", data_files={"train": "dataset/training_set.json"})


# Mapping to change service name with a letter
mapping = { 'carts': 'A','payment': 'B', 'shipping': 'C', 'user': 'D'} # Mapping used for SockShop

# Transform the services sequence in a sequence of letter according to the mapping
def find_unique_services(a):
    result = ""
    next_letter = 'A'
    
    # Extract the string from the JSON
    string = a["label"]
    elements = string.split('--')

    for element in elements:
        result += mapping[element] + '--'

    # Remove the last ' ' extra
    result = result[:-2]
    
    a["label"] = result
    

    return a

# Split the dataset in training and testing
dataset = dataset["train"].train_test_split(test_size=0.1)

#
# PREPROCESS
#
checkpoint = "t5-small"
tokenizer = AutoTokenizer.from_pretrained(checkpoint, fast=True)

source_lang = "raw_logs"
target_lang = "label"
prefix = "translate raw_logs to label:"

# Generate the tokenizer considering the source data and target data
# The prefix is needed to let the trasformer understand that the task is traslation
def preprocess_function(examples):
    inputs = [prefix + example for example in examples[source_lang]]
    targets = [example for example in examples[target_lang]]
    model_inputs = tokenizer(inputs, text_target=targets, max_length=1024, truncation=True)
    return model_inputs

# Subsititue the name of services with letters in the label column
tokenized_dataset = dataset.map(find_unique_services)

# Perform the tokenization on the entire dataset
tokenized_dataset = tokenized_dataset.map(preprocess_function, batched=True)

# Remove the label column from the tokenized dataset
tokenized_dataset = tokenized_dataset.remove_columns("label")


# Data collators are objects that will form a batch by using a list of dataset elements as input.
# These elements are of the same type as the elements of train_dataset or eval_dataset.
# DataCollatorForSeq2Seq will dynamically pad the inputs received, as well as the labels.
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=checkpoint)


#
# EVALUATE
#

# Edit distance used for evaluation
def compute_edit_distance(eval_preds):
    preds, labels = eval_preds

    # Calculate the edit distance for each pair of predictions and labels
    edit_distances = [Levenshtein.distance(pred, label) for pred, label in zip(preds, labels)]

    # Calculate the average edit distance
    avg_edit_distance = sum(edit_distances) / len(edit_distances)

    # Return the average edit distance as the evaluation metric
    result = {"edit_distance": avg_edit_distance}

    return result

#
# TRAINING
#
model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint, device_map='balanced')

# Define training hyperparameters
training_args = Seq2SeqTrainingArguments(
    output_dir="model",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=18,
    predict_with_generate=True,
    fp16=True,
    push_to_hub=False,
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_edit_distance,
)

# Finetuning
trainer.train()
trainer.save_model("nuovo_pretrained_model")



