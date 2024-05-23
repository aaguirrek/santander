import requests
import frappe
import json
import base64
from pydub import AudioSegment


@frappe.whitelist(allow_guest=False)
def solicitud_cert(name):
	doc = frappe.get_doc("Santander Documentos Credito Vehicular",name)
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
	"files": [
		{
		"name": "hoja_resumen.pdf",
		"base64": atob(doc.hoja_resumen)
		}
	]
	})
	headers = {
			'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlZXh0ZXJubzciLCJpYXQiOjE3MTY0ODMyNDQsImV4cCI6MTcxNzM0NzI0NH0.R9grZBL4TmbJzyvYAixsndj9yFFLJjvc24ntfN2ZHIyySmfOPyo8FRgfFp61Gtz8jXfoSWYs6CoaGpSCdQHM8Q',
			'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=payload)
	doc.docstatus=1
	doc.save()
	return response.json()


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