import asyncio
from app.simulation.user_sim_agent import UserSimAgent
from app.simulation.user_sim_profiles import user_profiles

async def run_user_simulations():
    ws_url = "ws://localhost:8000/ws"
    
    # Create a list of tasks, each running a simulation for one user
    tasks = []
    for profile in user_profiles:
        user_simulator = UserSimAgent(profile, profile.id, ws_url)
        tasks.append(user_simulator.simulate_conversation())

    # Run all simulations concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Run all user simulations concurrently
    asyncio.run(run_user_simulations())
