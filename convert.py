import json
import subprocess
import spacy
import re

# Convert NER tag to IOB format based on token and annotated text 
def convertIOB(token, annotation_text, annotation_label, previous_annotation):
    # If token is equal to annotated text or at least first word, return with 'B' tag
    if token == annotation_text[0]:
        return [token, 'B-{}'.format(annotation_label.upper())]

    # Add I tag only if previous tag was B or I
    elif previous_annotation in ['B', 'I']:
        return [token, 'I-{}'.format(annotation_label.upper())]

    return None

def main():
    udt_json = json.load(open("dev_data.json", "r", encoding='utf-8'))
    udt_samples = udt_json['samples']

    # Open IOB file for annotated data output in IOB format
    f = open('dev_data.iob', 'w', encoding="utf-8")
    
    # Create blank PT language class
    nlp = spacy.blank("pt")

    # Convert UDT NER JSON to NER in IOB format
    for index, sample in enumerate(udt_samples):
        doc = nlp(sample['document'].replace('|', '')) # Replace | for ''
        sample_words = [w.text for w in doc if w.text != ' ' and w.text != ''] # Store all sample words in a list

        # Store all sample entities in a list of lists
        if 'annotation' in sample:
            sample_entities = []
            for entity in sample['annotation']['entities']:
                entity_text = nlp(entity['text'])
                entity_text = [w.text for w in entity_text if w.text != ' ' and w.text != '']

                sample_entities.append([entity_text, entity['label']])
        # ----------------- Ignore document without annotation ------------------------------
        else:
            break

        # Check if token is anotated or not, if it's not, annotate it
        # Each token will be added to final list according to IOB format of annotation
        sample_iob = []
        previous_annotation = None
        for token in sample_words:
            tag_added = False # Flag to indicate token has already been tagged
            
            # Check if token is inside annotated text and convert it to IOB
            for idx, annotation in enumerate(sample_entities):
                if token in annotation[0]: # Check if token is in annotated text
                    token_iob = convertIOB(token, annotation[0], annotation[1], previous_annotation) # Convert single or multi-word token with respective IOB tag
                    if token_iob != None:
                        sample_iob.append(token_iob) # Append to annotated sample in IOB
                        index_token = sample_entities[idx][0].index(token)
                        sample_entities[idx][0][index_token] = sample_entities[idx][0][index_token].replace(token, '*') # Replace already used token in annotated text with keyword
                        
                        tag_added = True 
                        previous_annotation = token_iob[1][0] # Get last IOB tag
                    
                    break
    
            # If token is not already annotated, append with 'O' tag
            if tag_added == False:
                sample_iob.append([token, 'O'])
                previous_annotation = 'O'

        for idx, annotation in enumerate(sample_iob):
            f.write('{}|{}'.format(annotation[0], annotation[1]))

            # Add whitespace between annotations
            if idx + 1 < len(sample_iob):
                f.write(' ')

        # Break line after every sentence
        f.write('\n')

    # Convert IOB file to spaCy binary format
    subprocess.run(['python', '-m', 'spacy', 'convert', '-s', '-n', '10', '-l', 'pt', 'dev_data.iob', '.'])
        

if __name__ == '__main__':
    main()