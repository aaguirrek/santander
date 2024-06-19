import requests
import frappe
import json
import base64
from pydub import AudioSegment
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models


@frappe.whitelist(allow_guest=False)
def personaj(uri, nombre="",dominio='softhub.pe'):
	vertexai.init(project="academy-300721", location="us-central1")
	model = GenerativeModel(
		"gemini-1.5-flash-001",
	)
	generation_config = {
		"max_output_tokens": 8192,
		"temperature": 1,
		"top_p": 0.95,
	}
	document1 = Part.from_data(
		mime_type="application/pdf",
		data=atob(uri,dominio)
	)
	safety_settings = {
		generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
		generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
		generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
		generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
	}
	responses = model.generate_content(
	
		[document1, """a través del siguiente documento """+nombre+""" tiene el poder para celebrar una compraventa de un bien mueble? Dame la respuesta unica y exclusivamente en el siguente formato en caso tengas problemas en verificarlo la respuesta deberá ser NO y en el mensaje se detallara la respuesta el formato JSON es el siguiente: {"respuesta":"SI/NO", "MENSAJE":"Resumen de maximo 190 caracteres donde se explica el motivo de la respuesta","partida_registral":"Partida Registral de la empresa del registro de personas jurídicas","empresa":"nombre de la empresa","zona":"Zona registral de la empresa del registro de personas jurídicas","fecha":"fecha del documento"}"""],
		generation_config=generation_config,
		safety_settings=safety_settings,
		stream=True,
	)
	responsefinal = ''
	for response in responses:
		responsefinal += response.text
	responsefinal=responsefinal.split("{")
	if len(responsefinal) > 0:
		responsefinal="{"+responsefinal[1]
		
		responsefinal=responsefinal.split("}")
		if len(responsefinal) > 0:
			responsefinal=responsefinal[0]+"}"
	try:
		responsefinal = json.loads(responsefinal)
	except:
		pass
	return responsefinal

@frappe.whitelist(allow_guest=False)
def traducirdocumento(uri,dominio='softhub.pe'):
	vertexai.init(project="academy-300721", location="us-central1")
	model = GenerativeModel(
		"gemini-1.5-flash-001",
	)
	generation_config = {
		"max_output_tokens": 8192,
		"temperature": 1,
		"top_p": 0.95,
	}
	document1 = Part.from_data(
		mime_type="application/pdf",
		data=atob(uri,dominio)
	)
	safety_settings = {
		generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
		generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
		generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
		generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
	}
	responses = model.generate_content(
	
		[document1, """transcribe el documento de manera literal"""],
		generation_config=generation_config,
		safety_settings=safety_settings,
		stream=True,
	)

	responsefinal = ''
	for response in responses:
		responsefinal += response.text

	return responsefinal

