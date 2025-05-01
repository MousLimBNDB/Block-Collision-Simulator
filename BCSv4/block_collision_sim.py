import pygame
import sys
import os
import math
import time

class PhysicsSimulation:
    def __init__(self):
        # Default parameters (will be overridden by reading from file)
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
            'show_trajectories': False, # show trajectories
            'walls': 'both',           # which walls to use
            'block1_width': 50,        # width of block 1
            'block2_width': 60,        # width of block 2
            'block_height': 50,        # height of blocks
            'screen_width': 800,       # simulation screen width
            'screen_height': 500,      # simulation screen height
        }
        
        # Load parameters from file if available
        self.load_parameters()
        
        # Simulation state
        self.collisions = 0
        self.time = 0
        self.paused = False
        self.floor_height = 100
        self.trajectories = []
        
        # Scale factors (pixels per meter)
        self.scale = 100
        
        # Track if blocks are visible (active in simulation)
        self.block1_visible = True
        self.block2_visible = True
        
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption('Block Collision Simulation')
        self.width = self.params['screen_width']
        self.height = self.params['screen_height']
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
        self.LIGHT_RED = (255, 200, 200)
        self.LIGHT_BLUE = (200, 200, 255)
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        
        # Command checking timer
        self.last_command_check = time.time()
    
    def load_parameters(self):
        """Load parameters from file"""
        if os.path.exists("simulation_params.txt"):
            try:
                with open("simulation_params.txt", "r") as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            # Convert value to appropriate type
                            if key in self.params:
                                if isinstance(self.params[key], bool):
                                    self.params[key] = value.lower() == 'true'
                                elif isinstance(self.params[key], int):
                                    self.params[key] = int(float(value))
                                elif isinstance(self.params[key], float):
                                    self.params[key] = float(value)
                                else:
                                    self.params[key] = value
            except Exception as e:
                print(f"Error loading parameters: {e}")
    
    def check_commands(self):
        """Check for commands from the interface"""
        # Only check every 0.5 seconds to avoid excessive file IO
        current_time = time.time()
        if current_time - self.last_command_check < 0.5:
            return
            
        self.last_command_check = current_time
        
        if os.path.exists("simulation_command.txt"):
            try:
                with open("simulation_command.txt", "r") as f:
                    command = f.read().strip()
                
                # Clear the command file
                with open("simulation_command.txt", "w") as f:
                    f.write("")
                
                if command == "reload":
                    self.load_parameters()
                elif command == "reset":
                    self.load_parameters()
                    self.reset()
                elif command == "pause":
                    self.paused = not self.paused
                elif command == "exit":
                    pygame.quit()
                    sys.exit()
            except Exception as e:
                print(f"Error processing command: {e}")
    
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
    
    def check_collision(self):
        """Check for and handle collisions between blocks"""
        # Skip collision check if either block is not visible
        if not (self.block1_visible and self.block2_visible):
            return False
            
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
        
        # Left wall collision for block 1 (only if visible and left wall exists)
        if self.block1_visible and (walls in ['both', 'left']) and x1 <= 0:
            self.params['block1_velocity'] *= -self.params['wall_damping']
            self.params['block1_position'] = 0
            self.collisions += 1
            collision_happened = True
        
        # Left wall collision for block 2 (only if visible and left wall exists)
        if self.block2_visible and (walls in ['both', 'left']) and x2 <= 0:
            self.params['block2_velocity'] *= -self.params['wall_damping']
            self.params['block2_position'] = 0
            self.collisions += 1
            collision_happened = True
        
        # Right wall collision for block 1 (only if visible and right wall exists)
        if self.block1_visible and (walls in ['both', 'right']) and x1 + w1 >= self.width:
            self.params['block1_velocity'] *= -self.params['wall_damping']
            self.params['block1_position'] = self.width - w1
            self.collisions += 1
            collision_happened = True
        
        # Right wall collision for block 2 (only if visible and right wall exists)
        if self.block2_visible and (walls in ['both', 'right']) and x2 + w2 >= self.width:
            self.params['block2_velocity'] *= -self.params['wall_damping']
            self.params['block2_position'] = self.width - w2
            self.collisions += 1
            collision_happened = True
            
        return collision_happened
    
    def check_block_visibility(self):
        """Check if blocks should disappear (out of bounds with no wall)"""
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        w1 = self.params['block1_width']
        w2 = self.params['block2_width']
        walls = self.params['walls']
        
        # Block 1 - left edge check
        if self.block1_visible and walls not in ['both', 'left'] and x1 + w1 < 0:
            self.block1_visible = False
        
        # Block 1 - right edge check
        if self.block1_visible and walls not in ['both', 'right'] and x1 > self.width:
            self.block1_visible = False
            
        # Block 2 - left edge check
        if self.block2_visible and walls not in ['both', 'left'] and x2 + w2 < 0:
            self.block2_visible = False
            
        # Block 2 - right edge check
        if self.block2_visible and walls not in ['both', 'right'] and x2 > self.width:
            self.block2_visible = False
    
    def update(self, dt):
        """Update simulation state"""
        if self.paused:
            return
            
        # Apply time rate
        dt *= self.params['time_rate']
        self.time += dt
        
        # Store positions for trajectory if blocks are visible
        if self.params['show_trajectories'] and self.time % 0.1 < dt:
            if self.block1_visible or self.block2_visible:
                trajectory_point = {'time': self.time}
                
                if self.block1_visible:
                    trajectory_point['pos1'] = (self.params['block1_position'] + self.params['block1_width']/2, 
                                               self.height - self.floor_height - self.params['block_height']/2)
                else:
                    trajectory_point['pos1'] = None
                    
                if self.block2_visible:
                    trajectory_point['pos2'] = (self.params['block2_position'] + self.params['block2_width']/2, 
                                               self.height - self.floor_height - self.params['block_height']/2)
                else:
                    trajectory_point['pos2'] = None
                    
                self.trajectories.append(trajectory_point)
                
                # Limit trajectory points
                if len(self.trajectories) > 100:
                    self.trajectories.pop(0)
        
        # Update positions (continue updating even if not visible)
        self.params['block1_position'] += self.params['block1_velocity'] * dt * self.scale
        self.params['block2_position'] += self.params['block2_velocity'] * dt * self.scale
        
        # Apply gravity if enabled
        if self.params['gravity'] != 0:
            self.params['block1_velocity'] += self.params['gravity'] * dt
            self.params['block2_velocity'] += self.params['gravity'] * dt
            
        # Check if blocks should disappear (out of bounds with no wall)
        self.check_block_visibility()
            
        # Check for collisions between visible blocks and walls
        block_collision = self.check_collision()
        wall_collision = self.check_wall_collision()
    
    def draw_block(self, x, y, width, height, color, outline_color):
        """Draw a block with proper styling"""
        # Main block
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        
        # Block outline
        pygame.draw.rect(self.screen, outline_color, (x, y, width, height), 2)
        
        # Highlight (3D effect)
        pygame.draw.line(self.screen, self.WHITE, (x, y), (x + width, y), 2)
        pygame.draw.line(self.screen, self.WHITE, (x, y), (x, y + height), 2)
        
        # Shadow (3D effect)
        pygame.draw.line(self.screen, self.BLACK, (x, y + height), (x + width, y + height), 1)
        pygame.draw.line(self.screen, self.BLACK, (x + width, y), (x + width, y + height), 1)
    
    def draw_walls(self):
        """Draw the walls based on configuration"""
        walls = self.params['walls']
        floor_y = self.height - self.floor_height
        
        # Draw floor
        pygame.draw.rect(self.screen, self.GRAY, (0, floor_y, self.width, self.floor_height))
        
        # Left wall
        if walls in ['both', 'left']:
            pygame.draw.rect(self.screen, self.GRAY, (0, 0, 10, floor_y))
            # Add visual detail to wall
            for y in range(0, floor_y, 30):
                pygame.draw.rect(self.screen, self.BLACK, (0, y, 10, 15), 1)
        
        # Right wall
        if walls in ['both', 'right']:
            pygame.draw.rect(self.screen, self.GRAY, (self.width - 10, 0, 10, floor_y))
            # Add visual detail to wall
            for y in range(0, floor_y, 30):
                pygame.draw.rect(self.screen, self.BLACK, (self.width - 10, y, 10, 15), 1)
    
    def draw_trajectories(self):
        """Draw block trajectories if enabled"""
        if not self.params['show_trajectories'] or len(self.trajectories) < 2:
            return
            
        # Draw trajectories with fading opacity
        for i in range(1, len(self.trajectories)):
            prev = self.trajectories[i-1]
            curr = self.trajectories[i]
            
            # Calculate opacity based on time (newer = more opaque)
            alpha = min(255, int(255 * (1 - (self.time - curr['time']) / 10)))
            if alpha <= 0:
                continue
                
            # Need a surface with alpha support for transparent lines
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw lines on temporary surface for block 1 if points exist
            if 'pos1' in prev and 'pos1' in curr and prev['pos1'] is not None and curr['pos1'] is not None:
                red_line = (max(1, min(255, int(200 * alpha / 255))), 0, 0, alpha)
                pygame.draw.line(temp_surface, red_line, prev['pos1'], curr['pos1'], 2)
            
            # Draw lines on temporary surface for block 2 if points exist
            if 'pos2' in prev and 'pos2' in curr and prev['pos2'] is not None and curr['pos2'] is not None:
                blue_line = (0, 0, max(1, min(255, int(200 * alpha / 255))), alpha)
                pygame.draw.line(temp_surface, blue_line, prev['pos2'], curr['pos2'], 2)
            
            # Draw temporary surface onto main screen
            self.screen.blit(temp_surface, (0, 0))
    
    def draw(self):
        """Draw the simulation"""
        # Fill background
        self.screen.fill(self.WHITE)
        
        # Draw walls
        self.draw_walls()
        
        # Draw trajectories if enabled
        self.draw_trajectories()
        
        # Block positions
        x1 = self.params['block1_position']
        x2 = self.params['block2_position']
        w1 = self.params['block1_width']
        w2 = self.params['block2_width']
        h = self.params['block_height']
        y = self.height - self.floor_height - h
        
        # Draw blocks only if they are visible
        if self.block1_visible:
            self.draw_block(x1, y, w1, h, self.LIGHT_RED, self.RED)
            # Draw mass label on block 1
            m1_text = self.font.render(f"{self.params['block1_mass']} kg", True, self.BLACK)
            m1_pos = (x1 + w1/2 - m1_text.get_width()/2, y + h/2 - m1_text.get_height()/2)
            self.screen.blit(m1_text, m1_pos)
        
        if self.block2_visible:
            self.draw_block(x2, y, w2, h, self.LIGHT_BLUE, self.BLUE)
            # Draw mass label on block 2
            m2_text = self.font.render(f"{self.params['block2_mass']} kg", True, self.BLACK)
            m2_pos = (x2 + w2/2 - m2_text.get_width()/2, y + h/2 - m2_text.get_height()/2)
            self.screen.blit(m2_text, m2_pos)
        
        # Blocks' center positions for velocity vectors (only if visible)
        center1 = (x1 + w1 / 2, y + h / 2) if self.block1_visible else None
        center2 = (x2 + w2 / 2, y + h / 2) if self.block2_visible else None
        
        # Draw velocity vectors if enabled for visible blocks
        if self.params['show_vectors']:
            # Scale vectors for visibility (adjust based on velocity magnitude)
            max_vel = max(abs(self.params['block1_velocity']), abs(self.params['block2_velocity']))
            max_vel = max(max_vel, 0.1)  # Avoid division by zero
            vector_scale = min(50, 20 / max_vel)
            
            # Block 1 velocity vector (if visible)
            if self.block1_visible:
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
            
            # Block 2 velocity vector (if visible)
            if self.block2_visible:
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
        
        # Draw center of mass only if at least one block is visible
        if self.params['show_cm'] and (self.block1_visible or self.block2_visible):
            cm_pos = self.calculate_cm_position()
            cm_vel = self.calculate_cm_velocity()
            
            # Draw vertical line showing center of mass
            pygame.draw.line(self.screen, self.YELLOW, 
                            (cm_pos, 0), 
                            (cm_pos, self.height - self.floor_height), 
                            1)
            
            # Draw CM point
            pygame.draw.circle(self.screen, self.YELLOW, (cm_pos, y + h / 2), 6)
            pygame.draw.circle(self.screen, self.BLACK, (cm_pos, y + h / 2), 6, 1)
            
            # Draw CM velocity vector
            if self.params['show_vectors'] and abs(cm_vel) > 0.001:
                # Use same scale as other vectors
                max_vel = max(abs(self.params['block1_velocity']), abs(self.params['block2_velocity']))
                max_vel = max(max_vel, 0.1)  # Avoid division by zero
                vector_scale = min(50, 20 / max_vel)
                
                cm_end = (cm_pos + cm_vel * vector_scale, y + h / 2)
                pygame.draw.line(self.screen, self.YELLOW, (cm_pos, y + h / 2), cm_end, 2)
                
                # Arrow head for CM vector
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
            f"Block 1: {'Visible' if self.block1_visible else 'Off-screen'}, v={self.params['block1_velocity']:.2f} m/s",
            f"Block 2: {'Visible' if self.block2_visible else 'Off-screen'}, v={self.params['block2_velocity']:.2f} m/s",
            f"CM Velocity: {self.calculate_cm_velocity():.4f} m/s"
        ]
        
        # Background for text for better readability
        info_surface = pygame.Surface((280, 25 * len(info_text) + 10))
        info_surface.set_alpha(180)
        info_surface.fill(self.WHITE)
        self.screen.blit(info_surface, (5, 5))
        
        for i, text in enumerate(info_text):
            text_surface = self.font.render(text, True, self.BLACK)
            self.screen.blit(text_surface, (10, 10 + i * 25))
        
        # Paused indicator
        if self.paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(100)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Pause text
            pause_text = pygame.font.Font(None, 72).render("PAUSED", True, self.RED)
            pause_rect = pause_text.get_rect(center=(self.width / 2, self.height / 2))
            self.screen.blit(pause_text, pause_rect)
            
            # Instructions
            instructions = [
                "Space: Resume/Pause",
                "R: Reset",
                "C: Toggle Center of Mass",
                "V: Toggle Velocity Vectors",
                "T: Toggle Trajectories",
                "Esc: Exit"
            ]
            
            for i, text in enumerate(instructions):
                instr_text = self.font.render(text, True, self.WHITE)
                self.screen.blit(instr_text, (self.width / 2 - 80, self.height / 2 + 50 + i * 25))
            
        pygame.display.flip()
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
    
    def reset(self):
        """Reset the simulation with current parameters"""
        self.collisions = 0
        self.time = 0
        self.trajectories = []
        self.block1_visible = True
        self.block2_visible = True
        
        # Ensure blocks move toward wall when only one wall is present
        if self.params['walls'] == 'left':
            # Make blocks move left (toward left wall)
            if self.params['block1_velocity'] > 0:
                self.params['block1_velocity'] *= -1
            if self.params['block2_velocity'] > 0:
                self.params['block2_velocity'] *= -1
        elif self.params['walls'] == 'right':
            # Make blocks move right (toward right wall)
            if self.params['block1_velocity'] < 0:
                self.params['block1_velocity'] *= -1
            if self.params['block2_velocity'] < 0:
                self.params['block2_velocity'] *= -1
    
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
            self.trajectories = []
    
    def run(self):
        """Main simulation loop"""
        running = True
        
        # Set initial velocities based on wall configuration
        self.reset()
        
        while running:
            dt = self.clock.tick(60) / 1000.0  # time in seconds
            
            # Check for commands from the interface
            self.check_commands()
            
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
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update(dt)
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    # Create and run simulation
    sim = PhysicsSimulation()
    sim.run()