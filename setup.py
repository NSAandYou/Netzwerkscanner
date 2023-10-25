from worker import Worker


def run(arguments):
    network_interface = None

    for index in range(1, len(arguments)):
        try:
            if arguments[index][0] == '-':
                if arguments[index] == '-i':
                    network_interface = arguments[index + 1]
                elif arguments[index] == '-h':
                    print_help()
                    return None
                else:
                    print("ERROR! Couldn't understand parameter " + arguments[index])
                    print_help()
                    return None
        except IndexError:
            print("ERROR! Missing parameter value " + arguments[index])
            print_help()
            return None

    if network_interface is None:
        network_interface = input("Whats the interface name? ")

    return Worker(network_interface)


def print_help():
    print("""Welcome to this help dialog! Please use it as follows:
    -i NETWORK_INTERFACE, set the network interface witch should be used for passive scans
    -h, prints this help dialog""")
