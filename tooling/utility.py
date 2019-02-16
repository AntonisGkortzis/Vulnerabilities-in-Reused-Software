import datetime
import time
import subprocess
import os

class Utility(object):
    log_file = "error_log.txt"


    @staticmethod
    def write_to_file(file_path, content):
        #print("\tWriting project results to csv file: %s" % file_path)
        try:
            with open(file_path, 'a') as out_file:
                out_file.write(content)
        except IOError as e:
            print('''## ERROR while writting to file {}
                Check log file for further details'''
                .format(file_path))
            Utility.log(e)
            

    @staticmethod
    def execute_process(command):
        command = command.replace("\\","/")
        # print("\tExecuting process from command : {}".format(command)) # DEBUG

        try:
            process = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            (out, err) = [x.decode() for x in process.communicate()]

        except Exception as e:
            print('''## ERROR while executing process {}
                Check log file for further details'''
                .format(command))
            Utility.log(e)

        # print(err) # DEBUG
        return out, err


    @staticmethod
    def read_file(file_path):
        lines = []
        try:
            with open(file_path) as file:
                for line in file:
                    line = line.strip() # preprocess line to remove \n
                    lines.append(line)
        except IOError as e:
            print('''## ERROR while reading file {}
                Check log file for further details'''
                .format(file_path))
            Utility.log(e)

        return lines


    @staticmethod
    def log(line):
        f = open(Utility.log_file, "a", errors='ignore')
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " " + line + "\n")
        f.close()
