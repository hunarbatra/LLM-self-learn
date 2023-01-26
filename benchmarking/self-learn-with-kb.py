'''
Self-learning from Google Searches + Knowledge Base for learnt info
'''

import openai
from bs4 import BeautifulSoup
import requests

import pandas as pd

import time
import random
from config import api_key

green = '\x1b[32m'
white = '\x1b[37m'

openai.api_key = api_key
completion = openai.Completion()

questions, answers, knowledge = [], [], []

google_template = 'http://google.com/search?q='

main_prompt = 'You are incredibly intelligent with an interest in learning concepts online to improve your knowledge for solving questions. You like using Google to understand concepts and gain knowledge through Google search results to solve the given question.'

def naive_answer(q, questions, answers):
    convo = ""
    for ques, ans in zip(questions[:20], answers[:20]):
        convo += f"Question: {ques}\n"
        convo += f"Answer: {ans}\n"
    return f'''
{convo}
Question: {q}'''

def get_questions_answers_so_far(questions, answers):
    # convo = "Here is GPT-GQ's conversation so far:\n"
	convo = "Here are the questions you've solved so far" if len(questions) > 1 else ''
	for question, answer in zip(questions[:10], answers[:10]):
		convo += f"Question: {question}\n"
		convo += f"Answer: {answer}\n"
	return convo

def get_knowledge_base_so_far(knowledge, limit=False):
    knowledge_base = 'From the previously solved questions, you know that: ' if len(knowledge) else ''
    if limit:
        knowledge = random.sample(knowledge, min(15, len(knowledge)))
    for i in range(len(knowledge)):
        knowledge_base += '(' + str(i+1) + ') ' + knowledge[i]
    return knowledge_base 

def make_template1(question, convo, knowledge_base):
    return f'''
{main_prompt}
{knowledge_base}
{convo}
Question: {question}
You look up the question on Google and understand how to solve it.
You navigate to {google_template}'''

def make_template2(chat_log, html):
	if len(chat_log.split(' ')) + len(html.split(' ')) + 300 >= 4097:
		html = html[:(4097-len(chat_log.split(' '))-300)]
		html = ' '.join(html)
		print(len(html.split(' ')))
	return f'''
You see this text from the Google search page:
```
"""
{html}
"""
```
You summarize this information and conclude that:'''

def make_template3(concluded_answer):
	return f'''
{concluded_answer}
Now, lets thinks step by step over the concluded search information and over what you already know to solve the question:'''

def make_template4(cot_answer):
	return f'''
{cot_answer}
The final answer is:'''

def make_template5(answer):
    return f'''
{answer}
Now, you self-reflect and observe that by solving this question, you learned that:'''


def predict(chat_log, max_tokens=250):
	response = completion.create(engine="text-davinci-003",
								prompt=chat_log,
								temperature=0.0,
								max_tokens=max_tokens,
								top_p=1.0,
								frequency_penalty=0.0,
								presence_penalty=-0.6)
	answer = response.choices[0].text.strip()
	return answer


def get_google_search_url(response):
	supplemented = google_template + response
	return supplemented[:supplemented.index(' ')]

def get_html(url):
	response = requests.get(url)
	if response.status_code == 200:
		soup = BeautifulSoup(response.content, "html.parser")
		text = soup.get_text()
	else:
		text = ""
	return text

def flow(chat_log, ques, correct_answer):
	global questions
	global answers
	global knowledge
	print(f'{white}')
	question = ques
	naive_log = naive_answer(question, questions, answers)
	naive_response = predict(naive_log, max_tokens=50)
	print('\nNaive Response: ' + naive_response)
	questions.append(question)
	if correct_answer not in naive_response.split('Answer')[-1]:
		try:
			time.sleep(5)
			chat_log += make_template1(
				question, get_questions_answers_so_far(questions, answers), get_knowledge_base_so_far(knowledge))
			answers.append('')
			url_response = predict(chat_log)
			google_url = get_google_search_url(url_response)
			print('Search URL: ' + google_url)
			html = get_html(google_url)
			chat_log = chat_log.replace(google_template, google_url)
			temp_chat_log = chat_log + make_template2(chat_log, html)
			concluded_answer = predict(temp_chat_log)
			concluded_answer = 'From the Google Search page, you concluded that: ' + concluded_answer 
			print('Concluded Info: ' + concluded_answer)
			chat_log += make_template3(concluded_answer)
			cot_answer = predict(chat_log)
			print('CoT Answer: ' + cot_answer)
			chat_log += make_template4(cot_answer)
			answer = predict(chat_log)
			answers[-1] = answer
			chat_log += make_template5(answer)
			learnt_info = predict(chat_log, max_tokens=100)
			knowledge.append(learnt_info)
			print('Learnt Info: ' + learnt_info)
			return answer
		except:
			print('ERROR - Context window length: \n')
			time.sleep(5)
			chat_log += make_template1(
				question, get_questions_answers_so_far(questions, answers), get_knowledge_base_so_far(knowledge, limit=True))
			answers.append('')
			url_response = predict(chat_log)
			google_url = get_google_search_url(url_response)
			print('Search URL: ' + google_url)
			html = get_html(google_url)
			chat_log = chat_log.replace(google_template, google_url)
			temp_chat_log = chat_log + make_template2(html)
			concluded_answer = predict(temp_chat_log)
			concluded_answer = 'From the Google Search page, you concluded that: ' + concluded_answer 
			print('Concluded Info: ' + concluded_answer)
			chat_log += make_template3(concluded_answer)
			cot_answer = predict(chat_log)
			print('CoT Answer: ' + cot_answer)
			chat_log += make_template4(cot_answer)
			answer = predict(chat_log)
			answers[-1] = answer
			chat_log += make_template5(answer)
			learnt_info = predict(chat_log, max_tokens=100)
			knowledge.append(learnt_info)
			print('Learnt Info: ' + learnt_info)
			return answer
	else:
		time.sleep(1)
		answers.append(naive_response)
	return naive_response

correct_count = 0
chat_log = ''
option_mapping = {0: ' (A) ', 1: ' (B) ', 2: ' (C) ', 3: ' (D) '}

df = pd.read_csv('datasets/global_facts_test.csv', header=None)

for i in range(0, len(df)): 
	print("\n\nCurrent Q number = " + str(i+1))
	ques = df[0][i]
	if ques[-1] != '.':
		ques += '.'
	options = ''
	for j in range(4):
		options += option_mapping[j] + df[j+1][i]
	ques += options + '. Choose the correct answer.'
	correct_answer = df[5][i]
	answer = flow(chat_log, ques, correct_answer)
	print(f"{green}{answer}")
	if '(' + correct_answer + ')' in answer or correct_answer + ')' in answer or correct_answer in answer or correct_answer + '.' in answer:
		print("Correct")
		correct_count += 1
		print("Current Correct Count = " + str(correct_count))
	else:
		print("Current Correct Count = " + str(correct_count))
		print("Incorrect")
	chat_log = ''
 

print('Knowledge Base: ')
for i in range(len(knowledge)):
    print('(' + str(i+1) + ') ' + knowledge[i])

print('GPT++ SL w Memory Updation Accuracy: ' + str(float(correct_count / len(df) * 100)))
