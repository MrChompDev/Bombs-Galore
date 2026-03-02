import pygame
import math
import os
import sys

pygame.init()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Constants
INFO = pygame.display.Info()
WIDTH, HEIGHT = INFO.current_w, INFO.current_h
FPS = 60
GRID = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
RED = (255, 68, 68)
BLUE = (68, 170, 255)
CYAN = (100, 255, 255)
PURPLE = (200, 100, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)

# Initialize screen - fullscreen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Bombs Galore")
clock = pygame.time.Clock()

# Initialize mixer for music
pygame.mixer.init()

# Load music with resource_path
music_tracks = {}
music_paths = {
    'menu': resource_path('Assets/Music/MenuOST.mp3'),
    'main': resource_path('Assets/Music/MainOST.mp3'),
    'ice': resource_path('Assets/Music/IceOST.mp3'),
    'gas': resource_path('Assets/Music/GasOST.mp3'),
    'final': resource_path('Assets/Music/FinalOST.mp3')
}

for key, path in music_paths.items():
    try:
        # Just store the path, we'll load when needed
        music_tracks[key] = path
        print(f"Found music: {key}")
    except Exception as e:
        print(f"Warning: Could not find {path}: {e}")

# Load sound effects with resource_path
sound_effects = {}
sfx_paths = {
    'explosion': resource_path('Assets/SFX/Explosion.mp3'),
    'walking': resource_path('Assets/SFX/Walking.mp3'),
    'ding': resource_path('Assets/SFX/Ding.mp3')
}

for key, path in sfx_paths.items():
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(0.5)  # Set SFX volume to 50%
        sound_effects[key] = sound
        print(f"Loaded SFX: {key}")
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        sound_effects[key] = None

current_music = None

def play_music(track_name, loop=-1):
    """Play music track. Loop=-1 means loop forever."""
    global current_music
    if track_name in music_tracks and current_music != track_name:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_tracks[track_name])
            pygame.mixer.music.play(loop)
            pygame.mixer.music.set_volume(0.6)
            current_music = track_name
            print(f"Playing music: {track_name}")
        except Exception as e:
            print(f"Could not play {track_name}: {e}")

def play_sound(sound_name):
    """Play a sound effect."""
    if sound_name in sound_effects and sound_effects[sound_name]:
        sound_effects[sound_name].play()

# Load Assets
def load_image(path, scale=None):
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        return None

# Load player animation (4 frames) - scale them up properly
player_frames = []
for i in range(1, 5):
    frame = load_image(f"Assets/Player/creature-sheet{i}.png")
    if frame:
        # Scale up 2x to make character bigger and not squashed
        original_size = frame.get_size()
        scaled_frame = pygame.transform.scale(frame, (original_size[0] * 2, original_size[1] * 2))
        player_frames.append(scaled_frame)

# Load bomb sprites (organized by type) - make them bigger
bomb_sprites = {
    'fire': [],
    'ice': [],
    'gas': [],
    'directional': [],
    'chain': []
}

# Load Fire bombs
for i in range(1, 7):
    bomb = load_image(f"Assets/Bombs/Fire_Bomb{i}.png")
    if bomb:
        # Scale up 3x to make bombs more visible
        original_size = bomb.get_size()
        bomb = pygame.transform.scale(bomb, (original_size[0] * 3, original_size[1] * 3))
        bomb_sprites['fire'].append(bomb)

# Load Ice bombs
for i in range(1, 7):
    bomb = load_image(f"Assets/Bombs/IceBomb{i}.png")
    if bomb:
        original_size = bomb.get_size()
        bomb = pygame.transform.scale(bomb, (original_size[0] * 3, original_size[1] * 3))
        bomb_sprites['ice'].append(bomb)

# Load Gas bombs
for i in range(1, 7):
    bomb = load_image(f"Assets/Bombs/GasBomb{i}.png")
    if bomb:
        original_size = bomb.get_size()
        bomb = pygame.transform.scale(bomb, (original_size[0] * 3, original_size[1] * 3))
        bomb_sprites['gas'].append(bomb)

# Load Directional bombs
for i in range(1, 7):
    bomb = load_image(f"Assets/Bombs/DirectionalBomb{i}.png")
    if bomb:
        original_size = bomb.get_size()
        bomb = pygame.transform.scale(bomb, (original_size[0] * 3, original_size[1] * 3))
        bomb_sprites['directional'].append(bomb)

# Load Chain bombs
for i in range(1, 7):
    bomb = load_image(f"Assets/Bombs/ChainBomb{i}.png")
    if bomb:
        original_size = bomb.get_size()
        bomb = pygame.transform.scale(bomb, (original_size[0] * 3, original_size[1] * 3))
        bomb_sprites['chain'].append(bomb)

# Load tile sprites
tile_sprites = []
for i in range(1, 37):
    tile = load_image(f"Assets/Tilesets/Tiles_{i:02d}.png")
    if tile:
        # Ensure tiles are 32x32
        tile = pygame.transform.scale(tile, (32, 32))
        tile_sprites.append(tile)

print(f"Loaded {len(tile_sprites)} tile sprites")

# Default tile
tile_sprite = tile_sprites[0] if tile_sprites else None

# Load background - try different paths
background = None
bg_paths = [
    "Assets/Tilesets/Background/Blue.png",
    "Assets/Background/Blue.png",
    "Assets/Backgrounds/Blue.png"
]
for path in bg_paths:
    background = load_image(path)
    if background:
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        print(f"Loaded background from {path}")
        break

