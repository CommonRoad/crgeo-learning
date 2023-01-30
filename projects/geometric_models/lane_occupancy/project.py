from typing import Type

from crgeo.common.io_extensions.scenario import LaneletAssignmentStrategy
from crgeo.dataset.collection.scenario_dataset_collector import ScenarioDatasetCollector
from crgeo.dataset.extraction.traffic.edge_drawers.implementations.no_edge_drawer import NoEdgeDrawer
from crgeo.dataset.extraction.traffic.feature_computers.implementations.defaults import DefaultFeatureComputers
from crgeo.dataset.extraction.traffic.feature_computers.implementations.vehicle_to_lanelet.vehicle_lanelet_pose_feature_computer import VehicleLaneletPoseEdgeFeatureComputer
from crgeo.dataset.extraction.traffic.traffic_extractor import TrafficExtractorOptions, TrafficFeatureComputerOptions
from crgeo.dataset.extraction.traffic.traffic_extractor_factory import TrafficExtractorFactory
from crgeo.dataset.postprocessing.implementations.lanelet_occupancy_post_processor import LaneletOccupancyPostProcessor
from crgeo_learning.geometric.base_geometric import BaseGeometric
from crgeo_learning.geometric.project.base_geometric_project import BaseGeometricProject
from crgeo_learning.geometric.training.experiment import GeometricExperiment, GeometricExperimentConfig
from crgeo.simulation.interfaces.static.scenario_simulation import ScenarioSimulationOptions
from projects.geometric_models.lane_occupancy.models.occupancy.occupancy_model import OccupancyModel


class LaneOccupancyProject(BaseGeometricProject):
    def configure_experiment(self, cfg: dict) -> GeometricExperimentConfig:
        return GeometricExperimentConfig(
            extractor_factory=TrafficExtractorFactory(
                TrafficExtractorOptions(
                    edge_drawer=NoEdgeDrawer(),
                    feature_computers=TrafficFeatureComputerOptions(
                        v=DefaultFeatureComputers.v(),
                        v2v=DefaultFeatureComputers.v2v(),
                        l=DefaultFeatureComputers.l(),
                        l2l=DefaultFeatureComputers.l2l(),
                        v2l=[VehicleLaneletPoseEdgeFeatureComputer()],
                        l2v=DefaultFeatureComputers.l2v()
                    )
                ),
            ),
            data_collector_cls=ScenarioDatasetCollector,
            preprocessors=[],
            postprocessors=[LaneletOccupancyPostProcessor(
                time_horizon=cfg["time_horizon"],
                discretization_resolution=None,
                min_occupancy_ratio=cfg["min_occupancy_ratio"]
            )],
            simulation_options=ScenarioSimulationOptions(
                lanelet_assignment_order=LaneletAssignmentStrategy.ONLY_SHAPE,
                collision_checking=False
            )
        )

    def configure_model(self, cfg: dict, experiment: GeometricExperiment) -> Type[BaseGeometric]:
        return OccupancyModel

