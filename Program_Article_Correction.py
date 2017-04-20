import re
import operator as op
import numpy as np
import os

regex = re.compile('[^a-zA-Z\s]')

# Get relative path till the data files
def open_file(fname):
    script_dir = os.path.dirname(__file__)
    rel_path = "Data/%s" % fname
    abs_path = os.path.join(script_dir,rel_path)
    with open(abs_path,"r") as f:
        f_lines = f.readline().split('], [')
    return f_lines

# Process the file to remove extra whitespaces and special characters
def process_file(fname,lst):
    for i in range(len(fname)):
        fname[i] = fname[i].strip()
        fname[i] = regex.sub('', fname[i])
        temp = fname[i].split(' ')
        lst.append(temp)
    return lst

# Update the incorrect articles in sentence_train.txt using corrections_train.txt, before creating the model
def correct_articles(sent_list,corr_list):
    for i in range(len(sent_list)):
        for j in range(len(sent_list[i])):
            if corr_list[i][j] != 'null':
                sent_list[i][j] = corr_list[i][j]
    return sent_list

# Remove words which are not alphabetic
def remove_non_alpha(sent_list):
    res = []
    for i in sent_list:
        for j in i:
            if not j.isalpha():
                i.remove(j)
    return sent_list

# Convert all words to lower case
def to_lower(sent_list):
    res = []
    for i in sent_list:
        i = [j.lower() for j in i]
        res.append(i)
    return res

# Get article count for each word
def set_art(sent_list,words):
    for x in sent_list:
        art = [0, 0, 0]  # ['a','an','the']
        for w in x:
            if w == 'a':
                art[0] = 1
            elif w == 'an':
                art[1] = 1
            elif w == 'the':
                art[2] = 1

        for w in x:
            if w not in ['a', 'an', 'the']:
                if w not in words:
                    words[w] = art
                else:
                    x = words[w]
                    x = map(op.add, x, art)
                    words[w] = x
    return words

# Calculate article frequency for each word in sentence_test file and get article with max value
def word_art_count(temp_list,words,final_ans):
    for i in temp_list:
        res = []
        for j in i:
            if j not in ['a', 'an', 'the'] and j in words:
                res.append(words[j])
        res1 = np.array(res)
        np.place(res1, res1 == 0, 1)
        a, b, c = 1.0, 1.0, 1.0
        for i in res1:
            a = (a * i[0]) / 1000
            b = (b * i[1]) / 1000
            c = (c * i[2]) / 1000

        ans = max(a, b, c)
        if ans == a:
            final_ans.append('a')
        elif ans == b:
            final_ans.append('an')
        else:
            final_ans.append('the')
    return final_ans

# Calculate number of correct predictions
def calculate_accuracy(corr_test_list,final_ans,sent_test_list,correct):
    for k in range(len(corr_test_list)):
        correct_art = None
        for i in range(len(corr_test_list[k])):
            if corr_test_list[k][i] != 'null':
                correct_art = corr_test_list[k][i]
                break
        if correct_art is not None:
            if final_ans[k] == correct_art:
                correct += 1
        else:
            for i in range(len(sent_test_list[k])):
                if sent_test_list[k][i] != 'null':
                    correct_art = sent_test_list[k][i]
                    break

            if correct_art == final_ans[k]:
                correct += 1
    return correct

def calculate_matching_words(private_sent_list,words):
    total_count,present_count,art_count,temp_lst = 0,0,0,[]
    for i in private_sent_list:
        for j in i:
            if j not in ['a','an','the']:
                total_count += 1
                if j in words:
                    present_count += 1
            else:
                art_count += 1
    temp_lst.append(total_count)
    temp_lst.append(present_count)
    temp_lst.append(art_count)
    return temp_lst

def predict_art_private_test(private_sent_list,words,final_art_lst):
    confidence_interval = []
    for i in private_sent_list:
        res1 = []
        for j in i:
            if j not in ['a','an','the']:
                if j in words:
                    res1.append(words[j])
        a, b, c = 1.0, 1.0, 1.0
        for i in res1:
            if i[0] == 0 or i[1] == 0 or i[2] == 0:
                a = (a * 1) / 1000
                b = (b * 1) / 1000
                c = (c * 1) / 1000
            else:
                a = (a * i[0]) / 1000
                b = (b * i[1]) / 1000
                c = (c * i[2]) / 1000
        temp = max(a,b,c)
        if temp == a:
            final_art_lst.append('a')
        elif temp == b:
            final_art_lst.append('an')
        else:
            final_art_lst.append('the')
        confidence_interval.append(temp/(a+b+c))
    return final_art_lst, confidence_interval