if not background:
    print("No background loaded, using solid color")

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.w = 48  # Bigger hitbox to match scaled sprite
        self.h = 48
        self.grounded = False
        self.frame = 0
        self.frame_timer = 0
        self.facing_right = True
        self.was_moving = False  # Track if player was moving last frame
        
    def update(self, platforms, ice_platforms):
        # Gravity
        self.vy += 0.5
        
        # Cap fall speed
        if self.vy > 15:
            self.vy = 15
        
        # Movement
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = max(self.vx - 0.5, -5)
            self.facing_right = False
            moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = min(self.vx + 0.5, 5)
            self.facing_right = True
            moving = True
        else:
            self.vx *= 0.85
        
        # Play walking sound
        if moving and self.grounded and abs(self.vx) > 0.5:
            if not self.was_moving:
                # Start walking sound
                if 'walking' in sound_effects and sound_effects['walking']:
                    sound_effects['walking'].play(-1)  # Loop walking sound
            self.was_moving = True
        else:
            if self.was_moving:
                # Stop walking sound
                if 'walking' in sound_effects and sound_effects['walking']:
                    sound_effects['walking'].stop()
            self.was_moving = False
            
        # Animation
        if moving and self.grounded:
            self.frame_timer += 1
            if self.frame_timer >= 8:
                self.frame_timer = 0
                if player_frames:
                    self.frame = (self.frame + 1) % len(player_frames)
        else:
            self.frame = 0
            self.frame_timer = 0
        
        # Apply horizontal velocity first
        self.x += self.vx
        
        # Check horizontal collisions
        for plat in platforms + ice_platforms:
            if self.collides(plat):
                # Right collision (moving left into wall)
                if self.vx < 0:
                    self.x = plat['x'] + plat['w']
                    self.vx = 0
                # Left collision (moving right into wall)
                elif self.vx > 0:
                    self.x = plat['x'] - self.w
                    self.vx = 0
        
        # Apply vertical velocity
        self.y += self.vy
        
        # Check vertical collisions
        self.grounded = False
        for plat in platforms + ice_platforms:
            if self.collides(plat):
                # Top collision (landing on platform)
                if self.vy >= 0:
                    self.y = plat['y'] - self.h
                    self.vy = 0
                    self.grounded = True
                # Bottom collision (hitting ceiling)
                elif self.vy < 0:
                    self.y = plat['y'] + plat['h']
                    self.vy = 0
        
        # Screen bounds
        if self.x < 0:
            self.x = 0
            self.vx = 0
        if self.x + self.w > WIDTH:
            self.x = WIDTH - self.w
            self.vx = 0
        
        # Only die if significantly below screen
        if self.y > HEIGHT + 100:
            return True  # Death
        
        return False
        
    def collides(self, rect):
        return (self.x < rect['x'] + rect['w'] and
                self.x + self.w > rect['x'] and
                self.y < rect['y'] + rect['h'] and
                self.y + self.h > rect['y'])
    
    def draw(self, screen):
        if player_frames:
            frame_img = player_frames[self.frame]
            if not self.facing_right:
                frame_img = pygame.transform.flip(frame_img, True, False)
            # Center the sprite on the hitbox
            sprite_w, sprite_h = frame_img.get_size()
            offset_x = (sprite_w - self.w) / 2
            offset_y = (sprite_h - self.h) / 2
            screen.blit(frame_img, (self.x - offset_x, self.y - offset_y))
        else:
            # Fallback to colored rectangle
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.w, self.h))
            # Goggles
            pygame.draw.circle(screen, CYAN, (int(self.x + 14), int(self.y + 18)), 6)
            pygame.draw.circle(screen, CYAN, (int(self.x + 34), int(self.y + 18)), 6)

class Bomb:
    def __init__(self, x, y, bomb_type):
        self.x = x
        self.y = y
        self.type = bomb_type
        self.placed = True
        self.detonated = False
        self.timer = 0
        self.bob_offset = 0
        self.anim_frame = 0
        self.anim_timer = 0
        
    def update(self):
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3
        
        # Animate bomb sprites
        self.anim_timer += 1
        if self.anim_timer >= 6:
            self.anim_timer = 0
            bomb_type_names = ['fire', 'ice', 'gas', 'directional', 'chain']
            if self.type < len(bomb_type_names):
                frames = bomb_sprites[bomb_type_names[self.type]]
                if frames:
                    self.anim_frame = (self.anim_frame + 1) % len(frames)
        
    def draw(self, screen):
        if not self.detonated:
            y_pos = int(self.y + self.bob_offset)
            
            # Draw animated bomb sprite
            bomb_type_names = ['fire', 'ice', 'gas', 'directional', 'chain']
            if self.type < len(bomb_type_names):
                frames = bomb_sprites[bomb_type_names[self.type]]
                if frames and self.anim_frame < len(frames):
                    bomb_img = frames[self.anim_frame]
                    img_w, img_h = bomb_img.get_size()
                    screen.blit(bomb_img, (int(self.x - img_w/2), y_pos - img_h/2))
                    return
            
            # Fallback to colored circles
            if self.type == 0:  # Fire
                pygame.draw.circle(screen, RED, (int(self.x), y_pos), 12)
                pygame.draw.circle(screen, ORANGE, (int(self.x), y_pos), 8)
            elif self.type == 1:  # Ice
                pygame.draw.circle(screen, CYAN, (int(self.x), y_pos), 12)
                pygame.draw.circle(screen, BLUE, (int(self.x), y_pos), 8)
            elif self.type == 2:  # Gas
                pygame.draw.circle(screen, (150, 255, 150), (int(self.x), y_pos), 12)
                pygame.draw.circle(screen, (100, 200, 100), (int(self.x), y_pos), 8)
            elif self.type == 3:  # Directional
                pygame.draw.circle(screen, PURPLE, (int(self.x), y_pos), 12)
                pygame.draw.circle(screen, (150, 50, 200), (int(self.x), y_pos), 8)

class Explosion:
    def __init__(self, x, y, bomb_type, radius):
        self.x = x
        self.y = y
        self.type = bomb_type
        self.radius = radius
        self.timer = 30
        self.max_radius = radius
        self.particles = []
        
        # Create particles
        for _ in range(20):
            angle = math.radians(pygame.time.get_ticks() % 360 + _ * 18)
            speed = 2 + _ * 0.2
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'size': 4
            })
        
    def update(self):
        self.timer -= 1
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.95
            p['vy'] *= 0.95
            p['life'] -= 1
            p['size'] = max(1, p['size'] * 0.95)
        return self.timer > 0
    
    def draw(self, screen):
        alpha = self.timer / 30
        current_radius = self.max_radius * (0.5 + alpha * 0.5)
        
        if self.type == 0:  # Fire
            outer_color = (255, int(150 * alpha), int(50 * alpha))
            inner_color = (255, int(200 * alpha), int(100 * alpha))
        elif self.type == 1:  # Ice
            outer_color = (int(150 * alpha), int(220 * alpha), 255)
            inner_color = (int(200 * alpha), int(240 * alpha), 255)
        elif self.type == 2:  # Gas
            outer_color = (150, 255, 150)
            inner_color = (200, 255, 200)
        else:  # Directional
            outer_color = (200, 100, 255)
            inner_color = (220, 150, 255)
        
        # Draw expanding rings
        pygame.draw.circle(screen, outer_color, (int(self.x), int(self.y)), int(current_radius), 4)
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(current_radius * 0.7), 2)
        
        # Draw particles
        for p in self.particles:
            if p['life'] > 0:
                p_alpha = p['life'] / 30
                if self.type == 0:
                    p_color = (255, int(150 * p_alpha), int(50 * p_alpha))
                elif self.type == 1:
                    p_color = (int(150 * p_alpha), int(220 * p_alpha), 255)
                elif self.type == 2:
                    p_color = (150, 255, 150)
                else:
                    p_color = (200, 100, 255)
                pygame.draw.circle(screen, p_color, (int(p['x']), int(p['y'])), int(p['size']))

