import openai
import pandas as pd

import time
from config import api_key

green = '\x1b[32m'
white = '\x1b[37m'

openai.api_key = api_key
completion = openai.Completion()

def get_questions_answers_so_far(questions, answers):
  convo = ""
  for question, answer in zip(questions[:20], answers[:20]):
    convo += f"Question: {question}\n"
    convo += f"Answer: {answer}\n"
  return convo

def make_template1(question, convo):
    return f'''
        {convo}
        Question: {question}'''

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

questions, answers = [], []

def flow(chat_log, ques):
  global questions
  global answers
  print(f'{white}')
  question = ques
  chat_log += make_template1(
    question, get_questions_answers_so_far(questions, answers))
  questions.append(question)
  answers.append('')
  answer = predict(chat_log)
  answers[-1] = answer
  return answer

correct_count = 0
chat_log = ''
option_mapping = {0: ' (A) ', 1: ' (B) ', 2: ' (C) ', 3: ' (D) '}

df = pd.read_csv('datasets/global_facts_test.csv', header=None)

for i in range(0, len(df)):
  print("Current Q number = " + str(i+1))
  time.sleep(2)
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
  if correct_answer in answer.split('Answer')[-1]:
      print("Correct") 
      correct_count += 1
      print("Current Correct Count = " + str(correct_count))
  else:
      print("Incorrect")
      print("Current Correct Count = " + str(correct_count))
  chat_log = ''
  
  
print('GPT-3 Accuracy: ' + str(float(correct_count / len(df) * 100)))
  