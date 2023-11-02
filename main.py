from pyray import *
import math
import random
import opensimplex

# from player import Player

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "2D Voxels")
set_target_fps(60)

WORLD_WIDTH = 128
WORLD_HEIGHT = 64

BLOCK_TABLE = {
    0:"Grass",
    1:"Dirt",
    2:"Stone",
    3:"Sand",
    4:"Log",
    5:"Leaves",
    6:"Cobblestone",
    7:"Planks",
    8:"Bedrock",
    63:"Null",
}

texture_sheet = load_texture("resources/textures.png")

camerapos = Vector2(0, 0)

camera = Camera2D()
camera.rotation = 0.0
camera.zoom = 3.0

world = [[-1 for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]

def world_to_cam(world_pos):
    cam_x = int(world_pos.x*16)
    cam_y = int(world_pos.y*-16)
    return Vector2(cam_x, cam_y)

def cam_to_world(cam_pos):
    world_x = math.floor(cam_pos.x/16)
    world_y = math.floor(cam_pos.y/-16)
    return Vector2(world_x, world_y)

def draw_voxel(x, y, id):
    if (id == -1):
        return 

    i = math.floor(id % 8)
    j = math.floor(id / 8)

    position = Vector2(x*16, y*-16)
    frameRec = Rectangle(i*16, j*16, 16, 16)
    draw_texture_rec(texture_sheet, frameRec, position, WHITE)

def draw_world():
    for x in range(0, WORLD_WIDTH):
        for y in range(0, WORLD_HEIGHT):
            draw_voxel(x, y, world[x][y])

def generate_flat_world():

    # Bedrock
    for x in range(0, WORLD_WIDTH):
        world[x][0] = 8

    # Stone
    for x in range(0, WORLD_WIDTH):
        for y in range(1, 4):
            world[x][y] = 2
    
    # Dirt
    for x in range(0, WORLD_WIDTH):
        for y in range(4, 5):
            world[x][y] = 1
    
    # Grass
    for x in range(0, WORLD_WIDTH):
        for y in range(5, 6):
            world[x][y] = 0

def generate_moutin_world(seed):
    opensimplex.seed(seed)
    random.seed(seed)

    for x in range(0, WORLD_WIDTH):
        y = (round(opensimplex.noise2(x=x/15, y=0) * 6)+20)+round(opensimplex.noise2(x=x/2, y=10))
        # Grass
        world[x][y] = 0
        
        # Dirt
        for y2 in range(y-5, y):
            world[x][y2] = 1
        
        # Stone
        for y3 in range(1, y-5):
            world[x][y3] = 2

        # Clean and elegent tree generation
        if (random.randrange(0, 15) == 5):
            # Logs
            world[x]  [y+1] = 4
            world[x]  [y+2] = 4

            # Leaves
            world[x-2][y+3] = 5
            world[x-1][y+3] = 5
            world[x]  [y+3] = 5
            world[x+1][y+3] = 5
            world[x+2][y+3] = 5

            world[x-2][y+4] = 5
            world[x-1][y+4] = 5
            world[x]  [y+4] = 5
            world[x+1][y+4] = 5
            world[x+2][y+4] = 5

            world[x-1][y+5] = 5
            world[x]  [y+5] = 5
            world[x+1][y+5] = 5

            world[x]  [y+6] = 5
   
    # Bedrock
    for x in range(0, WORLD_WIDTH):
        world[x][0] = 8

        if (random.randrange(0, 2) == 1):
            world[x][1] = 8
        
        if (random.randrange(0, 2) == 1):
            world[x][2] = 8    

generate_moutin_world(round(random.random()*10))

camerapos = world_to_cam(Vector2(1, 1))

cam_bounds = world_to_cam(Vector2(WORLD_WIDTH, WORLD_HEIGHT))

block = 0

while not window_should_close():

    if is_key_down(KEY_D):
        camerapos.x += 5
    if is_key_down(KEY_A):
        camerapos.x -= 5
    if is_key_down(KEY_W):
        camerapos.y -= 5
    if is_key_down(KEY_S):
        camerapos.y += 5

    temp_key = get_char_pressed()
    if (temp_key >= 48 and temp_key <= 57):
        if ((temp_key - 48) == 0):
            block = 63
        else:
            block = (temp_key - 48)-1

    cam_bounds
    camerapos.x = clamp(camerapos.x, 0, cam_bounds.x-SCREEN_WIDTH/3)
    camerapos.y = clamp(camerapos.y, cam_bounds.y+16, 16-SCREEN_HEIGHT/3)

    if is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
        # Get the mouse position when the left mouse button is pressed
        mouse_screen_pos = get_mouse_position()
        mouse_pos = get_screen_to_world_2d(mouse_screen_pos, camera)
        world_pos = cam_to_world(mouse_pos)

        world[int(world_pos.x)][int(world_pos.y+1)] = -1
    if is_mouse_button_pressed(MOUSE_RIGHT_BUTTON):
        mouse_screen_pos = get_mouse_position()
        mouse_pos = get_screen_to_world_2d(mouse_screen_pos, camera)
        world_pos = cam_to_world(mouse_pos)

        world[int(world_pos.x)][int(world_pos.y+1)] = block

    begin_drawing()

    clear_background((0, 135, 206, 250))
    
    begin_mode_2d(camera)

    camera.target = camerapos

    draw_world()

    mouse_screen_pos = get_mouse_position()
    mouse_pos = get_screen_to_world_2d(mouse_screen_pos, camera)
    pos = world_to_cam(cam_to_world(mouse_pos))

    draw_rectangle_lines(int(pos.x), int(pos.y-16), 16, 16, BLACK)

    end_mode_2d()

    fps_text = f"{get_fps()} FPS"
    draw_rectangle(0, 0, measure_text(fps_text, 20)+10, 20, (20, 20, 20, 128))
    draw_text(fps_text, 5, 0, 20, WHITE)

    pos_text = f"Positon: x:{int(cam_to_world(camerapos).x)} y:{int(cam_to_world(camerapos).y)}"
    draw_rectangle(0, 20, measure_text(pos_text, 20)+10, 20, (20, 20, 20, 128))
    draw_text(pos_text, 5, 20, 20, WHITE)

    block_text = f"Selected Block: {BLOCK_TABLE[block]}"
    draw_rectangle(0, 40, measure_text(block_text, 20)+10, 20, (20, 20, 20, 128))
    draw_text(block_text, 5, 40, 20, WHITE)
    
    
    # draw_text(f"Positon: x:{int(cam_to_world(camerapos).x)} y:{int(cam_to_world(camerapos).y)}", 2, 20, 20, WHITE)
    # draw_text(f"Selected Block: {BLOCK_TABLE[block]}", 2, 40, 20, WHITE)

    #draw_rectangle(0, 0, SCREEN_WIDTH, 20, (20, 20, 20, 128))
    #draw_text(f"{get_fps()} FPS     Positon: x:{int(cam_to_world(camerapos).x)} y:{int(cam_to_world(camerapos).y)}     Selected Block: {BLOCK_TABLE[block]}", 2, 0, 20, WHITE)

    controlls_text = "Controlls: [W] [S] [A] [D] to move, [0]..[9] to select a block, [LMB] to break a block, [RMB] to place a block, [ESC] to exit"
    draw_rectangle(0, SCREEN_HEIGHT-20, measure_text(controlls_text, 20)+10, 20, (20, 20, 20, 128))
    draw_text(controlls_text, 5, SCREEN_HEIGHT-20, 20, WHITE)

    end_drawing()

close_window()