@frappe.whitelist(allow_guest=False)
def solicitud_cert(name):
	doc = frappe.get_doc("Santander Documentos Credito Vehicular",name)
	docjson  = frappe.get_doc("Santander Documentos Credito Vehicular",name).as_dict()
	url = "https://api.qa.iofesign.com/api/v1/outside/createrequest/onesign"

	payload = {'typePersonId': '1',
	'documentType': '1',
	'documentNumber': doc.dni,
	'enterpriseDocumentNumber': '',
	'enterpriseBusinessName': '',
	'firstName': doc.nombre,
	'lastName': doc.apellido_paterno+" "+doc.apellido_materno,
	'email': doc.correo_cliente,
	'countryId': '168',
	'phone': doc.telefono,
	'powerValidity': '',
	'rucFile': ''}
	front_uri='/home/frappe/frappe-bench/sites/softhub.pe/public'+doc.documento_dni
	back_uri='/home/frappe/frappe-bench/sites/softhub.pe/public'+doc.cargar_dni_reverso
	files=[
			('frontDocuments',open(front_uri,'rb') ),
			('backDocuments',open(back_uri,'rb') )
	]
	headers = {
			'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlZXh0ZXJubzciLCJpYXQiOjE3MTY0ODMyNDQsImV4cCI6MTcxNzM0NzI0NH0.R9grZBL4TmbJzyvYAixsndj9yFFLJjvc24ntfN2ZHIyySmfOPyo8FRgfFp61Gtz8jXfoSWYs6CoaGpSCdQHM8Q'
	}

	response = requests.request("POST", url, headers=headers, data=payload, files=files)
	response =  response.json()
	front_b64=""
	back_b64=""
	with open(front_uri, 'rb') as image_file:
		base64_bytes = base64.b64encode(image_file.read())
		front_b64 = base64_bytes.decode()
		
	with open(back_uri, 'rb') as image_file:
		base64_bytes = base64.b64encode(image_file.read())
		back_b64 = base64_bytes.decode()


	filesJson=[]
	filesJson=addtofiles(filesJson, docjson,"hoja_resumen")
	filesJson=addtofiles(filesJson, docjson,"cotizacion_seguro_vehicular")
	filesJson=addtofiles(filesJson, docjson,"carta_beneficios_repsol")
	filesJson=addtofiles(filesJson, docjson,"contrato_de_credito_vehicular")
	filesJson=addtofiles(filesJson, docjson,"solicitud_de_credito")
	filesJson=addtofiles(filesJson, docjson,"pagare_credito_vehicular")
	filesJson=addtofiles(filesJson, docjson,"carta_beneficios_repsol")
	filesJson=addtofiles(filesJson, docjson,"hoja_resumen")
	filesJson=addtofiles(filesJson, docjson,"solicitud_de_instalacion_de_gps")
	filesJson=addtofiles(filesJson, docjson,"proteccion_de_datos_personales")
	filesJson=addtofiles(filesJson, docjson,"formato_edpyme")
	filesJson=addtofiles(filesJson, docjson,"cronograma_vehicular")
	filesJson=addtofiles(filesJson, docjson,"seguro_de_desgravamen")
	filesJson=addtofiles(filesJson, docjson,"declaracion_uso_de_vehiculo")
	filesJson=addtofiles(filesJson, docjson,"fichar_ruc")
	filesJson=addtofiles(filesJson, docjson,"vigencia_de_poder")
	
	
	url = "https://api.qa.iofesign.com/api/v1/outside/documents"

	payload = json.dumps({
	"type": 1,
	"subject": "FIRMA DE CONTRATO",
	"workflowId": 651,
	"participants": [
		{
		"personByPersonId": {
			"type": 1,
			"documentType": 1,
			"documentNumber": doc.dni,
			"firstname": doc.nombre,
			"lastname":  doc.apellido_paterno,
			"lastname2": doc.apellido_materno,
			"email": doc.correo_cliente,
			"countryId": "168",
			"requestId": str(response["requestId"]),
			"cellphone": "982025955",
			"documentFrontBase64Data": front_b64,
			"documentFrontFilename": doc.documento_dni.replace("/files/",""),
			"documentRearBase64Data": back_b64,
			"documentRearFilename": doc.cargar_dni_reverso.replace("/files/",""),
			"enterpriseDocumentNumber": "",
			"jobDescription": ""
		},
		"orderParticipant": 1
		}
	],
	"files":filesJson
	})
	headers = {
			'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlZXh0ZXJubzciLCJpYXQiOjE3MTY0ODMyNDQsImV4cCI6MTcxNzM0NzI0NH0.R9grZBL4TmbJzyvYAixsndj9yFFLJjvc24ntfN2ZHIyySmfOPyo8FRgfFp61Gtz8jXfoSWYs6CoaGpSCdQHM8Q',
			'Content-Type': 'application/json'
	}
	
	doc.request_id= str(response["requestId"])
	response = requests.request("POST", url, headers=headers, data=payload)
	doc.save()
	return response.json()

@frappe.whitelist(allow_guest=True)
def wh(id, subject,verificationcode,urlfile,filename,code):
	frappe.set_user("Administrator")
	doc = frappe.get_last_doc(doctype="Santander Documentos Credito Vehicular", filters=["request_id","=",id])
	doc.subject =subject
	doc.verificationcode =verificationcode
	doc.urlfile =urlfile
	doc.filename =filename
	doc.code =code
	doc.docstatus=1
	doc.save()
	return "save"

def addtofiles(arr=[],doc=None,name=""):
	if doc["check_"+name]==1:
		arr.append({
		"name": doc[name].replace("/files/",""),
		"base64": atob(doc[name])
		})
	return arr

def filename(name):
	return name.replace("/files/","")

def atob(uri,origin='softhub.pe'):
	back_b64=""
	back_uri='/home/frappe/frappe-bench/sites/'+origin+'/public'+uri
	with open(back_uri, 'rb') as image_file:
		base64_bytes = base64.b64encode(image_file.read())
		back_b64 = base64_bytes.decode()
	return back_b64



