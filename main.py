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



def get_data(*args, **kws):
	df = pd.read_json("data/"+Element("path").value+"/chase.json")[['name','provenance']]
	df2 = df[df['provenance'] == "[]"]['name'].reset_index(drop = True).to_string(header = False, index = False)
	Element('edb_facts').write(df2)
	if "trading" in Element("path").value:
		df = df[df['name'].str.startswith('returns(')][['name']]
		df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		Element('idb_facts').write(df_write)
	elif "ownership" in Element("path").value:
		df = df[df['name'].str.startswith('control(')][['name']]
		df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		Element('idb_facts').write(df_write)
	elif "closeLink" in Element("path").value:
		df = df[df['name'].str.startswith('closelink(')][['name']]
		df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		Element('idb_facts').write(df_write)
	elif "shock" in Element("path").value:
		df = df[df['name'].str.startswith('default(')][['name']]
		df_write = df.reset_index(drop = True).to_string(header = False, index = False)
		Element('idb_facts').write(df_write)
	new_options = ""
	for i in range(len(df)):
		new_options = new_options + "<option>"+df.iloc[i]['name']+"</option>"
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
		
		# prompt_para= 'Paraphrase this text:' + verb[['Original Verbalization']].to_string(header = False, index = False)
		# bearer = "Bearer <APIKEY>"
		# engine = "gpt-3.5-turbo-instruct"
		# xhr = XMLHttpRequest.new()
		# xhr.open("POST", "https://api.openai.com/v1/completions", False)
		# xhr.setRequestHeader("Content-Type", "application/json")
		# xhr.setRequestHeader("Authorization", bearer)
		# data = json.dumps({
		# 	"model": engine,
		# 	"prompt": prompt_para,
		# 	"max_tokens": 250,
		# 	"temperature": 0.9,
		# 	"top_p": 1,
		# 	"frequency_penalty": 0,
		# 	"presence_penalty": 0
		# })
		# xhr.send(data)
		# paraph = json.loads(xhr.response)
		# Element("paraphrased").write(paraph['choices'][0]['text'])
	
		# prompt_summary = 'Summarize this text:' + verb[['Original Verbalization']].to_string(header = False, index = False)
		# xhr = XMLHttpRequest.new()
		# xhr.open("POST", "https://api.openai.com/v1/completions", False)
		# xhr.setRequestHeader("Content-Type", "application/json")
		# xhr.setRequestHeader("Authorization", bearer)
		# data = json.dumps({
		# 	"model": engine,
		# 	"prompt": prompt_summary,
		# 	"max_tokens": 250,
		# 	"temperature": 0.9,
		# 	"top_p": 1,
		# 	"frequency_penalty": 0,
		# 	"presence_penalty": 0
		# })
		# xhr.send(data)
		# summarization = json.loads(xhr.response)

		# Element("paraphrased").write(paraph['choices'][0]['text'])
		# Element("summarized").write(summarization['choices'][0]['text'])

		Element("paraphrased").write('---')
		Element("summarized").write('---')
		
		Element("result").write(verb[['Paraphrased Verbalization']].to_string(header = False, index = False))

	except Exception as e:
		print(f"An error occurred: {e}")