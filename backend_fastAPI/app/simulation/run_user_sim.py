import asyncio
from app.simulation.user_sim_agent import UserSimAgent
from app.simulation.user_sim_profiles import user_profiles

async def run_user_simulations(sequential=True, num_profiles=None):
    ws_url = "ws://localhost:8000/ws"
    
    # Determine the subset of profiles to use
    if num_profiles is None or num_profiles > len(user_profiles):
        selected_profiles = user_profiles
    else:
        selected_profiles = user_profiles[:num_profiles]
    
    # Create user simulators based on selected profiles
    user_simulators = [UserSimAgent(profile, profile.id, ws_url) for profile in selected_profiles]
    
    if sequential:
        # Run simulations one after another
        for user_simulator in user_simulators:
            await user_simulator.simulate_conversation(sequential)
    else:
        # Run simulations concurrently
        tasks = [user_simulator.simulate_conversation(sequential) for user_simulator in user_simulators]
        await asyncio.gather(*tasks)

    # After all simulations are done, show a summary
    print("\nSimulation Summary:")
    for user_simulator in user_simulators:
        summary = user_simulator.get_summary()
        print(f"User ID: {summary['user_id']}, Goal: {summary['goal']}, "
              f"Actions Taken: {summary['actions_taken']}, "
              f"Songs Added to Playlist: {summary['songs_added_to_playlist']}, "
              f"Number of questions asked: {summary['num_questions_asked']}, "
              f"Completed: {summary['completed']}")

if __name__ == "__main__":
    # Set parameters for the simulation run
    sequential = True
    num_profiles = 10
    asyncio.run(run_user_simulations(sequential=sequential, num_profiles=num_profiles))
