from crgeo_learning.reinforcement.constants import COMMONROAD_GYM_ENV_ENTRY_POINT, COMMONROAD_GYM_ENV_ID
from crgeo_learning.reinforcement.training.rl_trainer import RLTrainer
from crgeo_learning.reinforcement.commonroad_gym_env import CommonRoadGymEnv, RLEnvironmentOptions, CommonRoadGymStepInfo

from gym.envs.registration import register

register(
    id=COMMONROAD_GYM_ENV_ID,
    entry_point=COMMONROAD_GYM_ENV_ENTRY_POINT,
)