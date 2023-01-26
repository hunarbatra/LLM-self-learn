'''
Self-learning with Google Search
'''

import openai
from bs4 import BeautifulSoup
import requests

import pandas as pd
import time
from config import api_key

green = '\x1b[32m'
white = '\x1b[37m'

openai.api_key = api_key
completion = openai.Completion()

def get_questions_answers_so_far(questions, answers):
	# convo = "Here is GPT-GQ's conversation so far:\n"
	convo = "Here are the questions you've solved so far"
	for question, answer in zip(questions[:15], answers[:15]):
		convo += f"Question: {question}\n"
		convo += f"Answer: {answer}\n"
	return convo

google_template = 'http://google.com/search?q='

def naive_answer(q, questions, answers):
    convo = ""
    for ques, ans in zip(questions[:20], answers[:20]):
        convo += f"Question: {ques}\n"
        convo += f"Answer: {ans}\n"
    return f'''
{convo}
Question: {q}'''

def make_template1(question, convo):
    return f'''
You are incredibly intelligent with an interest in learning concepts online to improve your knowledge for solving questions. You like using Google to understand concepts and gain knowledge through Google search results to solve the given question. 
{convo}
Question: {question}
You look up the question on Google and understand how to solve it.
You navigates to {google_template}'''

def make_template2(html):
	# if len(html.split(' ')) > (4097 - 250):
	# 	html = html[:(4097-250)]
	# 	html = ' '.join(html)
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
Now, lets thinks step by step over the concluded search information to solve the question:'''

def make_template4(cot_answer):
	return f'''
{cot_answer}
The final answer is:'''


def predict(chat_log, max_tokens=250):
	response = completion.create(engine="text-davinci-003",
								prompt=chat_log,
								temperature=0.0,
								max_tokens=max_tokens,
								top_p=1.0,
								frequency_penalty=0.0,
								presence_penalty=0)
	answer = response.choices[0].text.strip()
	return answer

questions, answers = [], []

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
	print(f'{white}')
	question = ques
	naive_log = naive_answer(question, questions, answers)
	naive_response = predict(naive_log, max_tokens=50)
	print('\nNaive Response: ' + naive_response)
	questions.append(question)
	if correct_answer not in naive_response.split('Answer')[-1]:
		time.sleep(5)
		chat_log += make_template1(
			question, get_questions_answers_so_far(questions, answers))
		answers.append('')
		url_response = predict(chat_log)
		google_url = get_google_search_url(url_response)
		print('Search URL: ' + google_url)
		html = get_html(google_url)
		chat_log = chat_log.replace(google_template, google_url)
		chat_log += make_template2(html)
		concluded_answer = predict(chat_log)
		print('Concluded Answer: ' + concluded_answer)
		chat_log += make_template3(concluded_answer)
		cot_answer = predict(chat_log)
		print('CoT Answer: ' + cot_answer)
		chat_log += make_template4(cot_answer)
		answer = predict(chat_log)
		answers[-1] = answer
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
  
  
print('GPT-GQ with Naive+GS CoT Accuracy: ' + str(float(correct_count / len(df) * 100)))
  