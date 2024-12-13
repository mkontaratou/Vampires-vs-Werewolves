# Vampire vs Werewolves

## About
This project involves developing a heuristic to play the Vampire vs Werewolves game. The AI uses strategic algorithms to control either Vampires or Werewolves, aiming to dominate the grid-based universe by converting humans and defeating the opposing species. The project tests your ability to implement effective AI strategies while considering opponent moves and game mechanics.

## Rules: 
Universe Representation

The game is played on an n x m grid. Vampires and Werewolves each start in a single cell with all their creatures. Creatures can move in 8 directions (adjacent cells).

Movements must follow these rules:

- At least one move per turn is mandatory.

- Only your own species' groups can be moved.

- A cell cannot be both the source and target in the same turn.

- To convert humans, your creatures must equal or exceed the number of humans in the cell.

- To attack enemies, your creatures must outnumber them by 1.5 times.

### Random Battles

If insufficient creatures are available to convert or attack, a random battle occurs:

Win Probability: Depends on the ratio of attacking to defending creatures.

Survivors: Based on probabilities, attackers and defenders may lose creatures.

## How to play :
1. Download Docker Desktop
2. Set Up the AI Environment, make sure you have python installed with numpy. Activate your environment:
   ```sh
   source venv/bin/activate
    ```
3. Run the Server:
   ```sh
   >>docker run -p 5555:5555 -p 8080:8080 -v /path/to/maps:/maps vamps-server -map /maps/testmap2.xml
   ```
4. Run the AI, open two terminal windows and on each one write the following to activate each player: 
   ```sh
    >>python -m main localhost 5555 name
    >>python -m main localhost 5555 another_agent_name    
   ```
