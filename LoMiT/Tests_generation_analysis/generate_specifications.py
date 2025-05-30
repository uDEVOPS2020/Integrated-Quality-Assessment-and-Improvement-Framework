import json
import os
import shutil
import sys  

def get_services(item):
    
    s = item['inferred_services']

    # split the list obtained as data from the label field
    services = s.split('--')

    # list of indicated services
    return services
        
def get_json(services, swagger_folder, destination_folder, JSONFiles_tt_text_file, init_execute_clear_tt_sh_file):

    i=0

    for filename in os.listdir(swagger_folder):

        # take all json files
        if filename.endswith(".json"):

            # create the total path of each json file
            swagger_file_path = os.path.join(swagger_folder, filename)
        
            with open(swagger_file_path, 'r') as swagger_file:

                dati = json.load(swagger_file)
                
                s = dati['paths'] 
                
                # for on all the obtained services
                for service in services:
                
                    
                    
                    serv = service.replace('user', 'customers/{id}')
                    serv = serv.replace('shipping', 'catalogue')
                    serv = serv.replace('carts', 'carts/{customerId}/items')
                    serv = serv.replace('payment', '/health')

                    print("**** SERV: " + serv + " ****")
                    
                    
                    file_paths=list(map(lambda x: x.lower(), s))

                   

                    # check if the service is in the json file
                    if serv.lower() in '\t'.join(file_paths):

                        print("SERVICE FOUND!!")

                        # move the specification in the new json file
                            
                        m = {}

                        for path, methods in dati.get('paths', {}).items():
                                
                            if 'post' in methods and serv in path:

                                print(path)
                                print(methods)

                                start = {k: dati[k] for k in list(dati.keys())[:list(dati.keys()).index("paths")]}
                                m[path] = {'post': methods['post']}
                                p = {'paths': m}
                                fine = {"definitions": dati.get("definitions", {})}                                

                                new_json={**start, **p, **fine}

                                
                                new_file = f"./{destination_folder}/service_{str(i).zfill(3)}.json"
                                    
                                with open(new_file, 'w') as new_file:

                                    # create a new json file with the selected specifications
                                    json.dump(new_json, new_file, indent=4) 

                                # Append in the file "JSONFiles_tt.txt" of an entry like "JSONDoc/Files/service_{str(i).zfill(3)}.json"
                                with open(f"./{destination_folder}/{JSONFiles_tt_text_file}", 'a') as txt_file:
                                    txt_file.write(f"JSONDoc/Files/service_{str(i).zfill(3)}.json\n")

                                # Append of the request to the sh file
                                with open(f"./{destination_folder}/{init_execute_clear_tt_sh_file}", 'a') as sh_file:
                                    sh_file.write(f"curl -X POST -H \"Accept: application/text\" -T ./initFiles/JSONFiles_ss_burp/service_{str(i).zfill(3)}.json http://localhost:11111/specification?filename=service_{str(i).zfill(3)}.json\n")

                                i=i+1

                                break

                            elif 'get' in methods and serv in path:

                                print(path)
                                print(methods)

                                start = {k: dati[k] for k in list(dati.keys())[:list(dati.keys()).index("paths")]}
                                m[path] = {'get': methods['get']}
                                p = {'paths': m}
                                fine = {"definitions": dati.get("definitions", {})}                                

                                new_json={**start, **p, **fine}

                                new_file = f"./{destination_folder}/service_{str(i).zfill(3)}.json"
                                    
                                with open(new_file, 'w') as new_file:

                                    # create a new json file with the selected specifications
                                    json.dump(new_json, new_file, indent=4) 

                                # Append in the file "JSONFiles_tt.txt" of an entry like "JSONDoc/Files/service_{str(i).zfill(3)}.json"
                                with open(f"./{destination_folder}/{JSONFiles_tt_text_file}", 'a') as txt_file:
                                    txt_file.write(f"JSONDoc/Files/service_{str(i).zfill(3)}.json\n")

                                # Append of the request to the sh file
                                with open(f"./{destination_folder}/{init_execute_clear_tt_sh_file}", 'a') as sh_file:
                                    sh_file.write(f"curl -X POST -H \"Accept: application/text\" -T ./initFiles/JSONFiles_ss_burp/service_{str(i).zfill(3)}.json http://localhost:11111/specification?filename=service_{str(i).zfill(3)}.json\n")

                                i=i+1

                                break

                        services.remove(service)

             

