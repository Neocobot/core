'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo
'''
import importlib


class PVTAlgorithmImpl:
    def __init__(self, arm):
        self.arm = arm

    def run(self, path_poses, max_velocity=None, max_acceleration=None, closed_path=False, linear_segments=None):
        pass


class PVTAlgorithmManager:
    @staticmethod
    def set_algorithm(arm, algorithm_name=None):
        try:
            if algorithm_name is None:
                module = importlib.import_module("neocobot.model.pvt.pvta_none")
                c = module.PVTAlgorithm
                return c(arm)
        except Exception as e:
            import neocobot.model.pvt.pvta_none
            return neocobot.model.pvt.pvta_none.PVTAlgorithm


