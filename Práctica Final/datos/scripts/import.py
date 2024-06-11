import urllib.request
import json
import os

start = 6000
end = 6100

url_base = "https://hj.tribunalconstitucional.es/HJ/Resolucion/Api/json/"  # Replace with the actual URL of the file


current = start
while current <= end:
    try:
        urllib.request.urlretrieve(url_base+(str(current)), "Files/"+str(current)+".json")
        print("Downloaded " + str(current) + ".json")
    except Exception as e:
        print("Error: " + str(e))

    finally:
        with open("Files/"+str(current)+".json", encoding='utf8') as json_file:
            data = json.load(json_file)
        if data["TIPO_RESOLUCION"] != "SENTENCIA":
            print("Deleting " + str(current) + ".json")
            os.remove("Files/"+str(current)+".json")
        current += 1