class TutorialBox:
    def __init__(self, text, x, y, duration=None):
        self.text = text
        self.x = x
        self.y = y
        self.duration = duration
        self.timer = 0
        self.visible = True
        self.alpha = 0  # Start transparent
        self.fade_in_time = 30  # Frames to fade in
        self.fade_out_time = 30  # Frames to fade out
        self.hold_time = duration * FPS if duration else 300  # Frames to hold
        self.phase = 'fade_in'  # fade_in, hold, fade_out
        
    def update(self):
        self.timer += 1
        
        if self.phase == 'fade_in':
            self.alpha = min(255, (self.timer / self.fade_in_time) * 255)
            if self.timer >= self.fade_in_time:
                self.phase = 'hold'
                self.timer = 0
        elif self.phase == 'hold':
            if self.duration and self.timer >= self.hold_time:
                self.phase = 'fade_out'
                self.timer = 0
        elif self.phase == 'fade_out':
            self.alpha = max(0, 255 - (self.timer / self.fade_out_time) * 255)
            if self.timer >= self.fade_out_time:
                self.visible = False
        
        return self.visible
    
    def draw(self, screen, font):
        if not self.visible or self.alpha <= 0:
            return
        
        # Word wrap
        words = self.text.split()
        lines = []
        current_line = []
        max_width = 400
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate box size
        padding = 20
        line_height = 28
        box_width = max_width + padding * 2
        box_height = len(lines) * line_height + padding * 2
        
        # Create surfaces with alpha
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        
        # Draw box background
        box_color = (*DARK_GRAY, int(self.alpha * 0.9))
        pygame.draw.rect(box_surface, box_color, (0, 0, box_width, box_height), border_radius=10)
        
        # Draw border
        border_color = (*YELLOW, int(self.alpha))
        pygame.draw.rect(box_surface, border_color, (0, 0, box_width, box_height), 3, border_radius=10)
        
        # Draw text on box surface
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, WHITE)
            text_with_alpha = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            text_with_alpha.blit(text_surf, (0, 0))
            text_with_alpha.set_alpha(int(self.alpha))
            box_surface.blit(text_with_alpha, (padding, padding + i * line_height))
        
        # Blit to screen
        screen.blit(box_surface, (self.x - padding, self.y - padding))

