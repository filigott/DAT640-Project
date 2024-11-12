import asyncio
from app.simulation.user_sim_agent import UserSimAgent
from app.simulation.user_sim_profiles import user_profiles

async def run_user_simulations():
    ws_url = "ws://localhost:8000/ws"
    
    # Store original instances to retrieve updated states later
    user_simulators = [UserSimAgent(profile, profile.id, ws_url) for profile in user_profiles]
    
    # Create a list of tasks, each running a simulation for one user
    tasks = [user_simulator.simulate_conversation() for user_simulator in user_simulators]
    
    # Run all simulations concurrently
    await asyncio.gather(*tasks)

    # After all simulations are done, show a summary
    print("\nSimulation Summary:")
    for user_simulator in user_simulators:
        summary = user_simulator.get_summary()
        print(f"User ID: {summary['user_id']}, Goal: {summary['goal']}, "
              f"Actions Taken: {summary['actions_taken']}, "
              f"Songs Added to Playlist: {summary['songs_added_to_playlist']}, "
              f"Completed: {summary['completed']}")

if __name__ == "__main__":
    # Run all user simulations concurrently
    asyncio.run(run_user_simulations())
