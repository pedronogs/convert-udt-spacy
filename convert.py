import json
import subprocess

# Convert NER tag to IOB format based on token and annotated text 
def convertIOB(token, annotation):
    # If token is equal to annotated text or at least first word, return with 'B' tag
    if token == annotation[0] or token == annotation[0].split(' ')[0]:
        return (token, 'B-{}'.format(annotation[1].upper()))

    return (token, 'I-{}'.format(annotation[1].upper()))

def main():
    udt_json = json.load(open("sample.json", "r", encoding='utf-8'))
    udt_samples = udt_json['samples']

    # Open IOB file for annotated data output in IOB format
    f = open('sample.iob', 'w', encoding="utf-8")

    # Convert UDT NER JSON to NER in IOB format
    for sample in udt_samples:
        sample_words = sample['document'].split(' ') # Store all sample words in a list

        # Store all sample entities in a list of tuples
        sample_entities = []
        for entity in sample['annotation']['entities']:
            sample_entities.append((entity['text'], entity['label']))

        # Check if token is anotated or not, if it's not, annotate it
        # Each token will be added to final list according to IOB format of annotation
        sample_iob = []
        for token in sample_words:
            flag_added = False
            for annotation in sample_entities:
                if token in annotation[0].split(): # Check if token is in annotated text
                    token_iob = convertIOB(token, annotation) # Convert single or multi-word token with respective IOB tag
                    sample_iob.append(token_iob)
                    flag_added = True
            
            # If token is not already annotated, append with 'O' tag
            if flag_added == False:
                sample_iob.append((token, 'O'))

        for idx, annotation in enumerate(sample_iob):
            f.write('{}|{}'.format(annotation[0], annotation[1]))

            if idx + 1 < len(sample_iob):
                f.write(' ')

        # Break line after every sentence     
        f.write('\n')

    # Convert IOB file to spaCy binary format
    spacy = True
    if spacy == True:
        subprocess.run(['python', '-m', 'spacy', 'convert', '-c', 'iob', '-n', '2', '-l', 'pt', 'sample.iob', '.'])
        

if __name__ == '__main__':
    main()