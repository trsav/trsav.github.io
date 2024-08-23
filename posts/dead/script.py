from transformers import pipeline
import numpy as np
import time

def process_file(filename):
    # Read file content
    with open(filename, 'r') as file:
        data = file.readlines()
    
    # Find lines with 'changeable_text'
    changeable_lines = []
    for i in range(len(data)):
        if '''.changeable_text''' in data[i] :
            changeable_lines.append(i+1)
            break 

    random_line = np.random.choice(changeable_lines)
    text = data[random_line]
    
    # Process footnote if present
    if '^[' in text:
        footnote_index = text.index('^[')
        end_footnote = text.index('\\x00]')
        pre_footnote, post_footnote = text.split('^[')[0], text.split("\\x00]")[1]
        footnote = text[footnote_index:end_footnote+5]
        footnote_word_index = text[:footnote_index].count(' ')
        print('FOOTNOTE WORD INDEX:', footnote_word_index)
        data[random_line] = pre_footnote + post_footnote
    
    # Replace random word with [MASK]
    line = data[random_line].split()
    random_word_index = np.random.randint(0, len(line))
    print('REMOVED WORD', line[random_word_index])
    rem_word_store = line[random_word_index]
    line[random_word_index] = '[MASK]'
    line = ' '.join(line)
    
    # Use BERT to fill [MASK]
    unmasker = pipeline('fill-mask', model='bert-base-uncased')
    res = unmasker(line)
    replacement_word = res[0]['token_str']
    print('REPLACEMENT WORD:', replacement_word)
    line = line.replace('[MASK]', replacement_word)
    
    # Reinsert footnote if it existed
    if 'footnote' in locals():
        line_words = line.split()
        line_words.insert(footnote_word_index, footnote)
        line = ' '.join(line_words) + '\n'
    
    line = line.replace(':::', '\n:::\n')
    data[random_line] = line
    
    # Process 'extra' lines
    extra_lines = [i+1 for i, line in enumerate(data) if 'extra' in line]
    if extra_lines:
        generated = data[extra_lines[0]].strip()
        hypothesised = generated + ' [MASK]'
        res = unmasker(hypothesised)
        print('ADDED WORD:', res[0]['token_str'])
        data[extra_lines[0]] = f"{generated} {res[0]['token_str']}\n"
    
    # Update timestamp
    utc_str = time.asctime(time.gmtime())
    print('UTC:', utc_str)

    data[-1] = f'''Updated: {utc_str}. Replaced {rem_word_store} with {replacement_word}. Added {res[0]['token_str']} to the end of the generated text.'''
    
    # Write updated content back to file
    with open(filename, 'w') as file:
        file.writelines(data)

process_file('posts/dead/index.qmd')