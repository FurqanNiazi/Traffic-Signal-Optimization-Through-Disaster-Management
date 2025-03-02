# Traffic Lights Simulation

This project simulates a traffic light system at an intersection using Pygame for visualization and Google Generative AI for decision-making. The simulation includes various types of vehicles, including emergency vehicles, and dynamically adjusts traffic light timings based on real-time traffic conditions.

## Features

- **Traffic Light Control**: Simulates traffic lights with green, yellow, and red signals.
- **Vehicle Simulation**: Includes different types of vehicles such as cars, buses, trucks, bikes, ambulances, and fire trucks.
- **Emergency Vehicle Priority**: Prioritizes emergency vehicles (ambulances and fire trucks) in traffic light decisions.
- **Dynamic Signal Timing**: Adjusts traffic light durations based on the number of vehicles and their wait times.
- **AI Integration**: Uses Google Generative AI to make decisions about traffic light timings based on current traffic conditions.
- **Pygame Visualization**: Visualizes the traffic simulation using Pygame.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/traffic-lights-simulation.git
    cd traffic-lights-simulation
    ```

2. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure the Google Generative AI API**:
    - Replace the placeholder API key in [simulation.py](http://_vscodecontentref_/0) with your actual API key:
      
```python      genai.configure(api_key="YOUR_API_KEY")
 ```

## Usage

1. **Run the simulation**:
    ```bash
    python simulation.py
    ```

2. **Simulation Controls**:
    - The simulation will start automatically and display the intersection with traffic lights and vehicles.
    - The traffic lights will change based on the AI decisions and the current traffic conditions.

## File Structure

- [simulation.py](http://_vscodecontentref_/1): Main script that runs the traffic simulation.
- [images](http://_vscodecontentref_/2): Directory containing images for the intersection, traffic lights, and vehicles.
- `requirements.txt`: List of required Python packages.

## Code Overview

### Main Components

- **TrafficSignal Class**: Manages the state of traffic signals.
- **Vehicle Class**: Manages the state and behavior of vehicles, including movement and rendering.
- **initialize Function**: Initializes traffic signals with default values and starts the simulation loop.
- **repeat Function**: Manages the traffic signal cycle, switching between green and yellow signals.
- **updateValues Function**: Updates the signal timers every second.
- **generateVehicles Function**: Continuously generates vehicles in random lanes and directions.
- **get_traffic_state Function**: Collects the current state of traffic, including vehicle counts and wait times.
- **get_decision_from_ai Function**: Uses Google Generative AI to decide the next green signal based on the current traffic state.
- **Main Class**: Initializes threads for signal initialization, vehicle generation, and AI decision-making. Manages the Pygame display loop, rendering the background, signals, and vehicles.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [Pygame](https://www.pygame.org/) for the game development library.
- [Google Generative AI](https://cloud.google.com/generative-ai) for AI decision-making.
