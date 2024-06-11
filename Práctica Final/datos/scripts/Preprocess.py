import os
import json
import re
# Define the paths for the input and output folders
input_folder = "Files/"
output_folder = "Files_prep/"

regex_articulo = [r'\(art\.\s(\d+(?:\.\d+)*) CE\)',
                 r'art\.\s(\d+(?:\.\d+)*) CE', 
                 r'artículo\s(\d+(?:\.\d+)*) CE', 
                 r'articulo\s(\d+(?:\.\d+)*) CE',
                 r'\(art\.\s(\d+(?:\.\d+)*) Constitución Española\)',  
                 r'art\.\s(\d+(?:\.\d+)*) Constitución Española',
                 r'artículo\s(\d+(?:\.\d+)*) Constitución Española', 
                 r'articulo\s(\d+(?:\.\d+)*) Constitución Española',
                 r'\(arts\.\s(\d+(?:\.\d+)*) CE\)', 
                 r'arts\.\s(\d+(?:\.\d+)*) CE', 
                 r'artículos\s(\d+(?:\.\d+)*) CE', 
                 r'articulos\s(\d+(?:\.\d+)*) CE',
                 r'\(arts\.\s(\d+(?:\.\d+)*) Constitución Española\)',  
                 r'arts\.\s(\d+(?:\.\d+)*) Constitución Española',
                 r'artículos\s(\d+(?:\.\d+)*) Constitución Española', 
                 r'articulos\s(\d+(?:\.\d+)*) Constitución Española']
# (art. 15.2.1 CE)

regex_estima = [r'\bestimar\b',
                r'\botorgar el amparo\b',
                r'\botorgar los amparos\b',
                r'\botorgar el recurso de amparo\b',
                r'\botorgar los recursos de amparo\b',
                r'\badmitir el recurso de amparo\b',
                r'\badmitir los recursos de amparo\b']

regex_desestima = [r'\bdesestimar\b',
                   r'\bdenegar el amparo\b',
                   r'\bdeclarar inadmisible el recurso de amparo\b',
                   r'\binadmitir la cuestión de inconstitucionalidad\b',
                   r'\bdenegar los amparos\b',
                   r'\binadmitir el amparo\b',
                   r'\binadmitir el recurso de amparo\b',
                   r'\binadmitir los amparos\b',
                   r'\binadmitir los recursos de amparo\b']

flag_estima = False
flag_desestima = False

#regex_fallo = r'\b(?:desestimar|estimar)\b'

nEstima = 0
nDesestima = 0
nNoData = 0
nMultipleData = 0
# Iterate over the JSON files in the input folder
files = 0
urls_NoData = []
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        files += 1
        try:
            # Read the JSON file
            with open(os.path.join(input_folder, filename),encoding='utf8', mode="r") as file:
                data = json.load(file)
        except Exception as e:
            print("Error: " + str(e))
            #remove file
            os.remove(os.path.join(input_folder, filename))
            continue
        # Read the JSON file
        try:
            with open(os.path.join(input_folder, filename),encoding='utf8', mode="r") as file:
                data = json.load(file)
                
            antecedentes = ""
            # Iterate over the "antecedentes" field
            for antecedente in data["RESOLUCIONES_ANTECEDENTES"]:
                # Keep only the "TEXTO" field
                antecedentes += antecedente["TEXTO"]  + " "

            fudamentos = ""
            # Iterate over the "fundamentos" field
            for fundamento in data["RESOLUCIONES_FUNDAMENTOS"]:
                # Keep only the "TEXTO" field
                fudamentos += fundamento["TEXTO"]  + " "

            articulos_list = []
            for i in range(len(regex_articulo)):
                articulos = re.findall(regex_articulo[i], fudamentos)
                articulos_list += list(set(articulos))
                
            articulos_list = list(set(articulos_list))

            fallo_txt = ""
            for fallo in data["RESOLUCIONES_DICTAMEN"]:
                # Keep only the "TEXTO" field
                fallo_txt += fallo["TEXTO"]  + " "

            #estima = re.findall(regex_estima, fallo_txt)
            #desestima = re.findall(regex_desestima, fallo_txt)

            #coincidencias = re.findall(regex_fallo, fallo_txt, flags=re.IGNORECASE)

            flag_estima = 0
            flag_desestima = 0

            for i in regex_estima:
                coincidencias_es = re.findall(i, fallo_txt, flags=re.IGNORECASE)
                if len(coincidencias_es) == 1:
                    flag_estima += 1
                    

            for i in regex_desestima:
                coincidencias_des = re.findall(i, fallo_txt, flags=re.IGNORECASE)
                if len(coincidencias_des) == 1:
                    flag_desestima += 1
                    

            if flag_estima == 1 and flag_desestima == 0:
                nEstima += 1
                estima_txt = "Estima"
            if flag_desestima == 1 and flag_estima == 0:
                nDesestima += 1
                estima_txt = "Desestima"
            if (flag_estima > 0 and flag_desestima > 0) or flag_estima > 1 or flag_desestima > 1:
                nMultipleData += 1
            if flag_estima == 0 and flag_desestima == 0:
                nNoData += 1
                urls_NoData.append("https://hj.tribunalconstitucional.es/HJ/es/Resolucion/Show/" + str(data["ID"]))
                
            # Como solo queremos quedarnos con los datos que tienen un solo resultado, si hay mas de uno, nos saltamos el guardado del archivo
            if (flag_estima > 0 and flag_desestima > 0) or flag_estima > 1 or flag_desestima > 1:
                continue
            if flag_estima == 0 and flag_desestima == 0:
                continue
            
            # Create a new JSON file in the output folder with the same "id" field
            output_filename = os.path.join(output_folder, filename)
            with open(output_filename, encoding='utf8',mode="w") as file:
                json.dump({"ID": data["ID"],
                        "ANNO_RESOLUCION":data["ANNO_RESOLUCION"],
                        "SINTESIS_DESCRIPTIVA":data["SINTESIS_DESCRIPTIVA"],
                        "SINTESIS_ANALITICA":data["SINTESIS_ANALITICA"],
                        "ANTECEDENTES":antecedentes,
                        "FUNDAMENTOS":fudamentos,
                        "FALLO_TXR:": fallo_txt,
                        "ART_FUNDAMENTOS":articulos_list,
                        "ESTIMA": estima_txt
                        },indent=4,ensure_ascii=False, fp=file)
        except Exception as e:
            #esto esta para detectar errores en el formato del archivo
            print("Error: " + str(e)+ " in file " + filename)
            #Ha habido que eliminar tmbn desde el documento 29822 hasta el 29842 ya que tenian un formato erroneo
            
#save urls with no data
with open("urls_NoData.txt", "w") as file:
    for url in urls_NoData:
        file.write(url + "\n")
print("Files: " + str(files))
print("Estima: " + str(nEstima))
print("Desestima: " + str(nDesestima))
print("No data: " + str(nNoData))
print("Multiple data: " + str(nMultipleData))