# Clean destination folder
def clean(destination_folder):
    
    if (os.path.exists(destination_folder)):
        shutil.rmtree(destination_folder)
        os.makedirs(destination_folder, exist_ok=True)


# Create the initial part of the init-execute-clear_tt.sh file
def generate_initial_part_sh_file(item_folder, init_execute_clear_tt_sh_file):

    with open(f"{item_folder}/{init_execute_clear_tt_sh_file}", 'a') as sh_file:
        sh_file.write("#!/bin/sh\n")
        sh_file.write("#\n")
        sh_file.write("curl -X POST -H \"Accept: application/text\" -T ./initFiles/config.txt http://localhost:11111/configuration?filename=config.txt\n")
        sh_file.write("curl -X POST -H \"Accept: application/text\" -T ./initFiles/JSONFiles_ss.txt http://localhost:11111/jsonfilestxt?filename=JSONFiles.txt\n")


# Create the final part of the init-execute-clear_tt.sh file
def generate_final_part_sh_file(item_folder, init_execute_clear_tt_sh_file):

    with open(f"{item_folder}/{init_execute_clear_tt_sh_file}", 'a') as sh_file:
        sh_file.write("curl -X GET http://localhost:11111/execute?execOption=all\n")
        sh_file.write("curl -s -X GET http://localhost:11111/file?fileID=log --output ./output/log.txt\n")
        sh_file.write("curl -s -X GET http://localhost:11111/file?fileID=failed --output ./output/failedTests.txt\n")
        sh_file.write("curl -s -X GET http://localhost:11111/file?fileID=success --output ./output/successTests.txt\n")
        sh_file.write("curl -s -X GET http://localhost:11111/file?fileID=stats --output ./output/stats.txt\n")
        sh_file.write("curl -s -X GET http://localhost:11111/file?fileID=features --output ./output/testFeatures.csv\n")
        sh_file.write("curl -s -X GET http://localhost:11111/file?fileID=testsuite --output ./output/testsuite.txt\n")
        sh_file.write("curl -s -X GET http://localhost:11111/file?fileID=reliabilities --output ./output/reliabilities.csv\n")
        sh_file.write("curl -X GET http://localhost:11111/clean\n")


if __name__=="__main__":

    i = 1

    

    # Folder where the original swagger files are available
    swagger_folder = '/home/train/uTest/clientCommands/initFiles/JSONFiles_ss_burp'

    # Folder where the campaing files will be generated
    campaign_folder = 'campaign_ss'

    # Text file containing the list of swagger files to consider for the test generation
    JSONFiles_tt_text_file = "JSONFiles_ss.txt"

    # Sh file containing the request to uTest for loading the swagger files
    init_execute_clear_tt_sh_file = "init-execute-clear_ss.sh"

    # Clean destination folder
    clean(campaign_folder)


    with open("output_dataset.json", 'r') as file_json:

        data = json.load(file_json)

        for item in data:

            item_folder = f"{campaign_folder}/{str(i).zfill(4)}_{item['trace_id']}"

            os.makedirs(item_folder, exist_ok=True)

            # Save involved_urls in a file
            with open(f"{item_folder}/involved_services.txt", 'a') as involved_urls_file:
                involved_urls_file.write(item['label'])

            with open(f"{item_folder}/inferred_services.txt", 'a') as involved_urls_file:
                involved_urls_file.write(item['inferred_services'])

            with open(f"{item_folder}/logs.txt", 'a') as involved_urls_file:
                involved_urls_file.write(item['raw_logs'])

            # Create the initial part of the init-execute-clear_tt.sh file
            generate_initial_part_sh_file(item_folder, init_execute_clear_tt_sh_file)

            print("Trace-ID: " + str(item['trace_id']))

            services = get_services(item)

            # Print the list of services
            print("List of extracted services:")
            for idx, service in enumerate(services, start=1):
                print(f"{idx}. {service}")

            get_json(services, swagger_folder, item_folder, JSONFiles_tt_text_file, init_execute_clear_tt_sh_file)

            generate_final_part_sh_file(item_folder, init_execute_clear_tt_sh_file)

            i = i + 1
            

            


    
    
