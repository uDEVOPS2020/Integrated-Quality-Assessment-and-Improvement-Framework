import os
import sys
import csv
import glob

if __name__ == "__main__":

    folder_to_analyze = 'campaign_ss'
    jumped_test_file = 'jumped.txt'
    uTest_folder_name = 'uTestOutput'
    stats_file_name= 'stats.txt'
    testFeatures_file_name= 'testFeatures.csv'
    
    coverage_class3_string = 'Coverage (3 class):'
    coverage_class2_string = 'Coverage (2 class):'
    path_string = 'Path:'
    generated_test_string = 'Total tests generated:'
    executed_test_string = 'Executed test:'
    success_test_string = 'Success:'
    failed_test_string = 'Test Failures:'

    output_file_csv = 'results_ss_with_services.csv'
    output_file_txt = 'results_ss_with_services.txt'


    paths = {}
    error_codes = {}
    success_codes = {}

    total_coverage_class3 = 0
    total_coverage_class2 = 0
    total_executed_tests = 0
    total_not_executed_tests = 0
    total_success_tests = 0
    total_failed_tests = 0
    total_failed_500_tests = 0

    checked_folders = 0

    with open(output_file_csv, 'w') as results_csv_file:
        writer = csv.writer(results_csv_file, delimiter=",")
        writer.writerow(['test', 'coverage_class3', 'coverage_class2', 
                         'generated_tests', 'executed_tests', 'not_executed_tests', 
                         'success_tests', 'failed_tests', 'failed_500_tests',
                         'incremental_coverage_class3_%', 'incremental_coverage_class2_%', 'incremental_failed_tests_%', 
                         'incremental_failed_500_tests_%', 'incremental_executed_tests'])

    # Iterate on the tests
    for current_test_folder in sorted(os.listdir(folder_to_analyze)):

        # Check if the test has been jumped
        try:
            with open(jumped_test_file, 'r') as jumped_file:
                if (current_test_folder in jumped_file.read()) or (len(glob.glob(folder_to_analyze + "/" + current_test_folder + '/*.json')) == 0):
                    continue
        except FileNotFoundError:
            print("Jumped file not present")

        print("Folder: " + current_test_folder)

        path_to_inspect = folder_to_analyze + "/" + current_test_folder + "/" + uTest_folder_name

        generated_test = 0
        executed_test = 0
        coverage_class3 = 0
        coverage_class2 = 0
        not_executed_tests = 0
        success_test = 0
        failed_test = 0
        failed_500_test = 0

        # Check the stats file to take coverage (2 and 3 class), path and extecuted/failed and not executed test
        with open(path_to_inspect+"/"+stats_file_name, 'r') as stats_file:

            # Iterate on the file lines
            for line in stats_file.readlines():

                if coverage_class3_string in line: # Check for coverage 3 class string
                    coverage_class3 = float(line.split()[3])
                    total_coverage_class3 = total_coverage_class3 + coverage_class3
                    print("\tCoverage (3 class): " + str(coverage_class3))

                elif coverage_class2_string in line: # Check for coverage 3 class string
                    coverage_class2 = float(line.split()[3])
                    total_coverage_class2 = total_coverage_class2 + coverage_class2
                    print("\tCoverage (2 class): " + str(coverage_class2))

                elif path_string in line: # Check the covered Path 
                    path = line.split()[3]
                    if line.split()[3] in paths:
                        paths[path] = paths[path] + 1
                    else:
                        paths[path] = 1
                        #print("\tPath: " + path)
                    print("\tPath: " + path)

                elif generated_test_string in line: # Check the generated test

                    generated_test = int(line.split()[3])
                    print("\tGenerated tests: " + str(generated_test))

                elif executed_test_string in line: # Check the executed test

                    executed_test = int(line.split()[2])
                    print("\tExecuted tests: " + str(executed_test))

                    total_executed_tests = total_executed_tests + executed_test

                    if (int(generated_test)-int(executed_test) > 0): # Check the not executed
                        not_executed_tests = int(generated_test)-int(executed_test)
                        total_not_executed_tests = total_not_executed_tests + not_executed_tests
                        print("\tNot executed tests: " + str(not_executed_tests))

                elif success_test_string in line: # Check the succeed test
                    success_test = int(line.split()[1])
                    total_success_tests = total_success_tests + success_test
                    print("\tSuccess tests: " + str(success_test))

                elif failed_test_string in line: # Check the failed test
                    failed_test = int(line.split()[2])
                    total_failed_tests = total_failed_tests + failed_test
                    print("\tFailed tests: " + str(failed_test))
        
        # Check the test Features file to take the failed and success status
        with open(path_to_inspect+"/"+testFeatures_file_name, 'r') as testFeatures_file:
            reader = csv.reader(testFeatures_file, delimiter=',')
            
            next(reader, None)  # skip the headers
            
            # iterate on the csv file
            for row in reader:
                status = row[0]
                code = row[1]
                
                if status == "failed": # Check for failed test
                    if code in error_codes:
                        error_codes[code] = error_codes[code] + 1
                    else: 
                        error_codes[code] = 1
                        print("\tError code: " + code)
                    if code == '500':
                        failed_500_test = failed_500_test + 1
                        total_failed_500_tests = total_failed_500_tests + 1


                else: # Check for success test
                    if code in success_codes:
                        success_codes[code] = success_codes[code] + 1
                    else:
                        success_codes[code] = 1
                        print("\tSuccess code: " + code)

        checked_folders = checked_folders + 1

        with open(output_file_csv, 'a') as results_csv_file:
            writer = csv.writer(results_csv_file, delimiter=",")
            
            incremental_coverage_class3 = (total_coverage_class3/float(checked_folders))*100
            incremental_coverage_class2 = (total_coverage_class2/float(checked_folders))*100
            incremental_failed_tests = (total_failed_tests/float(total_executed_tests))*100
            incremental_failed_500_tests = (total_failed_500_tests/float(total_executed_tests))*100
            incremental_executed_tests = total_executed_tests


            writer.writerow([current_test_folder, coverage_class3, coverage_class2, 
                             generated_test, executed_test, not_executed_tests, 
                             success_test, failed_test, failed_500_test,
                             incremental_coverage_class3, incremental_coverage_class2, incremental_failed_tests,
                             incremental_failed_500_tests, incremental_executed_tests])

                

        #if checked_folders == 10:
        #    sys.exit()

    with open(output_file_txt, 'w') as results_file:

        results_file.write(f"Total executed test = {total_executed_tests}\n")
        results_file.write(f"Total not executed test = {total_not_executed_tests}\n")
        results_file.write(f"Total sucess test = {total_success_tests}\n")
        results_file.write(f"Total failed test = {total_failed_tests}\n")

        average_coverage_class3 = total_coverage_class3/float(checked_folders)
        average_coverage_class2 = total_coverage_class2/float(checked_folders)
        results_file.write(f"Average coverage (3 class) = {str(average_coverage_class3)}\n")
        results_file.write(f"Average coverage (2 class) = {str(average_coverage_class2)}\n")

        print(f"Total executed test = {total_executed_tests}")
        print(f"Total not executed test = {total_not_executed_tests}")
        print(f"Total success test = {total_success_tests}")
        print(f"Total failed test = {total_failed_tests}")
        print(f"Average coverage (3 class) = {str(average_coverage_class3)}")
        print(f"Average coverage (2 class) = {str(average_coverage_class2)}")

        print(f"Unique paths = {len(paths.keys())}")
        print("Paths: ")
        results_file.write("\nPaths:\n")
        for key in paths.keys():
            print(f"\t{key}: {paths[key]}")
            results_file.write(f"{key}: {paths[key]}\n")

        print("Error codes: ")
        results_file.write("\nError codes:\n")
        for key in error_codes.keys():
            print(f"\t{key}: {error_codes[key]}")
            results_file.write(f"{key}: {error_codes[key]}\n")


        print("Success codes: ")
        results_file.write("\nSuccess codes:\n")
        for key in success_codes.keys():
            print(f"\t{key}: {success_codes[key]}")
            results_file.write(f"{key}: {success_codes[key]}\n")

        
    

        
