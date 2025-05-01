import tkinter as tk
from tkinter import ttk
import sys
import subprocess
import threading
import os

class SimulationControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Collision Simulation Controls")
        self.root.geometry("600x680")
        self.root.resizable(False, False)
        
        # Set up styles
        self.setup_styles()
        
        # Create main frames
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.create_parameter_sections()
        self.create_buttons_section()
        
        # Process reference
        self.sim_process = None
    
    def setup_styles(self):
        """Set up styles for widgets"""
        style = ttk.Style()
        style.configure('TLabelframe', font=('Arial', 10, 'bold'))
        style.configure('TCheckbutton', font=('Arial', 9))
        style.configure('TRadiobutton', font=('Arial', 9))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        
    def create_parameter_sections(self):
        """Create all parameter sections"""
        # Block parameters frame
        self.blocks_frame = ttk.LabelFrame(self.main_frame, text="Block Parameters")
        self.blocks_frame.pack(fill="x", padx=5, pady=5)
        
        # Physics parameters frame
        self.physics_frame = ttk.LabelFrame(self.main_frame, text="Physics Parameters")
        self.physics_frame.pack(fill="x", padx=5, pady=5)
        
        # Display options frame
        self.display_frame = ttk.LabelFrame(self.main_frame, text="Display Options")
        self.display_frame.pack(fill="x", padx=5, pady=5)
        
        # Presets frame
        self.presets_frame = ttk.LabelFrame(self.main_frame, text="Preset Scenarios")
        self.presets_frame.pack(fill="x", padx=5, pady=5)
        
        # Create widgets in each section
        self.create_block_parameters()
        self.create_physics_parameters()
        self.create_display_parameters()
        self.create_presets()
    
    def create_block_parameters(self):
        """Create widgets for block parameters"""
        # Block 1 parameters
        block1_frame = ttk.Frame(self.blocks_frame)
        block1_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(block1_frame, text="Block 1 (Red)", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(block1_frame, text="Mass (kg):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.mass1_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(block1_frame, from_=0.1, to=100.0, increment=0.1, textvariable=self.mass1_var, width=8).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(block1_frame, text="Velocity (m/s):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.vel1_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(block1_frame, from_=-10.0, to=10.0, increment=0.1, textvariable=self.vel1_var, width=8).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(block1_frame, text="Position (pixels):").grid(row=1, column=4, sticky="w", padx=5, pady=2)
        self.pos1_var = tk.IntVar(value=200)
        ttk.Spinbox(block1_frame, from_=0, to=700, increment=10, textvariable=self.pos1_var, width=8).grid(row=1, column=5, padx=5, pady=2)
        
        # Block 2 parameters
        block2_frame = ttk.Frame(self.blocks_frame)
        block2_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(block2_frame, text="Block 2 (Blue)", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(block2_frame, text="Mass (kg):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.mass2_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(block2_frame, from_=0.1, to=100.0, increment=0.1, textvariable=self.mass2_var, width=8).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(block2_frame, text="Velocity (m/s):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.vel2_var = tk.DoubleVar(value=-1.0)
        ttk.Spinbox(block2_frame, from_=-10.0, to=10.0, increment=0.1, textvariable=self.vel2_var, width=8).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(block2_frame, text="Position (pixels):").grid(row=1, column=4, sticky="w", padx=5, pady=2)
        self.pos2_var = tk.IntVar(value=400)
        ttk.Spinbox(block2_frame, from_=0, to=700, increment=10, textvariable=self.pos2_var, width=8).grid(row=1, column=5, padx=5, pady=2)
        
    def create_physics_parameters(self):
        """Create widgets for physics parameters"""
        physics_grid = ttk.Frame(self.physics_frame)
        physics_grid.pack(fill="x", padx=5, pady=5)
        
        row = 0
        # Elasticity
        ttk.Label(physics_grid, text="Elasticity (0-1):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.elasticity_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(physics_grid, from_=0.0, to=1.0, increment=0.05, textvariable=self.elasticity_var, width=8).grid(row=row, column=1, padx=5, pady=3)
        
        # Gravity
        ttk.Label(physics_grid, text="Gravity (m/s²):").grid(row=row, column=2, sticky="w", padx=5, pady=3)
        self.gravity_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(physics_grid, from_=-10.0, to=10.0, increment=0.1, textvariable=self.gravity_var, width=8).grid(row=row, column=3, padx=5, pady=3)
        
        row += 1
        # Time rate
        ttk.Label(physics_grid, text="Time Rate:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.time_rate_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(physics_grid, from_=0.1, to=5.0, increment=0.1, textvariable=self.time_rate_var, width=8).grid(row=row, column=1, padx=5, pady=3)
        
        # Wall damping
        ttk.Label(physics_grid, text="Wall Damping (0-1):").grid(row=row, column=2, sticky="w", padx=5, pady=3)
        self.wall_damping_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(physics_grid, from_=0.0, to=1.0, increment=0.05, textvariable=self.wall_damping_var, width=8).grid(row=row, column=3, padx=5, pady=3)
        
        row += 1
        # Walls configuration
        ttk.Label(physics_grid, text="Walls:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.walls_var = tk.StringVar(value="both")
        ttk.Radiobutton(physics_grid, text="Both Walls", value="both", variable=self.walls_var).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        ttk.Radiobutton(physics_grid, text="Left Wall Only", value="left", variable=self.walls_var).grid(row=row, column=2, sticky="w", padx=5, pady=3)
        ttk.Radiobutton(physics_grid, text="Right Wall Only", value="right", variable=self.walls_var).grid(row=row, column=3, sticky="w", padx=5, pady=3)
        
    def create_display_parameters(self):
        """Create widgets for display parameters"""
        display_frame = ttk.Frame(self.display_frame)
        display_frame.pack(fill="x", padx=5, pady=5)
        
        # Show center of mass
        self.show_cm_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(display_frame, text="Show Center of Mass", variable=self.show_cm_var).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Show velocity vectors
        self.show_vectors_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Show Velocity Vectors", variable=self.show_vectors_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Show trajectories
        self.show_trajectories_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(display_frame, text="Show Trajectories", variable=self.show_trajectories_var).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # Block size
        size_frame = ttk.Frame(self.display_frame)
        size_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(size_frame, text="Block Width:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.block1_width_var = tk.IntVar(value=50)
        ttk.Spinbox(size_frame, from_=20, to=100, increment=5, textvariable=self.block1_width_var, width=8).grid(row=0, column=1, padx=5, pady=3)
        
        ttk.Label(size_frame, text="Block Height:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self.block_height_var = tk.IntVar(value=50)
        ttk.Spinbox(size_frame, from_=20, to=100, increment=5, textvariable=self.block_height_var, width=8).grid(row=0, column=3, padx=5, pady=3)
        
        # Block 2 size difference
        ttk.Label(size_frame, text="Block 2 Size Increase:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.block2_size_diff_var = tk.IntVar(value=10)
        ttk.Spinbox(size_frame, from_=0, to=50, increment=1, textvariable=self.block2_size_diff_var, width=8).grid(row=1, column=1, padx=5, pady=3)
        
        # Screen size
        ttk.Label(size_frame, text="Screen Width:").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        self.screen_width_var = tk.IntVar(value=800)
        ttk.Spinbox(size_frame, from_=600, to=1200, increment=50, textvariable=self.screen_width_var, width=8).grid(row=1, column=3, padx=5, pady=3)
        
        ttk.Label(size_frame, text="Screen Height:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.screen_height_var = tk.IntVar(value=500)
        ttk.Spinbox(size_frame, from_=400, to=800, increment=50, textvariable=self.screen_height_var, width=8).grid(row=2, column=1, padx=5, pady=3)
        
    def create_presets(self):
        """Create widgets for preset scenarios"""
        presets_frame = ttk.Frame(self.presets_frame)
        presets_frame.pack(fill="x", padx=5, pady=5)
        
        self.preset_var = tk.StringVar(value="custom")
        presets = [
            ("Custom", "custom"),
            ("Equal Masses", "equal_masses"),
            ("Light vs Heavy", "light_heavy"),
            ("Pi Approximation", "pi_approx"),
            ("Wall Collisions", "wall"),
            ("Space Race", "space_race")
        ]
        
        for i, (text, value) in enumerate(presets):
            ttk.Radiobutton(presets_frame, text=text, value=value, variable=self.preset_var, command=self.load_preset).grid(
                row=i // 3, column=i % 3, padx=10, pady=5, sticky="w"
            )
    
    def create_buttons_section(self):
        """Create buttons at the bottom"""
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill="x", padx=5, pady=10)
        
        # Start button
        self.start_button = ttk.Button(buttons_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(side="left", padx=5, pady=5)
        
        # Apply button (update running simulation)
        self.apply_button = ttk.Button(buttons_frame, text="Apply Changes", command=self.apply_changes)
        self.apply_button.pack(side="left", padx=5, pady=5)
        # Pause button
        self.pause_button = ttk.Button(buttons_frame, text="Pause/Resume", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=5, pady=5)

        # Reset button
        self.reset_button = ttk.Button(buttons_frame, text="Reset Simulation", command=self.reset_simulation)
        self.reset_button.pack(side="left", padx=5, pady=5)
        
        # Exit button
        self.exit_button = ttk.Button(buttons_frame, text="Exit", command=self.exit_application)
        self.exit_button.pack(side="right", padx=5, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=('Arial', 10, 'italic'))
        self.status_label.pack(side="bottom", padx=5, pady=5)
    
    def get_parameters(self):
        """Get parameters from UI widgets"""
        return {
            'block1_mass': self.mass1_var.get(),
            'block2_mass': self.mass2_var.get(),
            'block1_velocity': self.vel1_var.get(),
            'block2_velocity': self.vel2_var.get(),
            'block1_position': self.pos1_var.get(),
            'block2_position': self.pos2_var.get(),
            'elasticity': self.elasticity_var.get(),
            'gravity': self.gravity_var.get(),
            'time_rate': self.time_rate_var.get(),
            'wall_damping': self.wall_damping_var.get(),
            'show_cm': self.show_cm_var.get(),
            'show_vectors': self.show_vectors_var.get(),
            'show_trajectories': self.show_trajectories_var.get(),
            'walls': self.walls_var.get(),
            'block1_width': self.block1_width_var.get(),
            'block2_width': self.block1_width_var.get() + self.block2_size_diff_var.get(),
            'block_height': self.block_height_var.get(),
            'screen_width': self.screen_width_var.get(),
            'screen_height': self.screen_height_var.get(),
        }
    
    def load_preset(self):
        """Load preset scenario"""
        preset = self.preset_var.get()
        
        if preset == "equal_masses":
            # Two equal masses, one moving
            self.mass1_var.set(1.0)
            self.mass2_var.set(1.0)
            self.vel1_var.set(1.0)
            self.vel2_var.set(0.0)
            self.pos1_var.set(200)
            self.pos2_var.set(400)
            self.elasticity_var.set(1.0)
            self.gravity_var.set(0.0)
            self.walls_var.set("both")
            
        elif preset == "light_heavy":
            # Light block hitting heavy block
            self.mass1_var.set(0.5)
            self.mass2_var.set(5.0)
            self.vel1_var.set(1.0)
            self.vel2_var.set(0.0)
            self.pos1_var.set(200)
            self.pos2_var.set(400)
            self.elasticity_var.set(1.0)
            self.gravity_var.set(0.0)
            self.walls_var.set("both")
            
        elif preset == "pi_approx":
            # Pi approximation setup (many collisions)
            self.mass1_var.set(1.0)
            self.mass2_var.set(100.0)
            self.vel1_var.set(0.0)
            self.vel2_var.set(-0.1)
            self.pos1_var.set(100)
            self.pos2_var.set(400)
            self.elasticity_var.set(1.0)
            self.gravity_var.set(0.0)
            self.time_rate_var.set(2.0)
            self.walls_var.set("left")
            
        elif preset == "wall":
            # Wall collisions
            self.mass1_var.set(1.0)
            self.mass2_var.set(1.0)
            self.vel1_var.set(1.0)
            self.vel2_var.set(-1.0)
            self.pos1_var.set(50)
            self.pos2_var.set(700)
            self.elasticity_var.set(1.0)
            self.wall_damping_var.set(0.95)
            self.walls_var.set("both")
            
        elif preset == "space_race":
            # Block 2 chasing block 1
            self.mass1_var.set(1.0)
            self.mass2_var.set(2.0)
            self.vel1_var.set(0.5)
            self.vel2_var.set(0.8)
            self.pos1_var.set(600)
            self.pos2_var.set(100)
            self.elasticity_var.set(1.0)
            self.gravity_var.set(0.0)
            self.walls_var.set("right")
            self.show_trajectories_var.set(True)
        
        self.status_var.set(f"Preset '{preset}' loaded")
    
    def write_params_to_file(self):
        """Write parameters to a file for the simulation to read"""
        params = self.get_parameters()
        with open("simulation_params.txt", "w") as f:
            for key, value in params.items():
                f.write(f"{key}={value}\n")
        return params
    
    def start_simulation(self):
        """Start the simulation with current parameters"""
        if self.sim_process and self.sim_process.poll() is None:
            self.status_var.set("Simulation already running")
            return
            
        params = self.write_params_to_file()
        
        # Start the simulation process
        try:
            self.sim_process = subprocess.Popen([sys.executable, "block_collision_sim.py"])
            self.status_var.set("Simulation started")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def apply_changes(self):
        """Apply parameter changes to running simulation"""
        if not self.sim_process or self.sim_process.poll() is not None:
            self.status_var.set("No simulation running")
            return
            
        params = self.write_params_to_file()
        
        # Signal the simulation to reload parameters
        try:
            with open("simulation_command.txt", "w") as f:
                f.write("reload")
            self.status_var.set("Changes applied")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def reset_simulation(self):
        """Reset the simulation with current parameters"""
        if not self.sim_process or self.sim_process.poll() is not None:
            self.status_var.set("No simulation running")
            return
            
        params = self.write_params_to_file()
        
        # Signal the simulation to reset
        try:
            with open("simulation_command.txt", "w") as f:
                f.write("reset")
            self.status_var.set("Simulation reset")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def toggle_pause(self):
        if not self.sim_process or self.sim_process.poll() is not None:
            self.status_var.set("No simulation running")
            return
        try:
            with open("simulation_command.txt", "w") as f:
                f.write("pause")
            self.status_var.set("Toggled pause")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

    def exit_application(self):
        """Clean exit the application"""
        # Stop the simulation if running
        if self.sim_process and self.sim_process.poll() is None:
            try:
                with open("simulation_command.txt", "w") as f:
                    f.write("exit")
                # Give it a moment to clean up
                self.sim_process.wait(timeout=1)
            except:
                # Force kill if it doesn't shut down gracefully
                self.sim_process.kill()
        
        # Clean up temporary files
        for file in ["simulation_params.txt", "simulation_command.txt"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationControlPanel(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_application)
    root.mainloop()