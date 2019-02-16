import argparse
import json
import time

from utility import Utility

parser = argparse.ArgumentParser()
parser.add_argument("credentials", 
    help="Your Github username and token separated by :")
parser.add_argument("project_list", 
    help="The file that contains a list of Github repositories")
parser.add_argument("output_file", 
    help="The file that will store the Github repositories with their stars")
args = parser.parse_args()


def execute():
    output_file = args.output_file
    repository_list = Utility.read_file(args.project_list)
    username = args.credentials.split(':')[0]
    token = args.credentials.split(':')[1]

    for repo in repository_list:
        connection_string = "curl -u {}:**token** https://api.github.com/repos/{}".format(username, token, repo)
        print("Executing {}".format(connection_string))
        try:
            json_content = Utility.execute_process(connection_string) # retrieve the content
            data = json.loads(json_content) # load the retrieved content into a json objet
            stars = data['watchers_count'] # retrieve the value of the field 'stars'
        except Exception as e:
            stars = '#ErrorWhileRetrievingStars#'
        output_string = "{},{}\n".format(repo,stars) # create the output string
        print("Writing {}".format(output_string))
        Utility.write_to_file(output_file, output_string)  # write the output string to a file

        time.sleep(.1400) # sleep for 1.4 seconds to avoid exceeding the limit of 5k requests per hour

execute()
