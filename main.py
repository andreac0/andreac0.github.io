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


def get_data(*args, **kws):
	df = pd.read_json("data/"+Element("path").value+"/chase.json")[['name','provenance']]
	df2 = df[df['provenance'] == "[]"]['name'].reset_index(drop = True).to_string(header = False, index = False)
	Element('edb_facts').write(df2)
	if "trading" in Element("path").value:
		# df = df[df['name'].str.startswith('returns(')][['name']]
		# df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		# Element('idb_facts').write(df_write)
		df_nl = pd.read_csv("data/trading/nl.csv")
		Element('idb_facts').write(df_nl['Derived Fact'].to_string(header = False, index = False))
	elif "ownership" in Element("path").value:
		# df = df[df['name'].str.startswith('control(')][['name']]
		# df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		# Element('idb_facts').write(df_write)
		df_nl = pd.read_csv("data/ownership/nl.csv")
		Element('idb_facts').write(df_nl['Derived Fact'].to_string(header = False, index = False))
	elif "closeLink" in Element("path").value:
		# df = df[df['name'].str.startswith('closelink(')][['name']]
		# df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		# Element('idb_facts').write(df_write)
		df_nl = pd.read_csv("data/closeLink/nl.csv")
		Element('idb_facts').write(df_nl['Derived Fact'].to_string(header = False, index = False))
	elif "shock" in Element("path").value:
		# df = df[df['name'].str.startswith('default(')][['name']]
		# df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		df_nl = pd.read_csv("data/shock/nl.csv")
		Element('idb_facts').write(df_nl['Derived Fact'].to_string(header = False, index = False))
	new_options = ""
	# for i in range(len(df)):
	# 	new_options = new_options + "<option>"+df.iloc[i]['name']+"</option>"
	for i in range(len(df_nl)):
		new_options = new_options + "<option>"+df_nl.iloc[i]['Derived Fact']+"</option>"
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
		df_nl = pd.read_csv("data/ownership/nl.csv")
	elif "shock" in Element("path").value:
		df_nl = pd.read_csv("data/shock/nl.csv")
	elif "closeLink" in Element("path").value:
		df_nl = pd.read_csv("data/closeLink/nl.csv")
	elif "trading" in Element("path").value:
		df_nl = pd.read_csv("data/trading/nl.csv")
	fact_of_interest = Element("dropdownIDB").value
	df_nl[df_nl['Derived Fact'] == fact_of_interest]['Original Verbalization']
	Element("res_det").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['Original Verbalization']].to_string(header = False, index = False))
	Element("paraphrased").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['paraphrasis']].to_string(header = False, index = False))
	Element("summarized").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['summa']].to_string(header = False, index = False))
	Element("frameworked").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['Paraphrased Verbalization']].to_string(header = False, index = False))
	Element("result").write(df_nl[df_nl['Derived Fact'] == fact_of_interest][['Paraphrased Verbalization']].to_string(header = False, index = False))