# Generate [article, confidence_interval] list
def generate_art_confidence_interval(confidence_interval,final_art_lst,final_res):
    for i in range(len(final_art_lst)):
        tmp = []
        tmp.append(final_art_lst[i])
        tmp.append(confidence_interval[i])
        final_res.append(tmp)
    return final_res

# Find actual article in private_sentence.txt file
def get_actual_article(private_sent_list,actual_art):
    for i in private_sent_list:
        temp = []
        for j in i:
            if j in ['a','an','the']:
                if len(temp) < 1:
                    temp.append(j)
        actual_art.append(temp)
    return actual_art

# Create final article list
def create_final_art_lst(actual_art,final_art_lst,final_res,final_subm_lst):
    for i in range(len(actual_art)):
        tmp2 = []
        if len(actual_art[i]) == 0:
            tmp2.append('null')
        elif final_art_lst[i] == actual_art[i][0]:
            tmp2.append('null')
        else:
            tmp2.append(final_res[i])
        final_subm_lst.append(tmp2)
    return final_subm_lst

# Final list with corrected articles
def create_final_submission_file(lines,final_subm_lst):
    z = []
    for i in range(len(lines)):
        lines[i].strip()
        lines[i] = lines[i].replace('\"', '')
        lines[i] = lines[i].replace('[', '')
        lines[i] = lines[i].replace(',', '')
        z.append(lines[i].split(' '))

    submit_file = []
    for i in range(len(z)):
        tmp = []
        for j in range(len(z[i])):
            if z[i][j] not in ['a', 'an', 'the']:
                st = 'null'
                tmp.append(st)
                #tmp.append('null')
            else:
                tmp.append(final_subm_lst[i][0])
        submit_file.append(tmp)
    return submit_file

# Write to output file
def write_to_file(submit_file):
    fname = "my_submission.txt"
    script_dir = os.path.dirname(__file__)
    rel_path = "Data/%s" % fname
    abs_path = os.path.join(script_dir,rel_path)
    try:
        file = open(fname, 'w')
    except IOError:
        file = open(fname, 'w')

    #submit_file = map(str, submit_file)
    #line = ",".join(submit_file)
    #file.write(line)

    file.write(str(submit_file))

def main():
    corr_train_lines = open_file("corrections_train.txt")
    sent_train_lines = open_file("sentence_train - Org.txt")
    words = {}
    sent_list = process_file(sent_train_lines,[])
    corr_list = process_file(corr_train_lines, [])
    sent_list = correct_articles(sent_list,corr_list)
    sent_list = remove_non_alpha(sent_list)
    sent_list = to_lower(sent_list)

    words = set_art(sent_list,words)

    sent_test_lines = open_file("..\\Data\\sentence_test.txt")
    final_ans = []
    sent_test_list = process_file(sent_test_lines,[])
    sent_test_list = to_lower(sent_test_list)
    sent_test_list = remove_non_alpha(sent_test_list)

    final_ans = word_art_count(sent_test_list,words,[])

    corr_test_lines = open_file("..\\Data\\corrections_test.txt")
    correct = 0
    corr_test_list = process_file(corr_test_lines,[])
    print "corr_test:", len(corr_test_list)
    sent_test_list = process_file(sent_test_lines,[])
    sent_test_list = to_lower(sent_test_list)
    correct = calculate_accuracy(corr_test_list,final_ans,sent_test_list,correct)

    print "Correct predictions: ", correct
    print "Totcal Predictions: ", len(final_ans)
    print "Accuracy: " ,correct * 100.0 / len(final_ans)

    #Check on sentence_private_test
    private_sent_lines = open_file("..\\Data\\sentence_private_test.txt")
    private_sent_list = process_file(private_sent_lines,[])
    private_sent_list = remove_non_alpha(private_sent_list)
    private_sent_list = to_lower(private_sent_list)

    calculate_matching_words(private_sent_list,words)
    final_art_lst, confidence_interval = predict_art_private_test(private_sent_list,words,[])
    final_res = generate_art_confidence_interval(confidence_interval,final_art_lst,[])

    actual_art = get_actual_article(private_sent_list,[])

    final_subm_lst = create_final_art_lst(actual_art,final_art_lst,final_res,[])

    #with open("E:\\Personal\\Imp Docs\\Jobs\\Serenity\\Serenity_research_assignment\\data\\sentence_private_test.txt",
    #          "r") as sent_priv:
    with open("E:\\Personal\\Imp Docs\\Jobs\\Serenity\\Serenity_research_assignment\\data\\sentence_test.txt",
                "r") as sent_priv:

        lines = sent_priv.readline().split('], ')

    submit_file = create_final_submission_file(lines,final_subm_lst)

    write_to_file(submit_file)

if __name__ == "__main__":
    main()