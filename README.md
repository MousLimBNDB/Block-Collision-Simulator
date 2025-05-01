
## Features of the Simulation

1. **Tkinter Control Panel**:
    - Input parameters for both blocks (mass, velocity, position)
    - Adjust physics parameters (elasticity, gravity, time rate)
    - Toggle display options (center of mass, velocity vectors)
    - Preset scenarios for common experiments
    - Buttons to start, reset, and apply changes to the simulation
2. **Pygame Visualization**:
    - Real-time visualization of the blocks with proper sizing based on mass
    - Velocity vectors showing direction and magnitude
    - Center of mass tracking (optional)
    - Status display showing time, collisions, and block properties
    - Keyboard controls (space to pause, r to reset, c to toggle CM, v to toggle vectors)
3. **Physics Features**:
    - Perfectly elastic collisions with adjustable elasticity
    - Conservation of momentum and energy
    - Adjustable time rate to speed up or slow down the simulation
    - Wall collisions with adjustable damping
    - Support for gravity (can be set to zero)

## How to Run the Simulation

1. Make sure you have Python installed along with Pygame and Tkinter
2. Save the code to a file (e.g., `block_collision.py`)
3. Run the script: `python block_collision.py`
4. Use the Tkinter interface to set your parameters and click "Start Simulation"

## Preset Scenarios

I've included some interesting preset scenarios:

1. **Equal Masses**: Two equal mass blocks, one moving toward a stationary one
2. **Light vs Heavy**: A light block hitting a heavy stationary block
3. **Pi Approximation**: Setup to demonstrate how block collisions can calculate π
4. **Wall Collisions**: Both blocks moving with wall collisions enabled

## Try It Out!

The simulation allows you to recreate various physics experiments. For example, try the "Pi Approximation" preset - if you count the number of collisions between the blocks and the wall when the mass ratio is 100:1, it will approach π!
