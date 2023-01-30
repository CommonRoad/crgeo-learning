import numpy as np

from crgeo.dataset.commonroad_data import CommonRoadData
from crgeo_learning.reinforcement.rewarder.reward_computer.base_reward_computer import BaseRewardComputer
from crgeo.simulation.ego_simulation.ego_vehicle_simulation import EgoVehicleSimulation


class OffroutePenaltyRewardComputer(BaseRewardComputer):
    def __init__(self, penalty: float) -> None:
        self._penalty = penalty
        super().__init__()

    def __call__(
        self,
        action: np.ndarray,
        simulation: EgoVehicleSimulation,
        data: CommonRoadData
    ) -> float:
        if simulation.check_if_offroute():
            return self._penalty
        return 0.0
