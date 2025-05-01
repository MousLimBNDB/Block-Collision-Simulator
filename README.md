# Block Collision Simulation (BCS)

A Python-based physics simulation that visualizes elastic collisions between two blocks using Pygame and Tkinter. Comes with a GUI to control parameters and observe real-time effects.

---

## 🛠 Features

- Accurate elastic collision physics
- Toggle display options: center of mass, velocity vectors, and trajectories
- GUI for configuring block properties and environment settings
- Preset scenarios for quick demonstrations
- Pause, reset, and reload features

---

## 📦 Requirements

- Python 3.8 or higher
- Pygame (Tkinter is included in Python)

### Install with pip:
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

1. Open a terminal and navigate to the project folder.
2. Start the control panel (GUI):

```bash
python simulation_interface.py
```

3. Use the GUI to:
   - Set masses, velocities, and other physics parameters
   - Start, pause, or reset the simulation
   - Choose display options (vectors, trajectories, center of mass)

4. The simulation will open in a separate Pygame window.

---

## 🎮 Controls in the Simulation Window

| Key     | Action                        |
|---------|-------------------------------|
| Space   | Pause / Resume simulation     |
| R       | Reset simulation              |
| C       | Toggle center of mass display |
| V       | Toggle velocity vectors       |
| T       | Toggle trajectories           |
| Esc     | Exit simulation               |

---

## 🗂 Project Structure

```
BCS/
├── BCS.py               # Basic script version
├── BCSv2.py             # Improved version
├── BCSv3/
│   ├── block_collision_sim.py
│   └── simulation_interface.py
├── BCSv4/
│   ├── block_collision_sim.py
│   └── simulation_interface.py
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 📄 License

This project is released under the **MIT License**.

Feel free to use, modify, and share it.
```

Let me know if you want to include screenshots or GIFs of the simulation!
