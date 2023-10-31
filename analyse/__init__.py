class PassiveAnalyser:
    def __init__(self, network_structure, output_passive, output_structure):
        self.output_passive = output_passive
        self.output_structure = output_structure
        self.network_structure = network_structure

    def analyse_package(self, pkg):
        # Analysing packages and generating output based on the results

        self.network_structure.analyse_pkg(pkg)

        self.output_passive(str(pkg))
        self.output_structure(self.network_structure.tostring())