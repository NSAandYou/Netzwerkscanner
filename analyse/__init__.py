class PassiveAnalyser:
    def __init__(self, output_feedback):
        self.output_feedback = output_feedback

    def analyse_package(self, package):
        self.output_feedback(str(package))
