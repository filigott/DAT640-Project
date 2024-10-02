from dialoguekit.platforms import FlaskSocketPlatform
from sample_agents.parrot_agent import ParrotAgent

def test_parrot():
    platform = FlaskSocketPlatform(ParrotAgent)
    platform.start()

if __name__ == '__main__':
    test_parrot()