class Game:
    def __init__(self):
        self.state = 'menu'  # menu, playing, paused, settings, lore
        self.player = Player(100, 100)
        self.bombs = []
        self.explosions = []
        self.selected_bomb = 0
        self.level = 0
        self.deaths = 0
        self.tutorial_boxes = []
        self.show_tutorial = True
        self.levels = self.create_levels()
        self.menu_selection = 0  # 0 = Start, 1 = Lore, 2 = Settings, 3 = Tutorial On/Off, 4 = Quit
        self.menu_options = ['START GAME', 'LORE', 'SETTINGS', 'TUTORIAL: ON', 'QUIT']
        self.pause_selection = 0  # 0 = Continue, 1 = Settings, 2 = Main Menu
        self.pause_options = ['CONTINUE', 'SETTINGS', 'MAIN MENU']
        self.settings_selection = 0
        self.settings_options = ['MUSIC VOLUME', 'SFX VOLUME', 'BACK']
        self.music_volume = 0.6
        self.sfx_volume = 0.5
        self.lore_page = 0
        self.lore_text = [
            {
                'title': 'THE GREAT ALCHEMY LAB',
                'text': [
                    "The Great Alchemy Lab was once a respected research",
                    "facility dedicated to solving problems through alchemy.",
                    "",
                    "One day, the lead researchers asked a dangerous question:",
                    "",
                    '"What if one solution could solve every problem?"',
                    "",
                    "The answer was bombs.",
                    "",
                    "After a catastrophic test, the lab shattered into",
                    "isolated puzzle rooms. Elevators froze. Floors collapsed.",
                    "Gravity became... optional."
                ]
            },
            {
                'title': 'MEET BLIP',
                'text': [
                    "You are Blip, a junior alchemist with oversized goggles",
                    "and a backpack full of experimental bombs.",
                    "",
                    "Blip is very smart — just not in a safe way.",
                    "",
                    "Blip cannot jump normally.",
                    "",
                    "Blip blew up the stairs.",
                    "",
                    "But Blip survived! Mostly because Blip caused most of it.",
                    "",
                    "Now Blip must reach the top of the lab to stabilize",
                    "the final experiment. Or make it worse. Both are acceptable."
                ]
            },
                            {
                'title': 'THE BOMBS',
                'text': [
                    "FIRE BOMBS - Your main tool for movement.",
                    "Powerful radial explosions that launch you through the air.",
                    "Place bombs near yourself and detonate to fly!",
                    "",
                    "ICE BOMBS - Freeze water into temporary platforms.",
                    "Create paths where none existed before.",
                    "Ice melts after a few seconds, so move quickly!",
                    "",
                    "Remember: You can place bombs while flying!",
                    "Stack explosions to reach impossible heights.",
                    "",
                    "There is no bad ending. Only bigger explosions."
                ]
            }
        ]
        
    def start_game(self):
        self.state = 'playing'
        self.deaths = 0
        self.load_level(0)
    
    def adjust_music_volume(self, change):
        self.music_volume = max(0.0, min(1.0, self.music_volume + change))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def adjust_sfx_volume(self, change):
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + change))
        for sound in sound_effects.values():
            if sound:
                sound.set_volume(self.sfx_volume)
        
    def create_levels(self):
        # Calculate level boundaries based on screen size
        level_width = WIDTH
        level_height = HEIGHT
        
        return [
            {  # Tutorial - Fire Bomb
                'name': 'This Is Fine',
                'music': 'main',
                'player_start': (100, level_height - 150),
                'platforms': [
                    {'x': 0, 'y': level_height - 100, 'w': 300, 'h': 100},
                    {'x': level_width - 350, 'y': level_height - 200, 'w': 350, 'h': 200},
                ],
                'water': [],
                'goal': {'x': level_width - 250, 'y': level_height - 250, 'w': 40, 'h': 40},
                'unlocked_bombs': [0],
                'story': "The lab is shattered. Time to find a way up.",
                'tutorial': [
                    "You're Blip, a junior alchemist.",
                    "Left Click to place a Fire Bomb.",
                    "Right Click to detonate it!",
                    "The explosion will launch you."
                ]
            },
            {  # Gap crossing
                'name': 'Small Explosion = Small Problem',
                'music': 'main',
                'player_start': (100, level_height - 150),
                'platforms': [
                    {'x': 0, 'y': level_height - 100, 'w': 250, 'h': 100},
                    {'x': level_width // 2 - 100, 'y': level_height - 150, 'w': 200, 'h': 150},
                    {'x': level_width - 300, 'y': level_height - 200, 'w': 300, 'h': 200},
                ],
                'water': [],
                'goal': {'x': level_width - 200, 'y': level_height - 250, 'w': 40, 'h': 40},
                'unlocked_bombs': [0],
                'story': "The gaps are getting bigger. Good thing explosions scale.",
                'tutorial': [
                    "Use multiple bombs to cross gaps!",
                    "Place bombs while flying to chain jumps."
                ]
            },
            {  # Vertical climb
                'name': 'Higher Ground',
                'music': 'main',
                'player_start': (150, level_height - 100),
                'platforms': [
                    {'x': 0, 'y': level_height - 50, 'w': 350, 'h': 50},
                    {'x': level_width // 2 - 200, 'y': 200, 'w': 400, 'h': level_height - 200},
                ],
                'water': [],
                'goal': {'x': level_width // 2 - 20, 'y': 140, 'w': 40, 'h': 40},
                'unlocked_bombs': [0],
                'story': "Remember: You can place bombs while in the air!",
                'tutorial': [
                    "Stack bombs by placing while flying!",
                    "Detonate mid-air to go higher.",
                    "Reach the impossible."
                ]
            },
            {  # Ice platforms
                'name': 'Cold As The Floor',
                'music': 'ice',
                'player_start': (100, level_height - 150),
                'platforms': [
                    {'x': 0, 'y': level_height - 100, 'w': 250, 'h': 100},
                    {'x': level_width - 300, 'y': level_height - 250, 'w': 300, 'h': 250},
                ],
                'water': [
                    {'x': 350, 'y': level_height - 120, 'w': level_width - 750, 'h': 120},
                ],
                'goal': {'x': level_width - 200, 'y': level_height - 300, 'w': 40, 'h': 40},
                'unlocked_bombs': [0, 1],
                'story': "Ice bombs freeze water into platforms!",
                'tutorial': [
                    "Press 2 for Ice Bombs!",
                    "Freeze water into platforms.",
                    "Ice melts after a few seconds."
                ]
            },
            {  # Ice puzzle
                'name': 'Frozen Crossing',
                'music': 'ice',
                'player_start': (100, level_height - 150),
                'platforms': [
                    {'x': 0, 'y': level_height - 100, 'w': 250, 'h': 100},
                    {'x': level_width - 300, 'y': level_height - 150, 'w': 300, 'h': 150},
                ],
                'water': [
                    {'x': 350, 'y': level_height - 120, 'w': 250, 'h': 120},
                    {'x': 700, 'y': level_height - 140, 'w': 250, 'h': 140},
                ],
                'goal': {'x': level_width - 200, 'y': level_height - 200, 'w': 40, 'h': 40},
                'unlocked_bombs': [0, 1],
                'story': "Ice platforms melt quickly. Work fast.",
                'tutorial': []
            },
            {  # Ice + Fire combo
                'name': 'Chemistry Class',
                'music': 'ice',
                'player_start': (100, level_height - 150),
                'platforms': [
                    {'x': 0, 'y': level_height - 100, 'w': 250, 'h': 100},
                    {'x': level_width // 2 - 100, 'y': level_height - 250, 'w': 200, 'h': 250},
                    {'x': level_width - 350, 'y': level_height - 150, 'w': 350, 'h': 150},
                ],
                'water': [
                    {'x': 350, 'y': level_height - 120, 'w': 200, 'h': 120},
                ],
                'goal': {'x': level_width - 250, 'y': level_height - 200, 'w': 40, 'h': 40},
                'unlocked_bombs': [0, 1],
                'story': "Fire and ice. The perfect combination.",
                'tutorial': []
            },
            {  # Final level
                'name': 'The Final Experiment',
                'music': 'final',
                'player_start': (150, level_height - 100),
                'platforms': [
                    {'x': 0, 'y': level_height - 50, 'w': 300, 'h': 50},
                    {'x': level_width // 2 - 150, 'y': level_height - 200, 'w': 300, 'h': 200},
                    {'x': level_width - 350, 'y': level_height - 350, 'w': 350, 'h': 350},
                ],
                'water': [
                    {'x': 350, 'y': level_height - 80, 'w': 250, 'h': 80},
                ],
                'goal': {'x': level_width - 200, 'y': level_height - 400, 'w': 40, 'h': 40},
                'unlocked_bombs': [0, 1],
                'story': "If you reach this point... we are so sorry.",
                'tutorial': []
            }
        ]
    
    def load_level(self, level_num):
        if level_num >= len(self.levels):
            return
        
        self.level = level_num
        level_data = self.levels[level_num]
        
        self.player = Player(*level_data['player_start'])
        self.platforms = level_data['platforms'].copy()
        self.water = level_data['water'].copy()
        self.goal = level_data['goal'].copy()
        self.bombs = []
        self.explosions = []
        self.ice_platforms = []
        self.gas_clouds = []
        self.unlocked_bombs = level_data['unlocked_bombs']
        self.level_complete = False
        
        # Play level music
        if 'music' in level_data:
            play_music(level_data['music'])
        
        # Setup tutorial - position in top right
        self.tutorial_boxes = []
        if self.show_tutorial and 'tutorial' in level_data and level_data['tutorial']:
            y_offset = 20
            for text in level_data['tutorial']:
                self.tutorial_boxes.append(TutorialBox(text, WIDTH - 450, y_offset, duration=5))
                y_offset += 80
        
        # Show story text at top right
        if 'story' in level_data:
            self.tutorial_boxes.insert(0, TutorialBox(level_data['story'], WIDTH - 450, 20, duration=4))
        
    def place_bomb(self, x, y):
        if self.selected_bomb not in self.unlocked_bombs:
            return
        self.bombs.append(Bomb(x, y, self.selected_bomb))
    
    def detonate_bombs(self):
        for bomb in self.bombs[:]:
            if not bomb.detonated:
                bomb.detonated = True
                self.create_explosion(bomb)
                self.bombs.remove(bomb)
                # Play explosion sound
                play_sound('explosion')
    
    def create_explosion(self, bomb):
        if bomb.type == 0:  # Fire
            radius = 120  # Increased radius
            force = 20    # Increased force
            explosion = Explosion(bomb.x, bomb.y, bomb.type, radius)
            self.explosions.append(explosion)
            
            # Push player - calculate from center of player to bomb
            player_center_x = self.player.x + self.player.w/2
            player_center_y = self.player.y + self.player.h/2
            dx = player_center_x - bomb.x
            dy = player_center_y - bomb.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < radius:
                if dist < 1:
                    dist = 1
                dx /= dist
                dy /= dist
                # Stronger force, better for chaining
                push_force = force * (1 - dist/radius) * 2.0
                self.player.vx += dx * push_force
                self.player.vy += dy * push_force
                
        elif bomb.type == 1:  # Ice
            radius = 80
            explosion = Explosion(bomb.x, bomb.y, bomb.type, radius)
            self.explosions.append(explosion)
            
            # Freeze water
            for water in self.water:
                if self.circle_rect_collision(bomb.x, bomb.y, radius, water):
                    ice_plat = water.copy()
                    ice_plat['timer'] = 240
                    self.ice_platforms.append(ice_plat)
    
    def circle_rect_collision(self, cx, cy, r, rect):
        closest_x = max(rect['x'], min(cx, rect['x'] + rect['w']))
        closest_y = max(rect['y'], min(cy, rect['y'] + rect['h']))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (r * r)
    
    def update(self):
        if self.state != 'playing':
            return
            
        # Update tutorial boxes
        for box in self.tutorial_boxes[:]:
            if not box.update():
                self.tutorial_boxes.remove(box)
        
        # Update bombs
        for bomb in self.bombs:
            bomb.update()
            
        # Update gas clouds
        for cloud in self.gas_clouds[:]:
            cloud['timer'] -= 1
            if cloud['timer'] <= 0:
                self.gas_clouds.remove(cloud)
        
        # Update ice platforms
        for ice in self.ice_platforms[:]:
            ice['timer'] -= 1
            if ice['timer'] <= 0:
                self.ice_platforms.remove(ice)
        
        # Update explosions
        for exp in self.explosions[:]:
            if not exp.update():
                self.explosions.remove(exp)
        
        # Update player
        if self.player.update(self.platforms, self.ice_platforms):
            self.deaths += 1
            # Stop walking sound on death
            if 'walking' in sound_effects and sound_effects['walking']:
                sound_effects['walking'].stop()
            self.load_level(self.level)
        
        # Check goal - player must collide with it
        if self.player.collides(self.goal):
            if not self.level_complete:
                # Play completion sound
                play_sound('ding')
                # Stop walking sound
                if 'walking' in sound_effects and sound_effects['walking']:
                    sound_effects['walking'].stop()
            self.level_complete = True
    
    def draw(self):
        if self.state == 'menu':
            self.draw_menu()
            return
        elif self.state == 'lore':
            self.draw_lore()
            return
        elif self.state == 'settings':
            self.draw_settings()
            return
        elif self.state == 'paused':
            self.draw_game()  # Draw game underneath
            self.draw_pause()
            return
            
        # Draw game
        self.draw_game()
    
    def draw_game(self):
        # Draw background
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((30, 30, 50))
        
        # Draw platforms with tiles
        for plat in self.platforms:
            if tile_sprite:
                # Draw tiled platform
                tiles_x = int(plat['w'] / 32) + 1
                tiles_y = int(plat['h'] / 32) + 1
                for tx in range(tiles_x):
                    for ty in range(tiles_y):
                        x = plat['x'] + tx * 32
                        y = plat['y'] + ty * 32
                        if x < plat['x'] + plat['w'] and y < plat['y'] + plat['h']:
                            screen.blit(tile_sprite, (x, y))
            else:
                pygame.draw.rect(screen, GRAY, (plat['x'], plat['y'], plat['w'], plat['h']))
                pygame.draw.rect(screen, (150, 150, 150), (plat['x'], plat['y'], plat['w'], plat['h']), 2)
        
        # Draw water
        for water in self.water:
            pygame.draw.rect(screen, (50, 120, 200), (water['x'], water['y'], water['w'], water['h']))
            # Water animation
            for i in range(0, int(water['w']), 20):
                offset = math.sin((pygame.time.get_ticks() * 0.003) + i * 0.1) * 4
                pygame.draw.circle(screen, (100, 200, 255), 
                                 (int(water['x'] + i + 10), int(water['y'] + offset + 5)), 5)
        
        # Draw ice platforms
        for ice in self.ice_platforms:
            alpha = ice['timer'] / 240
            color = (int(100 + 100 * alpha), int(220 * alpha), 255)
            pygame.draw.rect(screen, color, (ice['x'], ice['y'], ice['w'], ice['h']))
            if alpha < 0.5:
                # Flashing when about to melt
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    pygame.draw.rect(screen, WHITE, (ice['x'], ice['y'], ice['w'], ice['h']), 3)
        
        # Draw gas clouds with better visibility
        for cloud in self.gas_clouds:
            alpha = cloud['timer'] / 120
            # Draw multiple layers for better visibility
            for i in range(5):
                offset_x = math.cos(i * 1.26 + pygame.time.get_ticks() * 0.002) * 20
                offset_y = math.sin(i * 1.26 + pygame.time.get_ticks() * 0.002) * 20
                radius = int((cloud['radius'] - i * 12) * alpha)
                if radius > 5:
                    # Draw filled circle with alpha for cloud effect
                    cloud_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    cloud_color = (150, 255, 150, int(100 * alpha))
                    pygame.draw.circle(cloud_surf, cloud_color, (radius, radius), radius)
                    screen.blit(cloud_surf, (int(cloud['x'] + offset_x - radius), int(cloud['y'] + offset_y - radius)))
                    # Draw outline
                    pygame.draw.circle(screen, (100, 200, 100), 
                                     (int(cloud['x'] + offset_x), int(cloud['y'] + offset_y)), 
                                     radius, 2)
        
        # Draw goal with fancy effects
        goal_pulse = abs(math.sin(pygame.time.get_ticks() * 0.004)) * 12
        
        # Draw goal box (solid yellow)
        pygame.draw.rect(screen, YELLOW, (self.goal['x'], self.goal['y'], self.goal['w'], self.goal['h']))
        
        # Draw pulsing border
        pygame.draw.rect(screen, ORANGE, 
                        (self.goal['x'] - goal_pulse/2, self.goal['y'] - goal_pulse/2, 
                         self.goal['w'] + goal_pulse, self.goal['h'] + goal_pulse), 4)
        
        # Draw star effect on goal
        for i in range(8):
            angle = i * math.pi / 4 + pygame.time.get_ticks() * 0.003
            x = self.goal['x'] + self.goal['w']/2 + math.cos(angle) * (30 + goal_pulse)
            y = self.goal['y'] + self.goal['h']/2 + math.sin(angle) * (30 + goal_pulse)
            pygame.draw.circle(screen, YELLOW, (int(x), int(y)), 4)
        
        # Draw bombs
        for bomb in self.bombs:
            bomb.draw(screen)
        
        # Draw explosions
        for exp in self.explosions:
            exp.draw(screen)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw UI with better styling
        font = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 22)
        
        # Level name with background
        level_bg = pygame.Surface((400, 40))
        level_bg.set_alpha(180)
        level_bg.fill(DARK_GRAY)
        screen.blit(level_bg, (5, 5))
        
        level_text = font.render(f"Level {self.level + 1}: {self.levels[self.level]['name']}", True, YELLOW)
        screen.blit(level_text, (15, 12))
        
        death_text = font_small.render(f"Deaths: {self.deaths}", True, WHITE)
        screen.blit(death_text, (15, 50))
        
        # Draw bomb selection with better visuals
        bomb_names = ['Fire', 'Ice']
        bomb_type_keys = ['fire', 'ice']
        bomb_colors = [(255, 100, 100), (100, 200, 255)]
        
        # Selection background
        sel_bg = pygame.Surface((140, 70))
        sel_bg.set_alpha(180)
        sel_bg.fill(DARK_GRAY)
        screen.blit(sel_bg, (5, HEIGHT - 75))
        
        y_pos = HEIGHT - 65
        for i in range(2):
            x_pos = 15 + i * 65
            if i in self.unlocked_bombs:
                # Draw slot background
                if i == self.selected_bomb:
                    pygame.draw.rect(screen, bomb_colors[i], (x_pos - 2, y_pos - 2, 54, 54), 4)
                else:
                    pygame.draw.rect(screen, GRAY, (x_pos, y_pos, 50, 50), 2)
                
                # Draw bomb sprite preview
                frames = bomb_sprites[bomb_type_keys[i]]
                if frames:
                    preview = pygame.transform.scale(frames[0], (40, 40))
                    screen.blit(preview, (x_pos + 5, y_pos + 5))
                else:
                    # Fallback circle
                    pygame.draw.circle(screen, bomb_colors[i], (x_pos + 25, y_pos + 25), 15)
                
                # Draw number
                num_surf = font_small.render(str(i + 1), True, WHITE)
                screen.blit(num_surf, (x_pos + 18, y_pos - 18))
            else:
                # Locked bomb
                pygame.draw.rect(screen, (50, 50, 50), (x_pos, y_pos, 50, 50))
                lock_text = font_small.render("?", True, GRAY)
                screen.blit(lock_text, (x_pos + 18, y_pos + 12))
        
        # Controls hint
        control_font = pygame.font.Font(None, 18)
        controls = control_font.render("LClick: Place | RClick: Detonate | R: Restart | T: Toggle Tutorial", True, WHITE)
        screen.blit(controls, (WIDTH - 480, HEIGHT - 22))
        
        # Draw tutorial boxes
        tutorial_font = pygame.font.Font(None, 22)
        for box in self.tutorial_boxes:
            box.draw(screen, tutorial_font)
        
        # Level complete screen
        if self.level_complete:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # Complete message
            complete_font = pygame.font.Font(None, 64)
            complete_text = complete_font.render("LEVEL COMPLETE!", True, YELLOW)
            text_rect = complete_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
            screen.blit(complete_text, text_rect)
            
            # Stats
            stats_font = pygame.font.Font(None, 32)
            deaths_text = stats_font.render(f"Deaths This Level: {self.deaths}", True, WHITE)
            deaths_rect = deaths_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(deaths_text, deaths_rect)
            
            # Next level prompt
            next_font = pygame.font.Font(None, 28)
            if self.level < len(self.levels) - 1:
                next_text = next_font.render("Press SPACE for next level", True, GREEN)
            else:
                next_text = next_font.render("GAME COMPLETE! Press SPACE to exit", True, GREEN)
            next_rect = next_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
            screen.blit(next_text, next_rect)
    
    def draw_menu(self):
        # Play menu music
        play_music('menu')
        
        # Draw animated background
        if background:
            screen.blit(background, (0, 0))
        else:
            # Animated gradient background
            for y in range(HEIGHT):
                color_val = int(30 + 20 * math.sin(y * 0.01 + pygame.time.get_ticks() * 0.001))
                pygame.draw.line(screen, (color_val, color_val, color_val + 20), (0, y), (WIDTH, y))
        
        # Title with explosion effect
        title_font = pygame.font.Font(None, 80)
        subtitle_font = pygame.font.Font(None, 36)
        
        # Animated title
        title_y = 100 + math.sin(pygame.time.get_ticks() * 0.002) * 10
        
        # Title shadow
        title_shadow = title_font.render("BOMBS GALORE", True, BLACK)
        screen.blit(title_shadow, (WIDTH//2 - 245, title_y + 5))
        
        # Title main text with color
        title_text = title_font.render("BOMBS GALORE", True, YELLOW)
        screen.blit(title_text, (WIDTH//2 - 250, title_y))
        
        # Subtitle
        subtitle = subtitle_font.render("A Puzzle Platformer by MrChomp", True, ORANGE)
        screen.blit(subtitle, (WIDTH//2 - 210, title_y + 80))
        
        # Draw floating bombs around title using actual sprites
        bomb_type_keys = ['fire', 'ice', 'gas', 'directional']
        for i in range(4):
            angle = i * math.pi / 2 + pygame.time.get_ticks() * 0.001
            x = WIDTH//2 + math.cos(angle) * 250
            y = 150 + math.sin(angle) * 80
            bomb_y_offset = math.sin(pygame.time.get_ticks() * 0.003 + i) * 5
            
            # Use actual bomb sprites
            frames = bomb_sprites[bomb_type_keys[i]]
            if frames:
                # Animate through frames
                frame_index = (pygame.time.get_ticks() // 100 + i * 2) % len(frames)
                bomb_img = frames[frame_index]
                # Scale up for menu
                menu_bomb = pygame.transform.scale(bomb_img, (int(bomb_img.get_width() * 1.5), int(bomb_img.get_height() * 1.5)))
                img_w, img_h = menu_bomb.get_size()
                screen.blit(menu_bomb, (int(x - img_w/2), int(y + bomb_y_offset - img_h/2)))
            else:
                # Fallback to colored circles
                bomb_colors = [(255, 100, 100), (100, 200, 255), (150, 255, 150), (200, 150, 255)]
                pygame.draw.circle(screen, bomb_colors[i], (int(x), int(y + bomb_y_offset)), 20)
                pygame.draw.circle(screen, WHITE, (int(x), int(y + bomb_y_offset)), 20, 2)
        
        # Menu options
        menu_font = pygame.font.Font(None, 48)
        option_y = 300
        
        for i, option in enumerate(self.menu_options):
            if i == self.menu_selection:
                # Selected option - larger and colored
                color = YELLOW
                text = menu_font.render(f"> {option} <", True, color)
                
                # Pulse effect
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
                option_rect = text.get_rect(center=(WIDTH//2, option_y + i * 80))
                
                # Draw glow
                glow_surf = pygame.Surface((text.get_width() + 20, text.get_height() + 20), pygame.SRCALPHA)
                glow_color = (*color[:3], 100)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=10)
                screen.blit(glow_surf, (option_rect.x - 10 - pulse/2, option_rect.y - 10 - pulse/2))
                
                screen.blit(text, option_rect)
            else:
                # Unselected option
                color = GRAY
                text = menu_font.render(option, True, color)
                text_rect = text.get_rect(center=(WIDTH//2, option_y + i * 80))
                screen.blit(text, text_rect)
        
        # Instructions at bottom
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "UP/DOWN or W/S: Navigate",
            "ENTER or SPACE: Select",
            "ESC: Quit"
        ]
        
        inst_y = HEIGHT - 150
        for inst in instructions:
            inst_text = instruction_font.render(inst, True, WHITE)
            inst_rect = inst_text.get_rect(center=(WIDTH//2, inst_y))
            screen.blit(inst_text, inst_rect)
            inst_y += 30
        
        # Credits
        credit_font = pygame.font.Font(None, 20)
        credit_text = credit_font.render("Made with Pygame | Alchemy Jam #7", True, GRAY)
        credit_rect = credit_text.get_rect(center=(WIDTH//2, HEIGHT - 30))
        screen.blit(credit_text, credit_rect)
    
    def draw_pause(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("PAUSED", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH//2, 150))
        screen.blit(title_text, title_rect)
        
        # Menu options
        menu_font = pygame.font.Font(None, 48)
        option_y = 280
        
        for i, option in enumerate(self.pause_options):
            if i == self.pause_selection:
                color = YELLOW
                text = menu_font.render(f"> {option} <", True, color)
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
                option_rect = text.get_rect(center=(WIDTH//2, option_y + i * 80))
                
                # Draw glow
                glow_surf = pygame.Surface((text.get_width() + 20, text.get_height() + 20), pygame.SRCALPHA)
                glow_color = (*color[:3], 100)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=10)
                screen.blit(glow_surf, (option_rect.x - 10 - pulse/2, option_rect.y - 10 - pulse/2))
                
                screen.blit(text, option_rect)
            else:
                color = GRAY
                text = menu_font.render(option, True, color)
                text_rect = text.get_rect(center=(WIDTH//2, option_y + i * 80))
                screen.blit(text, text_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        inst_text = instruction_font.render("UP/DOWN or W/S: Navigate | ENTER/SPACE: Select | ESC: Resume", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
        screen.blit(inst_text, inst_rect)
    
    def draw_settings(self):
        # Draw background
        if background:
            screen.blit(background, (0, 0))
        else:
            for y in range(HEIGHT):
                color_val = int(30 + 20 * math.sin(y * 0.01 + pygame.time.get_ticks() * 0.001))
                pygame.draw.line(screen, (color_val, color_val, color_val + 20), (0, y), (WIDTH, y))
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("SETTINGS", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        # Settings options
        menu_font = pygame.font.Font(None, 42)
        option_y = 250
        
        for i, option in enumerate(self.settings_options):
            if i == self.settings_selection:
                color = YELLOW
                
                # Show current value for volume settings
                if i == 0:  # Music Volume
                    display_text = f"> MUSIC VOLUME: {int(self.music_volume * 100)}% <"
                elif i == 1:  # SFX Volume
                    display_text = f"> SFX VOLUME: {int(self.sfx_volume * 100)}% <"
                else:
                    display_text = f"> {option} <"
                
                text = menu_font.render(display_text, True, color)
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
                option_rect = text.get_rect(center=(WIDTH//2, option_y + i * 80))
                
                # Draw glow
                glow_surf = pygame.Surface((text.get_width() + 20, text.get_height() + 20), pygame.SRCALPHA)
                glow_color = (*color[:3], 100)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=10)
                screen.blit(glow_surf, (option_rect.x - 10 - pulse/2, option_rect.y - 10 - pulse/2))
                
                screen.blit(text, option_rect)
            else:
                color = GRAY
                
                # Show current value for volume settings
                if i == 0:  # Music Volume
                    display_text = f"MUSIC VOLUME: {int(self.music_volume * 100)}%"
                elif i == 1:  # SFX Volume
                    display_text = f"SFX VOLUME: {int(self.sfx_volume * 100)}%"
                else:
                    display_text = option
                
                text = menu_font.render(display_text, True, color)
                text_rect = text.get_rect(center=(WIDTH//2, option_y + i * 80))
                screen.blit(text, text_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "UP/DOWN or W/S: Navigate",
            "LEFT/RIGHT or A/D: Adjust Volume",
            "ENTER/SPACE or ESC: Back"
        ]
        
        inst_y = HEIGHT - 120
        for inst in instructions:
            inst_text = instruction_font.render(inst, True, WHITE)
            inst_rect = inst_text.get_rect(center=(WIDTH//2, inst_y))
            screen.blit(inst_text, inst_rect)
            inst_y += 30
    
    def draw_lore(self):
        # Play menu music
        play_music('menu')
        
        # Draw background
        if background:
            screen.blit(background, (0, 0))
        else:
            for y in range(HEIGHT):
                color_val = int(30 + 20 * math.sin(y * 0.01 + pygame.time.get_ticks() * 0.001))
                pygame.draw.line(screen, (color_val, color_val, color_val + 20), (0, y), (WIDTH, y))
        
        # Get current lore page
        page = self.lore_text[self.lore_page]
        
        # Title
        title_font = pygame.font.Font(None, 60)
        title_text = title_font.render(page['title'], True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH//2, 80))
        screen.blit(title_text, title_rect)
        
        # Draw decorative line under title
        line_y = 120
        pygame.draw.line(screen, ORANGE, (WIDTH//2 - 200, line_y), (WIDTH//2 + 200, line_y), 3)
        
        # Lore text
        text_font = pygame.font.Font(None, 28)
        text_y = 160
        
        for line in page['text']:
            if line:  # Non-empty line
                text_surf = text_font.render(line, True, WHITE)
                text_rect = text_surf.get_rect(center=(WIDTH//2, text_y))
                screen.blit(text_surf, text_rect)
            text_y += 30
        
        # Page indicator
        page_font = pygame.font.Font(None, 32)
        page_indicator = page_font.render(f"Page {self.lore_page + 1} / {len(self.lore_text)}", True, GRAY)
        page_rect = page_indicator.get_rect(center=(WIDTH//2, HEIGHT - 100))
        screen.blit(page_indicator, page_rect)
        
        # Navigation instructions
        instruction_font = pygame.font.Font(None, 24)
        
        if self.lore_page < len(self.lore_text) - 1:
            next_inst = instruction_font.render("Press RIGHT or D for Next Page", True, GREEN)
        else:
            next_inst = instruction_font.render("Press ENTER to Start Game", True, GREEN)
        next_rect = next_inst.get_rect(center=(WIDTH//2, HEIGHT - 60))
        screen.blit(next_inst, next_rect)
        
        if self.lore_page > 0:
            prev_inst = instruction_font.render("Press LEFT or A for Previous Page", True, CYAN)
            prev_rect = prev_inst.get_rect(center=(WIDTH//2, HEIGHT - 35))
            screen.blit(prev_inst, prev_rect)
        
        back_inst = instruction_font.render("Press ESC to Return to Menu", True, WHITE)
        back_rect = back_inst.get_rect(center=(WIDTH//2, HEIGHT - 10))
        screen.blit(back_inst, back_rect)
        
        # Draw small floating bombs for decoration
        bomb_type_keys = ['fire', 'ice']
        positions = [(WIDTH//2 - 150, HEIGHT - 180), (WIDTH//2 + 150, HEIGHT - 180)]
        
        for i in range(2):
            x, y_base = positions[i]
            y = y_base + math.sin(pygame.time.get_ticks() * 0.002 + i) * 20
            
            frames = bomb_sprites[bomb_type_keys[i]]
            if frames:
                frame_index = (pygame.time.get_ticks() // 100 + i * 2) % len(frames)
                bomb_img = frames[frame_index]
                img_w, img_h = bomb_img.get_size()
                screen.blit(bomb_img, (int(x - img_w/2), int(y - img_h/2)))

def main():
    game = Game()
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Menu controls
                if game.state == 'menu':
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game.menu_selection = (game.menu_selection - 1) % len(game.menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game.menu_selection = (game.menu_selection + 1) % len(game.menu_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if game.menu_selection == 0:  # Start Game
                            game.start_game()
                        elif game.menu_selection == 1:  # Lore
                            game.state = 'lore'
                            game.lore_page = 0
                        elif game.menu_selection == 2:  # Settings
                            game.state = 'settings'
                            game.came_from_pause = False
                        elif game.menu_selection == 3:  # Toggle Tutorial
                            game.show_tutorial = not game.show_tutorial
                            game.menu_options[3] = f"TUTORIAL: {'ON' if game.show_tutorial else 'OFF'}"
                        elif game.menu_selection == 4:  # Quit
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        # Mute/unmute music
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                
                # Game controls
                elif game.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        game.state = 'menu'
                        game.menu_selection = 0
                        # Stop walking sound when returning to menu
                        if 'walking' in sound_effects and sound_effects['walking']:
                            sound_effects['walking'].stop()
                    elif event.key == pygame.K_m:
                        # Mute/unmute music
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                    elif event.key == pygame.K_r:
                        # Stop walking sound on restart
                        if 'walking' in sound_effects and sound_effects['walking']:
                            sound_effects['walking'].stop()
                        game.load_level(game.level)
                    elif event.key == pygame.K_t:
                        game.show_tutorial = not game.show_tutorial
                        game.menu_options[3] = f"TUTORIAL: {'ON' if game.show_tutorial else 'OFF'}"
                        if game.show_tutorial:
                            game.load_level(game.level)
                    elif event.key == pygame.K_1 and 0 in game.unlocked_bombs:
                        game.selected_bomb = 0
                    elif event.key == pygame.K_2 and 1 in game.unlocked_bombs:
                        game.selected_bomb = 1
                    elif event.key == pygame.K_SPACE and game.level_complete:
                        if game.level < len(game.levels) - 1:
                            game.deaths = 0
                            game.load_level(game.level + 1)
                        else:
                            print("GAME COMPLETE! Thanks for playing!")
                            game.state = 'menu'
                            game.menu_selection = 0
            
            if event.type == pygame.MOUSEBUTTONDOWN and game.state == 'playing' and not game.level_complete:
                if event.button == 1:  # Left click - place bomb
                    mx, my = pygame.mouse.get_pos()
                    game.place_bomb(mx, my)
                elif event.button == 3:  # Right click - detonate
                    game.detonate_bombs()
        
        if game.state == 'playing' and not game.level_complete:
            game.update()
        game.draw()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()