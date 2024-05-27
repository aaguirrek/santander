import requests
import frappe
import json
import base64
from pydub import AudioSegment


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

def atob(uri):
	back_b64=""
	back_uri='/home/frappe/frappe-bench/sites/softhub.pe/public'+uri
	with open(back_uri, 'rb') as image_file:
		base64_bytes = base64.b64encode(image_file.read())
		back_b64 = base64_bytes.decode()
	return back_b64



#{
#    "id": 3611,
#    "hashIdentifier": "3dfef829a28af77ea98f8a3db31619e09d8fa1ab7503a4ee437c0de26e1a1657",
#    "finished": 0,
#    "subject": "FIRMA DE CONTRATO",
#    "createAt": "2024-05-23T21:05:06.845+00:00",
#    "active": 1,
#    "_links": {
#        "stream": {
#            "href": "http://api.qa.iofesign.com/api/v1/public/outside/documents/3611/3dfef829a28af77ea98f8a3db31619e09d8fa1ab7503a4ee437c0de26e1a1657/stream"
#        }
#    }
#}