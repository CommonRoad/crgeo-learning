import numpy as np

from crgeo.dataset.commonroad_data import CommonRoadData
from crgeo_learning.reinforcement.rewarder.reward_computer.base_reward_computer import BaseRewardComputer
from crgeo.simulation.ego_simulation.ego_vehicle_simulation import EgoVehicleSimulation


class ReachedGoalRewardComputer(BaseRewardComputer):
    def __init__(self, reward: float) -> None:
        self._reward = reward
        super().__init__()

    def __call__(
        self,
        action: np.ndarray,
        simulation: EgoVehicleSimulation,
        data: CommonRoadData
    ) -> float:
        if simulation.check_if_has_reached_goal():
            return self._reward
        return 0.0
