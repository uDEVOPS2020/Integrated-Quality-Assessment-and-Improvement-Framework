#
# Inference
#
from transformers import pipeline
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM
from datasets import load_dataset
import numpy as np
import transformers as tr
import Levenshtein
import csv
import sys
import json


# Load the dataset
dataset = load_dataset("json", data_files={"train": "dataset/test_set.json"})

# Get the unique labels
def find_unique_labels(dataset):
    labels = []
    for val in dataset:

        # Extract the labels from the dataset
        data_string = dataset[val]["label"]

        # Remove the duplicated labels, keeping the order of appearance
        labels = list(dict.fromkeys(data_string))

    return labels

# Get the unique labels from the dataset
temp_list = find_unique_labels(dataset)

f = open('similarity.csv', 'w')
writer = csv.writer(f)
writer.writerow(['sample', 'label_distance', 'similarity'])

f2 = open('service_similarity.csv', 'w')
writer2 = csv.writer(f2)
writer2.writerow(['sample', 'similarity'])

f3 = open('service_levenshtein_distance.csv', 'w')
writer3 = csv.writer(f3)
writer3.writerow(['sample', 'distance'])

output_dataset = []

for x in range(len(dataset["train"])): 
 
   
    # Get the corresponding label
    in_text = dataset["train"][x]["label"]

    print("The system randomly selected the log number:",x,"\n", in_text)

    # Create a dictionary containing the log, the label and the position
    vocab = {"LOG" : dataset["train"][x]["raw_logs"], "LABEL" : dataset["train"][x]["label"], "POSITION": x}

    print("\n",vocab["LOG"])


    # Prepare the text to submit to the transfomer
    text = "translate raw_logs to label:"+vocab["LOG"][:512]


    # Get tokenizer from the fine-tuned model
    tokenizer = AutoTokenizer.from_pretrained("pretrained_model")

    # Tokenize the text
    inputs = tokenizer(text, return_tensors="pt").input_ids

    # Get the fine-tuned model
    model = AutoModelForSeq2SeqLM.from_pretrained("pretrained_model")

    # Generate the transaltion
    outputs = model.generate(inputs, max_new_tokens=40, do_sample=True, top_k=30, top_p=0.95)

    # Decode the transaltion
    tokenizer.decode(outputs[0], skip_special_tokens=True)

    
    # Mapping between letters and service names
    inverse_mapping = {'A': 'carts', 'B': 'payment', 'C': 'shipping', 'D': 'user'} # Mapping used for SockShop


    # Get the translation and split by separator
    string_input = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Translation: " + str(string_input))
    letters_list = string_input.split("--")

    words_list = []

    # Substitute letters with service names
    try:
        words_list = [inverse_mapping[letter] for letter in letters_list]
    except KeyError:
        continue

    string_output = "--".join(words_list)

    print("***OUTPUT***")
    print(string_output)

    # Prepare entry for the output dataset
    entry = dict(dataset["train"][x])
    entry['min_start_time'] = str(dataset["train"][x]['min_start_time'])
    entry['max_end_time'] = str(dataset["train"][x]['max_end_time'])
    entry["inferred_services"] = string_output

    output_dataset.append(entry)

    
    # Mapping between service names and letters
    mapping = { 'carts': 'A','payment': 'B', 'shipping': 'C', 'user': 'D'} # Mapping used for SockShop

    elements = in_text.split('--')
    result  = ''

    for element in elements:
            result += mapping[element] + '--'
    result = result[:-2]

    print("IN TEXT translated: ", result)

    distance = Levenshtein.distance(result, string_input)
    print("Levenshtein distance: ", distance)

    writer3.writerow([x, distance])
    f3.flush()


    def find_unique_services(a):
        result = ""
        next_letter = 'A'

        # Extract string from the JSON
        string = a["label"]
        elements = string.split('--')

        for element in elements:
            result += mapping[element] + '--'

        # Remove the last ' ' extra
        result = result[:-2]

        a["label"] = result

        return a

    dataset2 = load_dataset("json", data_files={"train": "dataset/dataset.json"}) # Validation dataset
    mapped_dataset = dataset2.map(find_unique_services)
    

    
    def find_similar_string(input_string, d_set):
        min_distance = 1000  # Initialized with a high value
        similar_string = None
        
        for candidate in d_set:
            distance = Levenshtein.distance(input_string, candidate["label"], score_cutoff=min_distance)
            if distance < min_distance:
                min_distance = distance
                similar_string = candidate["raw_logs"]
        return similar_string, min_distance

    # Example of usage
    similar_string, min_distance = find_similar_string(stringa_input, mapped_dataset["train"])

    print("\n")

    if similar_string is not None:
        print(f"The most similar log with respect to the generated service sequence \n'{string_output}' is \n\n'{similar_string}'")
    else:
        print("No similar string find in the list.")
    


    ## INPUT
    log_lines_IN = vocab["LOG"].split("\n")

    ultime_parti_IN = [line.split("|")[-1].strip() for line in log_lines_IN]

    log_unificato_IN = " ".join(ultime_parti_IN)

    ## OUTPUT
    log_lines_OUT = stringa_simile.split("\n")

    ultime_parti_OUT = [line.split("|")[-1].strip() for line in log_lines_OUT]

    log_unificato_OUT = " ".join(ultime_parti_OUT)



    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    def similarity_evaluation(input_text, output_text):

        # Creation of a counting vector for the words in the texts
        vectorizer = CountVectorizer().fit_transform([input_text, output_text])

        # Evaluation of the codine similarity between the text vectors
        cosine_sim = cosine_similarity(vectorizer)

        # The value in the (0, 1) cell represents the similarity between the input and output
        similarity = cosine_sim[0][1]

        return similarity

    # Example of usage

    input_text = log_unificato_IN
    output_text = log_unificato_OUT

    similarity = similarity_evaluation(input_text, output_text)
    similarity = similarity*100
    similarity = round(similarity, 2)
    print(f"\Similarity between input and output logs: {similarity}%")

    writer.writerow([x, min_distance, similarity])
    f.flush()

    # Evaluate similarity between services
    input_text = entry['label']
    output_text = entry['inferred_services']
    similarity = similarity_evaluation(input_text, output_text)
    similarity = similarity * 100
    similarity = round(similarity, 2)

    writer2.writerow([x, similarity])
    f2.flush()



output_path = "output_dataset.json"
with open(output_path, 'w') as output_file:
    json.dump(output_dataset, output_file, indent=4)

f.close()
f2.close()
f3.close()
