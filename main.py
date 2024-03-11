from js import document
import pandas as pd
import json
from pyodide.http import open_url
from datetime import datetime as dt
from pyodide.ffi.wrappers import add_event_listener
from pycode import AggregateVerbalizer
from pycode import ProgramVerbalizer
from pycode import TemplatesGenerator
from pycode.utils import *
from openai import OpenAI
import requests
from js import localStorage, document, console, XMLHttpRequest
from dotenv import load_dotenv
import os
import re
import random2 as random

# def round_numbers_in_text(text):
#     # Define a regular expression pattern to match numbers
#     pattern = r'\d+(\.\d+)?'  # Matches integers and decimals
    
#     # Find all matches in the text
#     matches = re.findall(pattern, text)
    
#     # Round each number found in the text
#     rounded_text = text
#     for match in matches:
#         rounded_number = round(float(match),2)
#         rounded_text = rounded_text.replace(match, str(rounded_number))
    
#     return rounded_text


def get_data(*args, **kws):
	# df = pd.read_json("data/"+Element("path").value+"/chase.json")[['name','provenance']]
	# df2 = df[df['provenance'] == "[]"]['name'].reset_index(drop = True).to_string(header = False, index = False)
	# Element('edb_facts').write(df2)
	pd.set_option("display.max_colwidth", 10000)
	df = pd.read_json("data/"+Element("path").value+"/deterministic_verbalization.json")[['derived_fact','type','sentence']]
	df2 = df[df['type'] == 'extensional']['sentence'].reset_index(drop = True).to_string(header = False, index = False).replace('\"','')
	df2 = re.sub(' +', ' ', df2)
	Element('edb_facts').write(df2)
	if "trading" in Element("path").value:
		df_nl = df[df['derived_fact'].str.startswith('returns(')][['sentence','derived_fact']]
		df_write = pd.DataFrame([head.split(', then')[1].replace('\"','').split(',')[0] for head in df_nl['sentence']]).to_string(header = False, index = False)
		Element('idb_facts').write(re.sub(' +', ' ', df_write))
	elif "ownership" in Element("path").value:
		df_nl = df[df['derived_fact'].str.startswith('control(')][['sentence','derived_fact']]
		df_write = pd.DataFrame([head.split(', then')[1].replace('\"','') for head in df_nl['sentence']]).to_string(header = False, index = False)
		Element('idb_facts').write(re.sub(' +', ' ', df_write))
	elif "closeLink" in Element("path").value:
		df_nl = df[df['derived_fact'].str.startswith('closeLink(')][['sentence','derived_fact']]
		df_write = pd.DataFrame([head.split(', then')[1].replace('\"','') for head in df_nl['sentence']]).to_string(header = False, index = False)
		Element('idb_facts').write(re.sub(' +', ' ', df_write))
	elif "shock" in Element("path").value:
		df_nl = df[df['derived_fact'].str.startswith('default(')][['sentence','derived_fact']]
		df_write = pd.DataFrame([head.split(', then')[1].replace('\"','') for head in df_nl['sentence']]).to_string(header = False, index = False)
		Element('idb_facts').write(re.sub(' +', ' ', df_write))
	new_options = ""

	for i in range(len(df_nl)):
		new_options = new_options + "<option>"+df_nl.iloc[i]['derived_fact']+"</option>"
	Element("dropdownIDB").element.innerHTML = new_options

def explanation_query(*args, **kws):
	path = Element("path").value
	url = "data/"+path+"/chase.json"
	with open('data/'+path+'/templates.json') as f:
		templates_full = json.load(f)
	chase_fact = list()
	chase_fact.append(AggregateVerbalizer.VerbalizationFinder().get_chase_fact(url,Element("dropdownIDB").value))
	try: 
		verb = TemplatesGenerator.TemplatesGenerator().mapping_to_template(chase_fact[0][0], chase_fact[0][1], templates_full, templates_full, 'data/'+path+'/', Element("dropdownIDB").value, 'data/'+path+'/deterministic_verbalization.json')
		
		Element("res_det").write(verb[['Original Verbalization']].to_string(header = False, index = False))
		
		load_dotenv()
		secret_key = os.getenv('API_KEY')
		prompt_para= 'Paraphrase this text:' + verb[['Original Verbalization']].to_string(header = False, index = False)
		bearer = "Bearer " + secret_key
		engine = "gpt-3.5-turbo-instruct"
		xhr = XMLHttpRequest.new()
		xhr.open("POST", "https://api.openai.com/v1/completions", False)
		xhr.setRequestHeader("Content-Type", "application/json")
		xhr.setRequestHeader("Authorization", bearer)
		data = json.dumps({
			"model": engine,
			"prompt": prompt_para,
			"max_tokens": 250,
			"temperature": 0.9,
			"top_p": 1,
			"frequency_penalty": 0,
			"presence_penalty": 0
		})
		xhr.send(data)
		paraph = json.loads(xhr.response)
		Element("paraphrased").write(paraph['choices'][0]['text'])

		prompt_summary = 'Summarize this text:' + verb[['Original Verbalization']].to_string(header = False, index = False)
		xhr = XMLHttpRequest.new()
		xhr.open("POST", "https://api.openai.com/v1/completions", False)
		xhr.setRequestHeader("Content-Type", "application/json")
		xhr.setRequestHeader("Authorization", bearer)
		data = json.dumps({
			"model": engine,
			"prompt": prompt_summary,
			"max_tokens": 250,
			"temperature": 0.9,
			"top_p": 1,
			"frequency_penalty": 0,
			"presence_penalty": 0
		})
		xhr.send(data)
		summarization = json.loads(xhr.response)

		Element("paraphrased").write(paraph['choices'][0]['text'])
		Element("summarized").write(summarization['choices'][0]['text'])

		# Element("paraphrased").write('---')
		# Element("summarized").write('---')
		
		Element("result").write(verb[['Paraphrased Verbalization']].to_string(header = False, index = False))

	except Exception as e:
		print(f"An error occurred: {e}")


def text_der(*args, **kws):
	if "ownership" in Element("path").value:
		varG = random.choice([1,2,3])
		df_nl = pd.read_csv("data/ownership/nl.csv")
		df_nl = df_nl[df_nl['type']==varG]
	elif "shock" in Element("path").value:
		varG = random.choice([1,2])
		df_nl = pd.read_csv("data/shock/nl.csv")
		df_nl = df_nl[df_nl['type']==varG]
	elif "closeLink" in Element("path").value:
		df_nl = pd.read_csv("data/closeLink/nl.csv")
	elif "trading" in Element("path").value:
		varG = random.choice([1,2,3,4])
		df_nl = pd.read_csv("data/trading/nl.csv")
		df_nl = df_nl[df_nl['type']==varG]
	fact_of_interest = Element("dropdownIDB").value
	df_nl[df_nl['Derived Fact'] == fact_of_interest]['Original Verbalization']
	Element("res_det").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['Original Verbalization']].to_string(header = False, index = False))
	Element("paraphrased").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['paraphrasis']].to_string(header = False, index = False))
	Element("summarized").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['summa']].to_string(header = False, index = False))
	Element("frameworked").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['Paraphrased Verbalization']].to_string(header = False, index = False))
	Element("result").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['Paraphrased Verbalization']].to_string(header = False, index = False))