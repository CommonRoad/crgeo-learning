from typing import Type
from crgeo.common.config import Config
from crgeo.dataset.extraction.traffic.traffic_extractor_factory import TrafficExtractorFactory

from crgeo_learning.geometric.base_geometric import BaseGeometric
from crgeo_learning.geometric.project.base_geometric_project import BaseGeometricProject
from crgeo_learning.geometric.training.experiment import GeometricExperiment
from crgeo.common.io_extensions.scenario import LaneletAssignmentStrategy
from crgeo.dataset.collection.scenario_dataset_collector import ScenarioDatasetCollector
from crgeo.dataset.extraction.traffic.edge_drawers.implementations import VoronoiEdgeDrawer
from crgeo.dataset.extraction.traffic.traffic_extractor import TrafficExtractorOptions
from crgeo_learning.geometric.training.experiment import GeometricExperimentConfig
from crgeo.simulation.interfaces.static.scenario_simulation import ScenarioSimulationOptions
from crgeo_learning.base_project import register_run_command

from projects.geometric_models.dummy.model import DummyModel


class DummyProject(BaseGeometricProject):

    def configure_experiment(self, cfg: Config) -> GeometricExperimentConfig:
        return GeometricExperimentConfig(
            extractor_factory=TrafficExtractorFactory(
                options=TrafficExtractorOptions(
                    edge_drawer=VoronoiEdgeDrawer(dist_threshold=cfg["dist_threshold_v2v"])
                ),
            ),
            data_collector_cls=ScenarioDatasetCollector,
            preprocessors=[],
            postprocessors=[],
            simulation_options=ScenarioSimulationOptions(
                lanelet_assignment_order=LaneletAssignmentStrategy.ONLY_SHAPE,
                collision_checking=False
            )
        )

    def configure_model(self, cfg: Config, experiment: GeometricExperiment) -> Type[BaseGeometric]:
        return DummyModel

    @register_run_command
    def custom(self) -> None:
        print("You can register custom run modes like this")
