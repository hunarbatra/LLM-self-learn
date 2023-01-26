'''
Recursive search, WORK IN PROGRESS (incomplete as of now, work paused until further update)
'''

import openai
from bs4 import BeautifulSoup
import requests

import pandas as pd
from config import api_key

green = '\x1b[32m'
white = '\x1b[37m'

openai.api_key = api_key
completion = openai.Completion()

def get_questions_answers_so_far(questions, answers):
    convo = "Here is GPT-GQ and User\'s conversation so far:\n"
    for question, answer in zip(questions[:20], answers[:20]):
        convo += f"User: {question}\n"
        convo += f"GPT-GQ: {answer}\n"
    return convo

google_template = 'http://google.com/search?q='

def naive_answer(question, convo):
    return f'''
        {convo}
        {question}'''

def make_template1(question, convo, naive_response):
    return f'''
		GPT-GQ is incredibly intelligent and has an interest in learning concepts online to improve its knowledge. It uses Google to help itself understand concepts, how things work under the hood, and gain knowledge through multiple online resources to solve the given question. To do this GPT-GQ, generates Google Search Query URLs, navigates to the results page and generates a summary of the observed text. If GPT-GQ has any follow-up concepts to learn about, it makes multiple Search Queries needed to solve the given question.
		Today, GPT-GQ and User are chatting online. 
		{convo}
		User: {question}
		Naive Answer: {naive_response}
		GPT-GQ looks that up on Google and understand how to solve user's question.
		GPT-GQ navigates to {google_template}'''

def make_template2(html):
	return f'''
		GPT-GQ sees this text from the Google search page:
		```
		"""
		{html}
		"""
		```
		From this information, GPT-GQ concludes that:
		'''
  
def follow_up_queries(chat):
    return f'''
    {chat}
    Are follow-up search queries needed?:
    '''

def make_template3(concluded_answer):
	return f'''
	{concluded_answer}
	Now, GPT-GQ thinks step by step and uses the initial naive answer and the concluded search information to solve the given the question:
	'''

def make_template4(cot_answer):
	return f'''
	{cot_answer}
	The final answer to User's question is:
	'''


def predict(chat_log):
    response = completion.create(engine="text-davinci-003",
                                prompt=chat_log,
                                temperature=0.0,
                                max_tokens=250,
                                top_p=1.0,
                                frequency_penalty=0.0,
                                presence_penalty=0)
    answer = response.choices[0].text.strip()
    return answer

questions, answers, summaries = [], [], []

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

def flow(chat_log, ques):
    global questions
    global answers
    global summaries
    print(f'{white}')
    question = ques
    naive_response = predict(naive_answer(question, get_questions_answers_so_far(questions, answers)))
    chat_log += make_template1(question, get_questions_answers_so_far(questions, answers), naive_response)
    questions.append(question)
    answers.append('')
    openai_response = predict(chat_log)
    google_url = get_google_search_url(openai_response)
    print('Search URL: ' + google_url)
    html = get_html(google_url)
    chat_log = chat_log.replace(google_template, google_url)
    temp_chat_log = chat_log + make_template2(html)
    concluded_answer = predict(temp_chat_log)
    print('Concluded Answer: ' + concluded_answer)
    chat_log += make_template3(concluded_answer)
    cot_answer = predict(chat_log)
    print('CoT Answer: ' + cot_answer)
    chat_log += make_template4(cot_answer)
    answer = predict(chat_log)
    answers[-1] = answer
    return answer

correct_count = 0
chat_log = ''
option_mapping = {0: ' (A) ', 1: ' (B) ', 2: ' (C) ', 3: ' (D) '}

df = pd.read_csv('datasets/college_physics_test.csv', header=None)

for i in range(0, len(df)): 
  print("Current Q number = " + str(i+1))
  ques = df[0][i]
  if ques[-1] != '.':
    ques += '.'
  options = ''
  for j in range(4):
    options += option_mapping[j] + df[j+1][i]
  ques += options + '. Choose the correct answer.'
  answer = flow(chat_log, ques)
  print(f"{green}{answer}")
  correct_answer = df[5][i]
  if '(' + correct_answer + ')' in answer or correct_answer + ')' in answer or correct_answer in answer:
      print("Correct")
      correct_count += 1
      print("Current Correct Count = " + str(correct_count))
  else:
      print("Incorrect")
  chat_log = ''
  
  
print('GPT-GQ Accuracy: ' + str(float(correct_count / len(df) * 100)))
  