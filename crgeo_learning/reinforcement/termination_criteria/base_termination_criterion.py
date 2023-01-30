from abc import ABC, abstractmethod
from typing import Optional, Set, Tuple

from crgeo.common.class_extensions.auto_repr_mixin import AutoReprMixin
from crgeo.common.class_extensions.class_property_decorator import classproperty
from crgeo.common.class_extensions.safe_pickling_mixin import SafePicklingMixin
from crgeo.common.class_extensions.string_resolver_mixing import StringResolverMixin
from crgeo.common.utils.string import rchop
from crgeo.simulation.ego_simulation.ego_vehicle_simulation import EgoVehicleSimulation


class BaseTerminationCriterion(ABC, SafePicklingMixin, AutoReprMixin, StringResolverMixin):
    @abstractmethod
    def __call__(
        self,
        simulation: EgoVehicleSimulation
    ) -> Tuple[bool, Optional[str]]:
        ...

    @classproperty
    def _name(cls) -> str:
        return rchop(cls.__name__, 'Criterion')  # type: ignore

    @property
    def name(self) -> str:
        return self._name  # type: ignore

    @property
    @abstractmethod
    def reasons(self) -> Set[str]:
        ...
