import pygame
import button
import csv

pygame.init()

FPS = 60
clock = pygame.time.Clock()

width = 800
height = 640

lower_margin = 100
side_margin = 300

root = pygame.display.set_mode((width + side_margin, height + lower_margin))
pygame.display.set_caption("Редактор уровней")

rows = 16
max_clos = 150
tile_size = height // rows
tile_types = 21
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
lvl = 0

#добавлние картнок
pine1_img = pygame.image.load('blek/pine1.png').convert_alpha()
pine2_img = pygame.image.load('blek/pine2.png').convert_alpha()
mountain_img = pygame.image.load('blek/mountain.png').convert_alpha()
sky_img = pygame.image.load('blek/sky_cloud.png').convert_alpha()

img_list = []
for x in range(tile_types):
    img = pygame.image.load(f'sprites/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

save_img = pygame.image.load('sprites/save_btn.png').convert_alpha()
load_img = pygame.image.load('sprites/load_btn.png').convert_alpha()

#colors
green = (144, 201, 120)
white = (255,255,255)
red = (200, 25, 25)
brown = (37, 37, 37)

font = pygame.font.SysFont('Arial', 20)

world_data = []
for row in range(rows):
    r = [-1] * max_clos
    world_data.append(r)

for tile in range(0, max_clos):
    world_data[rows - 1][tile] = 0

def dt(text, font, tc, x, y):
    img = font.render(text, True, tc)
    root.blit(img,(x, y))

def draw_bg():
    root.fill(green)
    width = sky_img.get_width()
    for x in range(4):
        root.blit(sky_img, ((x * width) - scroll * 0.5, 0))
        root.blit(mountain_img,((x * width) - scroll * 0.6, height - mountain_img.get_height() - 300))
        root.blit(pine1_img, ((x * width) - scroll * 0.7, height - pine1_img.get_height() - 150))
        root.blit(pine2_img, ((x * width) - scroll * 0.8, height - pine2_img.get_height()))

def draw_grid():
    #lines
    for c in range(max_clos + 1):
        pygame.draw.line(root, white, (c * tile_size - scroll, 0),(c * tile_size - scroll, height))
    #clos
    for c in range(rows + 1):
        pygame.draw.line(root, white, (0, c * tile_size),(width, c * tile_size))

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                root.blit(img_list[tile], (x * tile_size - scroll, y * tile_size))

save_button = button.Button(width // 2, height + lower_margin - 70, save_img, 1)
load_button = button.Button(width // 2 + 200, height + lower_margin - 70, load_img, 1)

button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(width + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

run = True

while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()

    dt(f'уровень: {lvl}', font, brown, 10, height + lower_margin - 90)
    dt('UP или DOWN чтобы сменить уровень', font, brown, 10, height + lower_margin - 60)

    if save_button.draw (root):
        with open (f'level {lvl} _data.csv ','w', newline ='') as csvfile: 
            writer = csv.writer (csvfile, delimiter =',') 
            for row  in world_data: 
                writer.writerow (row) 
    if load_button.draw (root): 
        scroll = 0 
        with open (f'level {lvl} _data.csv ', newline ='') as csvfile: 
            reader= csv.reader(csvfile, delimiter = ',') 
            for x, row in enumerate (reader): 
                for y, tile in enumerate (row): 
                    world_data [x] [y]=int(tile)

    pygame.draw.rect(root, green, (width, 0, side_margin, height))

    button_count = 0
    for button_count,i in enumerate(button_list):
        if i.draw(root):
            current_tile = button_count

    pygame.draw.rect(root, red, button_list[current_tile].rect, 5)

    if scroll_left == True and scroll > 0:
        scroll -=5 * scroll_speed
    if scroll_right == True and scroll < (max_clos * tile_size) - width:
        scroll +=5 * scroll_speed

    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // tile_size
    y = pos[1] // tile_size

    if pos[0] < width and pos[1] < height:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                scroll_left = True
            if event.key == pygame.K_d:
                scroll_right = True
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_UP:
                lvl += 1
            if event.key == pygame.K_DOWN and lvl > 0:
                lvl -= 1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                scroll_left = False
            if event.key == pygame.K_d:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
quit()