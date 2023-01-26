'''
Sandbox script to try out GPT-3 + Google Search
'''

import openai
from bs4 import BeautifulSoup
import requests

import pandas as pd

import time

green = '\x1b[32m'
white = '\x1b[37m'

api_key = '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' # old: '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'

openai.api_key = api_key
completion = openai.Completion()

def get_questions_answers_so_far(questions, answers):
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


def predict(chat_log):
    response = completion.create(engine="text-davinci-003",
                                prompt=chat_log,
                                temperature=0.0,
                                max_tokens=250,
                                top_p=1.0,
                                frequency_penalty=0.0,
                                presence_penalty=-0.6)
    answer = response.choices[0].text.strip()
    return answer


def predict_naive(chat_log):
    response = completion.create(engine="text-davinci-003",
                                prompt=chat_log,
                                temperature=0.0,
                                max_tokens=50,
                                top_p=1.0,
                                frequency_penalty=0.0,
                                presence_penalty=-0.6)
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

def flow(chat_log):
    global questions
    global answers
    print(f'{white}')
    question = input('Question: ')
    chat_log += make_template1(
    question, get_questions_answers_so_far(questions, answers))
    questions.append(question)
    answers.append('')
    openai_response = predict(chat_log)
    google_url = get_google_search_url(openai_response)
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
    answer = answer.split('GPT-GQ:')[-1]
    answers[-1] = answer
    return answer

correct_count = 0
chat_log = ''

for i in range(30):
  answer = flow(chat_log)
  print(f"{green}{answer}")
  chat_log = ''
  
  
