import pygame
import sys
import tkinter as tk
from tkinter import ttk
import math
import numpy as np

class PhysicsSimulation:
    def __init__(self, params=None):
        # Default parameters (similar to those on the website)
        self.params = {
            'block1_mass': 1.0,        # kg
            'block2_mass': 2.0,        # kg
            'block1_velocity': 0.0,    # m/s
            'block2_velocity': -1.0,   # m/s
            'block1_position': 200,    # pixels (from left)
            'block2_position': 400,    # pixels (from left)
            'elasticity': 1.0,         # perfect elasticity
            'gravity': 0.0,            # m/s^2
            'time_rate': 1.0,          # simulation speed multiplier
            'wall_damping': 1.0,       # wall elasticity
            'show_cm': False,          # show center of mass
            'show_vectors': True,      # show velocity vectors
        }
        
        # Update with provided parameters
        if params:
            self.params.update(params)
            
        # Simulation state
        self.collisions = 0
        self.time = 0
        self.paused = False
        self.block_height = 50
        self.floor_height = 100
        
        # Scale factors (pixels per meter)
        self.scale = 100
        
        # Calculate block widths based on mass (for visualization)
        self.block1_width = max(30, int(30 * math.sqrt(self.params['block1_mass'])))
        self.block2_width = max(30, int(30 * math.sqrt(self.params['block2_mass'])))
        
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption('Block Collision Simulation')
        self.width, self.height = 800, 500
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (200, 200, 200)
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        
    def calculate_cm_position(self):
        """Calculate the center of mass position"""
        m1 = self.params['block1_mass']
        m2 = self.params['block2_mass']
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        
        return (m1 * x1 + m2 * x2) / (m1 + m2)
    
    def calculate_cm_velocity(self):
        """Calculate the center of mass velocity"""
        m1 = self.params['block1_mass']
        m2 = self.params['block2_mass']
        v1 = self.params['block1_velocity']
        v2 = self.params['block2_velocity']
        
        return (m1 * v1 + m2 * v2) / (m1 + m2)
    
    def check_collision(self):
        """Check for and handle collisions between blocks"""
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        
        # Check collision between blocks
        if x1 + self.block1_width >= x2:
            # Calculate new velocities
            m1 = self.params['block1_mass']
            m2 = self.params['block2_mass']
            v1 = self.params['block1_velocity']
            v2 = self.params['block2_velocity']
            e = self.params['elasticity']
            
            # Elastic collision formula
            v1_new = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2)
            v2_new = ((1+e)*m1*v1 + (m2 - e*m1)*v2) / (m1 + m2)
            
            self.params['block1_velocity'] = v1_new
            self.params['block2_velocity'] = v2_new
            
            # Move blocks apart to prevent sticking
            overlap = (x1 + self.block1_width) - x2
            self.params['block1_position'] -= overlap/2
            self.params['block2_position'] += overlap/2
            
            self.collisions += 1
            return True
        
        return False
    
    def check_wall_collision(self):
        """Check for and handle wall collisions"""
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        
        # Left wall collision for block 1
        if x1 <= 0:
            self.params['block1_velocity'] *= -self.params['wall_damping']
            self.params['block1_position'] = 0
            self.collisions += 1
            return True
        
        # Right wall collision for block 2
        if x2 + self.block2_width >= self.width:
            self.params['block2_velocity'] *= -self.params['wall_damping']
            self.params['block2_position'] = self.width - self.block2_width
            self.collisions += 1
            return True
            
        return False
    
    def update(self, dt):
        """Update simulation state"""
        if self.paused:
            return
            
        # Apply time rate
        dt *= self.params['time_rate']
        self.time += dt
        
        # Update positions
        self.params['block1_position'] += self.params['block1_velocity'] * dt * self.scale
        self.params['block2_position'] += self.params['block2_velocity'] * dt * self.scale
        
        # Apply gravity
        if self.params['gravity'] != 0:
            self.params['block1_velocity'] += self.params['gravity'] * dt
            self.params['block2_velocity'] += self.params['gravity'] * dt
            
        # Check for collisions
        self.check_collision()
        self.check_wall_collision()
    
    def draw(self):
        """Draw the simulation"""
        # Fill background
        self.screen.fill(self.WHITE)
        
        # Draw floor
        floor_y = self.height - self.floor_height
        pygame.draw.rect(self.screen, self.GRAY, (0, floor_y, self.width, self.floor_height))
        
        # Block positions
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        y = floor_y - self.block_height
        
        # Draw blocks
        pygame.draw.rect(self.screen, self.RED, (x1, y, self.block1_width, self.block_height))
        pygame.draw.rect(self.screen, self.BLUE, (x2, y, self.block2_width, self.block_height))
        
        # Draw block outlines
        pygame.draw.rect(self.screen, self.BLACK, (x1, y, self.block1_width, self.block_height), 2)
        pygame.draw.rect(self.screen, self.BLACK, (x2, y, self.block2_width, self.block_height), 2)
        
        # Blocks' center positions for velocity vectors
        center1 = (x1 + self.block1_width / 2, y + self.block_height / 2)
        center2 = (x2 + self.block2_width / 2, y + self.block_height / 2)
        
        # Draw velocity vectors if enabled
        if self.params['show_vectors']:
            # Scale vectors for visibility
            vector_scale = 20
            
            # Block 1 velocity vector
            end1 = (center1[0] + self.params['block1_velocity'] * vector_scale, center1[1])
            pygame.draw.line(self.screen, self.GREEN, center1, end1, 3)
            # Arrow head
            if self.params['block1_velocity'] != 0:
                direction = 1 if self.params['block1_velocity'] > 0 else -1
                pygame.draw.polygon(self.screen, self.GREEN, [
                    (end1[0], end1[1]),
                    (end1[0] - direction * 8, end1[1] - 4),
                    (end1[0] - direction * 8, end1[1] + 4)
                ])
            
            # Block 2 velocity vector
            end2 = (center2[0] + self.params['block2_velocity'] * vector_scale, center2[1])
            pygame.draw.line(self.screen, self.GREEN, center2, end2, 3)
            # Arrow head
            if self.params['block2_velocity'] != 0:
                direction = 1 if self.params['block2_velocity'] > 0 else -1
                pygame.draw.polygon(self.screen, self.GREEN, [
                    (end2[0], end2[1]),
                    (end2[0] - direction * 8, end2[1] - 4),
                    (end2[0] - direction * 8, end2[1] + 4)
                ])
        
        # Draw center of mass if enabled
        if self.params['show_cm']:
            cm_pos = self.calculate_cm_position()
            cm_vel = self.calculate_cm_velocity()
            
            # Draw CM point
            pygame.draw.circle(self.screen, self.YELLOW, (cm_pos, y + self.block_height / 2), 6)
            
            # Draw CM velocity vector
            if self.params['show_vectors']:
                cm_end = (cm_pos + cm_vel * 20, y + self.block_height / 2)
                pygame.draw.line(self.screen, self.YELLOW, (cm_pos, y + self.block_height / 2), cm_end, 2)
        
        # Display simulation info
        info_text = [
            f"Time: {self.time:.2f}s",
            f"Collisions: {self.collisions}",
            f"Block 1 - Mass: {self.params['block1_mass']}kg, Velocity: {self.params['block1_velocity']:.2f}m/s",
            f"Block 2 - Mass: {self.params['block2_mass']}kg, Velocity: {self.params['block2_velocity']:.2f}m/s",
            f"Center of Mass Velocity: {self.calculate_cm_velocity():.4f}m/s"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = self.font.render(text, True, self.BLACK)
            self.screen.blit(text_surface, (10, 10 + i * 25))
        
        # Paused indicator
        if self.paused:
            pause_text = self.font.render("PAUSED", True, self.RED)
            self.screen.blit(pause_text, (self.width - 100, 10))
            
        pygame.display.flip()
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
    
    def reset(self, params=None):
        """Reset the simulation with new parameters"""
        if params:
            self.params.update(params)
        self.collisions = 0
        self.time = 0
        
        # Recalculate block widths based on mass
        self.block1_width = max(30, int(30 * math.sqrt(self.params['block1_mass'])))
        self.block2_width = max(30, int(30 * math.sqrt(self.params['block2_mass'])))
    
    def toggle_cm(self):
        """Toggle center of mass display"""
        self.params['show_cm'] = not self.params['show_cm']
    
    def toggle_vectors(self):
        """Toggle velocity vectors display"""
        self.params['show_vectors'] = not self.params['show_vectors']
    
    def run(self):
        """Main simulation loop"""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # time in seconds
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toggle_pause()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_c:
                        self.toggle_cm()
                    elif event.key == pygame.K_v:
                        self.toggle_vectors()
            
            self.update(dt)
            self.draw()
        
        pygame.quit()


class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Collision Simulation Controls")
        self.root.geometry("500x600")
        
        # Create frames
        self.params_frame = ttk.LabelFrame(root, text="Simulation Parameters")
        self.params_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.buttons_frame = ttk.Frame(root)
        self.buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Create widgets for parameters
        self.create_parameter_widgets()
        
        # Create buttons
        self.create_buttons()
        
        # Create simulation instance
        self.sim = None
    
    def create_parameter_widgets(self):
        # Mass parameters
        ttk.Label(self.params_frame, text="Block 1 Mass (kg):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.mass1_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(self.params_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.mass1_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.params_frame, text="Block 2 Mass (kg):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.mass2_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(self.params_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.mass2_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Velocity parameters
        ttk.Label(self.params_frame, text="Block 1 Velocity (m/s):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.vel1_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(self.params_frame, from_=-10.0, to=10.0, increment=0.1, textvariable=self.vel1_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.params_frame, text="Block 2 Velocity (m/s):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.vel2_var = tk.DoubleVar(value=-1.0)
        ttk.Spinbox(self.params_frame, from_=-10.0, to=10.0, increment=0.1, textvariable=self.vel2_var, width=10).grid(row=3, column=1, padx=5, pady=5)
        
        # Position parameters
        ttk.Label(self.params_frame, text="Block 1 Position (pixels):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.pos1_var = tk.IntVar(value=200)
        ttk.Spinbox(self.params_frame, from_=0, to=700, increment=10, textvariable=self.pos1_var, width=10).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(self.params_frame, text="Block 2 Position (pixels):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.pos2_var = tk.IntVar(value=400)
        ttk.Spinbox(self.params_frame, from_=0, to=700, increment=10, textvariable=self.pos2_var, width=10).grid(row=5, column=1, padx=5, pady=5)
        
        # Other physics parameters
        ttk.Label(self.params_frame, text="Elasticity (0-1):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.elasticity_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(self.params_frame, from_=0.0, to=1.0, increment=0.05, textvariable=self.elasticity_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(self.params_frame, text="Gravity (m/s²):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.gravity_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(self.params_frame, from_=-10.0, to=10.0, increment=0.1, textvariable=self.gravity_var, width=10).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(self.params_frame, text="Time Rate:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.time_rate_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(self.params_frame, from_=0.1, to=5.0, increment=0.1, textvariable=self.time_rate_var, width=10).grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Label(self.params_frame, text="Wall Damping (0-1):").grid(row=3, column=2, sticky="w", padx=5, pady=5)
        self.wall_damping_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(self.params_frame, from_=0.0, to=1.0, increment=0.05, textvariable=self.wall_damping_var, width=10).grid(row=3, column=3, padx=5, pady=5)
        
        # Display options
        ttk.Label(self.params_frame, text="Display Options:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        
        self.show_cm_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.params_frame, text="Show Center of Mass", variable=self.show_cm_var).grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        self.show_vectors_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.params_frame, text="Show Velocity Vectors", variable=self.show_vectors_var).grid(row=6, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Preset scenarios
        ttk.Label(self.params_frame, text="Preset Scenarios:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.preset_var = tk.StringVar(value="custom")
        presets = [
            ("Custom", "custom"),
            ("Equal Masses", "equal_masses"),
            ("Light vs Heavy", "light_heavy"),
            ("Pi Approximation", "pi_approx"),
            ("Wall Collisions", "wall")
        ]
        
        for i, (text, value) in enumerate(presets):
            ttk.Radiobutton(self.params_frame, text=text, value=value, variable=self.preset_var, command=self.load_preset).grid(
                row=7, column=i+1, padx=5, pady=5, sticky="w"
            )
    
    def create_buttons(self):
        # Start button
        self.start_button = ttk.Button(self.buttons_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(side="left", padx=5, pady=5)
        
        # Apply button (update running simulation)
        self.apply_button = ttk.Button(self.buttons_frame, text="Apply Changes", command=self.apply_changes)
        self.apply_button.pack(side="left", padx=5, pady=5)
        
        # Reset button
        self.reset_button = ttk.Button(self.buttons_frame, text="Reset Simulation", command=self.reset_simulation)
        self.reset_button.pack(side="left", padx=5, pady=5)
        
        # Exit button
        self.exit_button = ttk.Button(self.buttons_frame, text="Exit", command=self.exit_application)
        self.exit_button.pack(side="right", padx=5, pady=5)
    
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
    
    def start_simulation(self):
        """Start the simulation with current parameters"""
        params = self.get_parameters()
        
        # Create new simulation instance
        self.sim = PhysicsSimulation(params)
        
        # Start in a separate thread to keep UI responsive
        import threading
        sim_thread = threading.Thread(target=self.sim.run)
        sim_thread.daemon = True
        sim_thread.start()
    
    def apply_changes(self):
        """Apply parameter changes to running simulation"""
        if self.sim:
            params = self.get_parameters()
            self.sim.reset(params)
    
    def reset_simulation(self):
        """Reset the simulation with current parameters"""
        if self.sim:
            params = self.get_parameters()
            self.sim.reset(params)
    
    def exit_application(self):
        """Clean exit the application"""
        if self.sim:
            pygame.quit()
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_application)
    root.mainloop()