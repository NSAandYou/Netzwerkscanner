class PassiveAnalyser:
    def __init__(self, output_feedback):
        self.output_feedback = output_feedback

    def analyse_package(self, package):
        # Analysing packages and generating output based on the results

        self.output_feedback(str(package))
