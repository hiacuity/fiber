import gym
import time
from functools import partial
from fiber.managers import AsyncManager, SyncManager

NUM_ENVS = 4
STEPS = 5000

class EnvSyncManager(SyncManager):
    pass

class EnvAsyncManager(AsyncManager):
    pass

def sync_manager():
    EnvManager = EnvSyncManager

    create_cart_pole = partial(gym.make, "CartPole-v1")
    local_env = create_cart_pole()
    EnvManager.register("CartPoleEnv", create_cart_pole)

    managers = [EnvManager() for _ in range(NUM_ENVS)]
    [manager.start() for manager in managers]

    envs = [manager.CartPoleEnv() for manager in managers]
    [env.reset() for env in envs]

    for _ in range(STEPS):
        actions = [local_env.action_space.sample() for _ in range(len(envs))]
        results = [env.step(action) for env, action in zip(envs, actions)]
        for j in range(len(results)):
            observation, reward, done, info = results[j]
            if done:
                envs[j].reset()
        if not envs:
            break

def async_manager():
    EnvManager = EnvAsyncManager
    create_cart_pole = partial(gym.make, "CartPole-v1")
    local_env = create_cart_pole()
    EnvManager.register("CartPoleEnv", create_cart_pole)

    managers = [EnvManager() for _ in range(NUM_ENVS)]
    [manager.start() for manager in managers]

    envs = [manager.CartPoleEnv() for manager in managers]
    [env.reset() for env in envs]

    for _ in range(STEPS):
        actions = [local_env.action_space.sample() for _ in range(len(envs))]
        handles = [env.step(action) for env, action in zip(envs, actions)]
        results = [handle.get() for handle in handles]
        for j in range(len(results)):
            observation, reward, done, info = results[j]
            if done:
                envs[j].reset()
        if not envs:
            break

def main():
    start = time.time()
    sync_manager()
    print(f"Sync manager took {time.time() - start}s")

    start = time.time()
    async_manager()
    print(f"Async manager took {time.time() - start}s")

if __name__ == '__main__':
    main()
