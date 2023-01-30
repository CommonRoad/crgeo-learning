from typing import Optional, Set, Tuple

from crgeo_learning.reinforcement.termination_criteria.base_termination_criterion import BaseTerminationCriterion
from crgeo.simulation.ego_simulation.ego_vehicle_simulation import EgoVehicleSimulation


class ReachedGoalCriterion(BaseTerminationCriterion):
    def __call__(
        self,
        simulation: EgoVehicleSimulation
    ) -> Tuple[bool, Optional[str]]:
        reached_goal = simulation.check_if_has_reached_goal()
        return reached_goal, 'ReachedGoal' if reached_goal else None

    @property
    def reasons(self) -> Set[str]:
        return {'ReachedGoal'}
