import numpy as np

from crgeo.dataset.commonroad_data import CommonRoadData
from crgeo_learning.reinforcement.rewarder.reward_computer.base_reward_computer import BaseRewardComputer
from crgeo.simulation.ego_simulation.ego_vehicle_simulation import EgoVehicleSimulation


class StillStandingPenaltyRewardComputer(BaseRewardComputer):
    def __init__(self, penalty: float, velocity_threshold: float = 1.0) -> None:
        self._penalty = penalty
        self._velocity_threshold = velocity_threshold
        super().__init__()

    def __call__(
        self,
        action: np.ndarray,
        simulation: EgoVehicleSimulation,
        data: CommonRoadData
    ) -> float:
        if abs(simulation.ego_vehicle.state.velocity) < self._velocity_threshold:
            return self._penalty
        return 0.0