@frappe.whitelist(allow_guest=False)
def solicitud_cert_pj(name):
	doc = frappe.get_doc("Santander Documentos Credito Vehicular",name)
	docjson  = frappe.get_doc("Santander Documentos Credito Vehicular",name).as_dict()
	url = "https://api.qa.iofesign.com/api/v1/outside/createrequest/onesign"

	payload = {'typePersonId': '1',
	'documentType': '1',
	'documentNumber': doc.dni,
	'enterpriseDocumentNumber': '',
	'enterpriseBusinessName': '',
	'firstName': doc.nombre,
	'lastName': doc.apellido_paterno+" "+doc.apellido_materno,
	'email': doc.correo_cliente,
	'countryId': '168',
	'phone': doc.telefono,
	'powerValidity': '',
	'rucFile': ''}
	front_uri='/home/frappe/frappe-bench/sites/softhub.pe/public'+doc.documento_dni
	back_uri='/home/frappe/frappe-bench/sites/softhub.pe/public'+doc.cargar_dni_reverso
	files=[
			('frontDocuments',open(front_uri,'rb') ),
			('backDocuments',open(back_uri,'rb') )
	]
	headers = {
			'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlZXh0ZXJubzciLCJpYXQiOjE3MTY0ODMyNDQsImV4cCI6MTcxNzM0NzI0NH0.R9grZBL4TmbJzyvYAixsndj9yFFLJjvc24ntfN2ZHIyySmfOPyo8FRgfFp61Gtz8jXfoSWYs6CoaGpSCdQHM8Q'
	}

	response = requests.request("POST", url, headers=headers, data=payload, files=files)
	response =  response.json()
	front_b64=""
	back_b64=""
	with open(front_uri, 'rb') as image_file:
		base64_bytes = base64.b64encode(image_file.read())
		front_b64 = base64_bytes.decode()
		
	with open(back_uri, 'rb') as image_file:
		base64_bytes = base64.b64encode(image_file.read())
		back_b64 = base64_bytes.decode()


	filesJson=[]
	filesJson=addtofiles(filesJson, docjson,"hoja_resumen")
	filesJson=addtofiles(filesJson, docjson,"cotizacion_seguro_vehicular")
	filesJson=addtofiles(filesJson, docjson,"carta_beneficios_repsol")
	filesJson=addtofiles(filesJson, docjson,"contrato_de_credito_vehicular")
	filesJson=addtofiles(filesJson, docjson,"solicitud_de_credito")
	filesJson=addtofiles(filesJson, docjson,"pagare_credito_vehicular")
	filesJson=addtofiles(filesJson, docjson,"carta_beneficios_repsol")
	filesJson=addtofiles(filesJson, docjson,"hoja_resumen")
	filesJson=addtofiles(filesJson, docjson,"solicitud_de_instalacion_de_gps")
	filesJson=addtofiles(filesJson, docjson,"proteccion_de_datos_personales")
	filesJson=addtofiles(filesJson, docjson,"formato_edpyme")
	filesJson=addtofiles(filesJson, docjson,"cronograma_vehicular")
	filesJson=addtofiles(filesJson, docjson,"seguro_de_desgravamen")
	filesJson=addtofiles(filesJson, docjson,"declaracion_uso_de_vehiculo")
	filesJson=addtofiles(filesJson, docjson,"fichar_ruc")
	filesJson=addtofiles(filesJson, docjson,"vigencia_de_poder")
	
	
	url = "https://api.qa.iofesign.com/api/v1/outside/documents"

	payload = json.dumps({
	"type": 1,
	"subject": "FIRMA DE CONTRATO",
	"workflowId": 651,
	"participants": [
		{
		"personByPersonId": {
			"type": 1,
			"documentType": 1,
			"documentNumber": doc.dni,
			"firstname": doc.nombre,
			"lastname":  doc.apellido_paterno,
			"lastname2": doc.apellido_materno,
			"email": doc.correo_cliente,
			"countryId": "168",
			"requestId": str(response["requestId"]),
			"cellphone": "982025955",
			"documentFrontBase64Data": front_b64,
			"documentFrontFilename": doc.documento_dni.replace("/files/",""),
			"documentRearBase64Data": back_b64,
			"documentRearFilename": doc.cargar_dni_reverso.replace("/files/",""),
			"enterpriseDocumentNumber": "",
			"jobDescription": ""
		},
		"orderParticipant": 1
		}
	],
	"files":filesJson
	})
	headers = {
			'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlZXh0ZXJubzciLCJpYXQiOjE3MTY0ODMyNDQsImV4cCI6MTcxNzM0NzI0NH0.R9grZBL4TmbJzyvYAixsndj9yFFLJjvc24ntfN2ZHIyySmfOPyo8FRgfFp61Gtz8jXfoSWYs6CoaGpSCdQHM8Q',
			'Content-Type': 'application/json'
	}
	
	doc.request_id= str(response["requestId"])
	response = requests.request("POST", url, headers=headers, data=payload)
	doc.save()
	return response.json()
