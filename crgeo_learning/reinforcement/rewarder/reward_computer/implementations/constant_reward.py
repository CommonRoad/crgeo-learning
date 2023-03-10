import numpy as np

from crgeo.dataset.commonroad_data import CommonRoadData
from crgeo_learning.reinforcement.rewarder.reward_computer.base_reward_computer import BaseRewardComputer
from crgeo.simulation.ego_simulation.ego_vehicle_simulation import EgoVehicleSimulation


class ConstantRewardComputer(BaseRewardComputer):
    """
    Returns a constant reward at each time-step. If negative,
    this corresponds to a living penalty, which can be used to
    incentivise the agent to make progress.
    """
    def __init__(self, reward: float) -> None:
        self.reward = reward
        super().__init__()

    def __call__(
        self,
        action: np.ndarray,
        simulation: EgoVehicleSimulation,
        data: CommonRoadData
    ) -> float:
        return self.reward
