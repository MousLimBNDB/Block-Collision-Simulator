import pygame
import sys
import os
import time
import math

class PhysicsSimulation:
    def __init__(self):
        # Default parameters (will be overridden by file)
        self.params = {
            'block1_mass': 1.0,
            'block2_mass': 2.0,
            'block1_velocity': 0.0,
            'block2_velocity': -1.0,
            'block1_position': 200,
            'block2_position': 400,
            'elasticity': 1.0,
            'gravity': 0.0,
            'time_rate': 1.0,
            'wall_damping': 1.0,
            'show_cm': False,
            'show_vectors': True,
            'show_trajectories': False,
            'walls': 'both',
            'block1_width': 50,
            'block2_width': 60,
            'block_height': 50,
            'screen_width': 800,
            'screen_height': 500
        }
        
        # Load parameters from file
        self.load_parameters()
        
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption('Block Collision Simulation')
        self.width = self.params['screen_width']
        self.height = self.params['screen_height']
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        
        # Simulation state
        self.collisions = 0
        self.time = 0
        self.paused = False
        self.floor_height = 100
        self.command_check_timer = 0
        
        # Scale factors (pixels per meter)
        self.scale = 100
        
        # Trajectory history
        self.trajectory1 = []
        self.trajectory2 = []
        self.max_trajectory_points = 100
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 80, 80)
        self.BLUE = (80, 80, 255)
        self.GREEN = (50, 180, 50)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (200, 200, 200)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (160, 32, 240)
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
    
    def load_parameters(self):
        """Load parameters from file"""
        try:
            if os.path.exists("simulation_params.txt"):
                with open("simulation_params.txt", "r") as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            # Convert to appropriate type
                            if value.lower() == 'true':
                                self.params[key] = True
                            elif value.lower() == 'false':
                                self.params[key] = False
                            elif '.' in value:
                                try:
                                    self.params[key] = float(value)
                                except ValueError:
                                    self.params[key] = value
                            else:
                                try:
                                    self.params[key] = int(value)
                                except ValueError:
                                    self.params[key] = value
        except Exception as e:
            print(f"Error loading parameters: {e}")
    
    def check_commands(self):
        """Check for commands from the UI"""
        if os.path.exists("simulation_command.txt"):
            try:
                with open("simulation_command.txt", "r") as f:
                    command = f.read().strip()
                
                # Remove the command file
                os.remove("simulation_command.txt")
                
                if command == "reload":
                    self.load_parameters()
                elif command == "reset":
                    self.load_parameters()
                    self.reset()
                elif command == "exit":
                    return False  # Signal to exit
            except Exception as e:
                print(f"Error processing command: {e}")
        
        return True  # Continue running
        
    def calculate_cm_position(self):
        """Calculate the center of mass position"""
        m1 = self.params['block1_mass']
        m2 = self.params['block2_mass']
        x1 = self.params['block1_position'] + self.params['block1_width'] / 2
        x2 = self.params['block2_position'] + self.params['block2_width'] / 2
        
        return (m1 * x1 + m2 * x2) / (m1 + m2)
    
    def calculate_cm_velocity(self):
        """Calculate the center of mass velocity"""
        m1 = self.params['block1_mass']
        m2 = self.params['block2_mass']
        v1 = self.params['block1_velocity']
        v2 = self.params['block2_velocity']
        
        return (m1 * v1 + m2 * v2) / (m1 + m2)
    
    def calculate_total_momentum(self):
        """Calculate the total momentum of the system"""
        m1 = self.params['block1_mass']
        m2 = self.params['block2_mass']
        v1 = self.params['block1_velocity']
        v2 = self.params['block2_velocity']
        
        return m1 * v1 + m2 * v2
    
    def calculate_total_energy(self):
        """Calculate the total kinetic energy of the system"""
        m1 = self.params['block1_mass']
        m2 = self.params['block2_mass']
        v1 = self.params['block1_velocity']
        v2 = self.params['block2_velocity']
        
        return 0.5 * m1 * v1**2 + 0.5 * m2 * v2**2
    
    def check_collision(self):
        """Check for and handle collisions between blocks"""
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        w1 = self.params['block1_width']
        w2 = self.params['block2_width']
        
        # Check collision between blocks
        if x1 + w1 >= x2:
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
            overlap = (x1 + w1) - x2
            self.params['block1_position'] -= overlap/2
            self.params['block2_position'] += overlap/2
            
            self.collisions += 1
            return True
        
        return False
    
    def check_wall_collision(self):
        """Check for and handle wall collisions"""
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        w1 = self.params['block1_width']
        w2 = self.params['block2_width']
        walls = self.params['walls']
        
        collision_happened = False
        
        # Left wall collision for block 1
        if (walls in ['both', 'left']) and x1 <= 0:
            self.params['block1_velocity'] *= -self.params['wall_damping']
            self.params['block1_position'] = 0
            self.collisions += 1
            collision_happened = True
        
        # Right wall collision for block 1
        if (walls in ['both', 'right']) and x1 + w1 >= self.width:
            self.params['block1_velocity'] *= -self.params['wall_damping']
            self.params['block1_position'] = self.width - w1
            self.collisions += 1
            collision_happened = True
            
        # Left wall collision for block 2
        if (walls in ['both', 'left']) and x2 <= 0:
            self.params['block2_velocity'] *= -self.params['wall_damping']
            self.params['block2_position'] = 0
            self.collisions += 1
            collision_happened = True
        
        # Right wall collision for block 2
        if (walls in ['both', 'right']) and x2 + w2 >= self.width:
            self.params['block2_velocity'] *= -self.params['wall_damping']
            self.params['block2_position'] = self.width - w2
            self.collisions += 1
            collision_happened = True
            
        return collision_happened
    
    def update(self, dt):
        """Update simulation state"""
        if self.paused:
            return
            
        # Apply time rate
        dt *= self.params['time_rate']
        self.time += dt
        
        # Store positions for trajectory
        if self.params['show_trajectories']:
            center1 = (self.params['block1_position'] + self.params['block1_width'] / 2, 
                       self.height - self.floor_height - self.params['block_height'] / 2)
            center2 = (self.params['block2_position'] + self.params['block2_width'] / 2,
                       self.height - self.floor_height - self.params['block_height'] / 2)
            
            self.trajectory1.append(center1)
            self.trajectory2.append(center2)
            
            # Limit trajectory length
            if len(self.trajectory1) > self.max_trajectory_points:
                self.trajectory1.pop(0)
            if len(self.trajectory2) > self.max_trajectory_points:
                self.trajectory2.pop(0)
        
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
        
        # Check for UI commands (but not too frequently)
        self.command_check_timer += dt
        if self.command_check_timer >= 0.5:  # Check every half second
            self.command_check_timer = 0
            return self.check_commands()
            
        return True
    
    def draw_wall(self, x, height, is_left=True):
        """Draw a wall at the specified position"""
        wall_width = 10
        
        if is_left:
            rect = (0, self.height - height, wall_width, height)
        else:
            rect = (self.width - wall_width, self.height - height, wall_width, height)
            
        pygame.draw.rect(self.screen, self.BLACK, rect)
        
        # Draw a pattern on the wall
        brick_height = 20
        for y in range(self.height - height, self.height, brick_height):
            offset = brick_height // 2 if (y // brick_height) % 2 == 1 else 0
            brick_width = wall_width // 2
            
            if is_left:
                x_pos = offset
            else:
                x_pos = self.width - wall_width + offset
                
            pygame.draw.rect(self.screen, self.GRAY, 
                            (x_pos, y, brick_width, brick_height - 2))
    
    def draw(self):
        """Draw the simulation"""
        # Fill background
        self.screen.fill(self.WHITE)
        
        # Draw floor
        floor_y = self.height - self.floor_height
        pygame.draw.rect(self.screen, self.GRAY, (0, floor_y, self.width, self.floor_height))
        pygame.draw.line(self.screen, self.BLACK, (0, floor_y), (self.width, floor_y), 3)
        
        # Draw walls based on setting
        wall_height = floor_y
        if self.params['walls'] in ['both', 'left']:
            self.draw_wall(0, wall_height, True)
        if self.params['walls'] in ['both', 'right']:
            self.draw_wall(self.width, wall_height, False)
        
        # Draw trajectories if enabled
        if self.params['show_trajectories'] and len(self.trajectory1) > 1:
            # Draw with transparent colors and increasing intensity
            for i in range(1, len(self.trajectory1)):
                # Calculate intensity based on position in trajectory (more recent = more opaque)
                alpha = int(255 * (i / len(self.trajectory1)))
                
                # For block 1
                color1 = (self.RED[0], self.RED[1], self.RED[2], alpha)
                pygame.draw.line(self.screen, color1, 
                                self.trajectory1[i-1], self.trajectory1[i], 2)
                
                # For block 2
                color2 = (self.BLUE[0], self.BLUE[1], self.BLUE[2], alpha)
                pygame.draw.line(self.screen, color2,
                                self.trajectory2[i-1], self.trajectory2[i], 2)
        
        # Block positions
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        w1 = self.params['block1_width']
        w2 = self.params['block2_width']
        h = self.params['block_height']
        y = floor_y - h
        
        # Draw blocks
        pygame.draw.rect(self.screen, self.RED, (x1, y, w1, h))
        pygame.draw.rect(self.screen, self.BLUE, (x2, y, w2, h))
        
        # Draw block outlines
        pygame.draw.rect(self.screen, self.BLACK, (x1, y, w1, h), 2)
        pygame.draw.rect(self.screen, self.BLACK, (x2, y, w2, h), 2)
        
        # Draw block labels
        label1 = self.font.render("1", True, self.WHITE)
        label2 = self.font.render("2", True, self.WHITE)
        self.screen.blit(label1, (x1 + w1/2 - 5, y + h/2 - 8))
        self.screen.blit(label2, (x2 + w2/2 - 5, y + h/2 - 8))
        
        # Blocks' center positions for velocity vectors
        center1 = (x1 + w1 / 2, y + h / 2)
        center2 = (x2 + w2 / 2, y + h / 2)
        
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
            pygame.draw.circle(self.screen, self.YELLOW, (cm_pos, y + h / 2), 6)
            
            # Draw CM velocity vector
            if self.params['show_vectors']:
                cm_end = (cm_pos + cm_vel * 20, y + h / 2)
                pygame.draw.line(self.screen, self.YELLOW, (cm_pos, y + h / 2), cm_end, 2)
                # Arrow head
                if cm_vel != 0:
                    direction = 1 if cm_vel > 0 else -1
                    pygame.draw.polygon(self.screen, self.YELLOW, [
                        (cm_end[0], cm_end[1]),
                        (cm_end[0] - direction * 6, cm_end[1] - 3),
                        (cm_end[0] - direction * 6, cm_end[1] + 3)
                    ])
        
        # Display simulation info
        info_text = [
            f"Time: {self.time:.2f}s",
            f"Collisions: {self.collisions}",
            f"Block 1 - Mass: {self.params['block1_mass']}kg, Velocity: {self.params['block1_velocity']:.2f}m/s",
            f"Block 2 - Mass: {self.params['block2_mass']}kg, Velocity: {self.params['block2_velocity']:.2f}m/s",
            f"CM Velocity: {self.calculate_cm_velocity():.4f}m/s",
            f"Total Momentum: {self.calculate_total_momentum():.4f}kg·m/s",
            f"Total Energy: {self.calculate_total_energy():.4f}J"
        ]
        
        # Draw info box
        info_box_height = 10 + 25 * len(info_text)
        pygame.draw.rect(self.screen, (240, 240, 240), (10, 10, 450, info_box_height))
        pygame.draw.rect(self.screen, self.BLACK, (10, 10, 450, info_box_height), 1)
        
        for i, text in enumerate(info_text):
            text_surface = self.font.render(text, True, self.BLACK)
            self.screen.blit(text_surface, (20, 15 + i * 25))
        
        # Paused indicator
        if self.paused:
            pause_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 90))
            self.screen.blit(pause_overlay, (0, 0))
            
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render("PAUSED", True, self.RED)
            text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_text, text_rect)
            
            # Display controls
            controls_text = [
                "SPACE: Toggle Pause",
                "R: Reset Simulation",
                "C: Toggle Center of Mass",
                "V: Toggle Velocity Vectors",
                "T: Toggle Trajectories"
            ]
            
            control_font = pygame.font.Font(None, 24)
            for i, text in enumerate(controls_text):
                ctrl_text = control_font.render(text, True, self.WHITE)
                self.screen.blit(ctrl_text, (self.width // 2 - 100, self.height // 2 + 50 + i * 30))
            
        pygame.display.flip()
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
    
    def reset(self):
        """Reset the simulation"""
        self.collisions = 0
        self.time = 0
        self.trajectory1 = []
        self.trajectory2 = []
    
    def toggle_cm(self):
        """Toggle center of mass display"""
        self.params['show_cm'] = not self.params['show_cm']
    
    def toggle_vectors(self):
        """Toggle velocity vectors display"""
        self.params['show_vectors'] = not self.params['show_vectors']
    
    def toggle_trajectories(self):
        """Toggle trajectories display"""
        self.params['show_trajectories'] = not self.params['show_trajectories']
        if not self.params['show_trajectories']:
            self.trajectory1 = []
            self.trajectory2 = []
    
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
                    elif event.key == pygame.K_t:
                        self.toggle_trajectories()
            
            if not self.update(dt):
                running = False
            
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    sim = PhysicsSimulation()
    sim.run()