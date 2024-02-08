import sys

import structure
from worker import Worker


def run(arguments):
    network_interface = None
    clf_file_path = None

    for index in range(1, len(arguments)):
        try:
            if arguments[index][0] == '-':
                if arguments[index] == '-i':
                    network_interface = arguments[index + 1]
                elif arguments[index] == '-h':
                    print_help()
                    return None
                elif arguments[index] == '-p':
                    structure.PASSIVE_ONLY = True
                elif arguments[index] == '-c':
                    clf_file_path = arguments[index + 1]
                else:
                    print("ERROR! Couldn't understand parameter " + arguments[index])
                    print_help()
                    return None
        except IndexError:
            print("ERROR! Missing parameter value " + arguments[index])
            print_help()
            return None

    if network_interface is None:
        network_interface = input("Whats the name of the network interface? ")
    if clf_file_path is None:
        clf_file_path = input("Whats the path of the Passive Scan Classifier? ")

    return Worker(network_interface, clf_file_path)


def print_help():
    print("""Welcome to this help dialog! Please use it as follows:
    -i NETWORK_INTERFACE, set the network interface which should be used for passive scans
    -c CLASSIFIER, set the path to the classifier used for the passive analyser
    -p PASSIVE ONLY, turn off active scans to stay invisible
    -h, prints this help dialog""")


if __name__ == '__main__':
    worker = run(sys.argv)
    if worker is not None:
        worker.start()
