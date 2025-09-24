import pygame
import random
import pygame.surfarray as surfarray

pygame.init()
screen_width, screen_height = 800, 800
frame_width, frame_height = 32, 32
        
#############################################################################################
def replace_color(image, old_color, new_color):
    img_copy = image.copy()
    pxarray = pygame.PixelArray(img_copy)
    pxarray.replace(old_color, new_color)
    del pxarray
    return img_copy
#############################################################################################
class AnimationPool():
    pathss = []
    animationss = []
    
    @classmethod
    def check_exists(cls, paths):
        if paths in cls.pathss:
            return cls.pathss.index(paths)
        return -1
    
    def __init__(self):
        pass
    
class Animation():
    def __init__(self, animation_paths, frame_width, frame_height, color):
        h = hash((animation_paths, color))
        check_exists = AnimationPool.check_exists(h)
        if check_exists == -1:
            if color == -1:
                self.animations = self.cut_frame(animation_paths, frame_width, frame_height, -1)
                AnimationPool.pathss.append(h)
                AnimationPool.animationss.append(self.animations)
            else:
                self.animations = self.cut_frame(animation_paths, frame_width, frame_height, color)
                AnimationPool.pathss.append(h)
                AnimationPool.animationss.append(self.animations)
        else:
            self.animations = AnimationPool.animationss[check_exists]
        
        self.animation = random.randint(0, len(self.animations) - 1)
        self.index = 0
    
    def check_exist_animation(self, n):
        if self.animations[n] == -1:
            return False
        return True
    
    def set_random_animation(self):
        self.animation = random.randint(0, len(self.animations) - 1)
        self.index = 0
    def set_animation(self, n):
        self.animation = n
        self.index = 0
    
    def stop(self):
        return self.animations[self.animation][self.index]
    
    def has_next_frame(self):
        if self.index >= len(self.animations[self.animation]):
            return False
        return True
    
    def get_next_frame(self):
        self.index = self.index % len(self.animations[self.animation])
        a = self.animations[self.animation][self.index]
        self.index += 1
        return a
    
   
    
    
    def cut_frame(self, animation_links, frame_width, frame_height, color):
        animations = []
        for x in animation_links:
            if x == -1:
                animations.append(-1)
            else:            
                animation_image = pygame.image.load(x).convert_alpha()
                if color != -1:
                    animation_image = replace_color(animation_image, (53, 177, 35), color)
                animation = []
                w, h = animation_image.get_size()
                
                for y in range(int (w / frame_width)):
                    animation.append(animation_image.subsurface(frame_width * y, 0, frame_width, frame_height))
                animations.append(animation)
        return animations

        
class LayerSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.child = []
        self.parent = None
        self.image = None
        self.rect = None
    
    def update(self):
        self.update_myself()
        for x in self.child:
            x.update()
            self.image.blit(x.image, (x.rect.x, x.rect.y))
        
    
    
    def update_myself (self):
        pass
    def update_one_time(self):
        self.update_one_time_myself()
        for x in self.child:
            x.update_one_time()
        pass
    def update_one_time_myself (self):
        pass
    
    def add_child_freestyle(self, child):
        self.child.append(child)
        child.parent = self
    def add_child_vertical(self, child, rate):
        rate_all = 0
        for x in rate:
            rate_all += x
        
        current_y = 0
        for i,x in enumerate(child):
            self.child.append(x)
            x.parent = self
            x.rect = pygame.Rect((0, current_y), (self.rect.width, self.rect.height * rate[i]/rate_all))
            current_y += self.rect.height * rate[i]/rate_all

class LayerSpriteWithAnimation(LayerSprite):
       
    def __init__(self):
        super().__init__()
        self.loop_time = 0.12
        self.loop_clock = pygame.time.get_ticks()
        self.animation = None
    def set_animation (self,animation_paths, frame_width, frame_height):
        self.animation_singleton = False
        self.animation = Animation(animation_paths, frame_width, frame_height, -1)
        
    def update_myself (self):
        if (pygame.time.get_ticks() - self.loop_clock) / 1000 > self.loop_time:
            self.loop_clock = pygame.time.get_ticks()
            self.image = self.animation.get_next_frame()
            self.update_myself_in_loop()
    def update_myself_in_loop(self):
        pass
    def update_one_time_myself(self):
        self.image = self.animation.get_next_frame()
    
class Cloud(LayerSpriteWithAnimation):
    def __init__(self):
        super().__init__()
        self.move_mode = 0.2
    def update_myself_in_loop(self):
        if self.move_mode == 1 and self.rect.x > self.parent.rect.width * 0.9:
            self.move_mode = -1
        if self.move_mode == -1 and self.rect.x < self.parent.rect.width * 0.1:
            self.move_mode = 1
        self.rect.x += self.move_mode

        
class Token(LayerSprite):
    def __init__(self, color):
        super().__init__()
        self.token_animation = None
        self.second_token_animation = None
        self.curent_animation = None
        self.animation_mode = 1
        
        self.flip = bool(random.randint(0,1))
        
        self.image = None
        self.rect = None
        
        self.loop_clock = pygame.time.get_ticks()
        self.next_animation_clock = -1
        
        self.next_animation_time_range = (0, 5)
        self.next_animation_time = 0
        self.loop_time  = 0.12
         
        self.color = color
    
    def set_animation(self, animation_paths, frame_width, frame_height):
        self.token_animation = Animation(animation_paths, frame_width, frame_height, self.color)
        self.curent_animation = self.token_animation
        
    
    def set_second_animation(self, animation_paths, frame_width, frame_height):
        self.second_token_animation = Animation(animation_paths, frame_width, frame_height, self.color)
        
        
    def update_one_time(self):
        self.image = pygame.transform.flip(self.curent_animation.get_next_frame(),self.flip,False)
        #self.image = replace_color(self.image, (53, 177, 35), self.color)
        
    def update(self):
        if (pygame.time.get_ticks() - self.loop_clock) / 1000 > self.loop_time:
            self.loop_clock = pygame.time.get_ticks()
        
            #case: [animation keep going]
            if self.curent_animation.has_next_frame():
                self.image = pygame.transform.flip(self.curent_animation.get_next_frame(),self.flip,False)
                #self.image = replace_color(self.image, (53, 177, 35), self.color)                
            #case: [animation complete] AND [anti_action mode]
            elif self.animation_mode == -1 :
                self.animation_mode = 1
                self.curent_animation = self.token_animation
                self.curent_animation.set_random_animation()
                #self.image = self.curent_animation.get_next_frame()         
            #case: [animation complete] AND [action mode] AND [not exists relative anti action]
            elif self.second_token_animation.check_exist_animation(self.token_animation.animation) == False:
                if self.next_animation_clock == -1:
                    self.next_animation_time = random.randint(self.next_animation_time_range[0], self.next_animation_time_range[1])
                    self.next_animation_clock = pygame.time.get_ticks()
                if (pygame.time.get_ticks() - self.next_animation_clock)/1000 > self.next_animation_time:
                    self.animation_mode = 1
                    self.curent_animation = self.token_animation
                    self.curent_animation.set_random_animation()
                    #self.image = self.curent_animation.get_next_frame()
                    self.next_animation_clock = -1
            #case: [animation complete] AND [action mode] AND [exists relative anti action]
            else:
                if self.next_animation_clock == -1:
                    self.next_animation_time = random.randint(self.next_animation_time_range[0], self.next_animation_time_range[1])
                    self.next_animation_clock = pygame.time.get_ticks()
                if (pygame.time.get_ticks() - self.next_animation_clock)/1000 > self.next_animation_time:
                    self.animation_mode = -1
                    self.curent_animation = self.second_token_animation
                    self.curent_animation.set_animation(self.token_animation.animation)
                    #self.image = self.curent_animation.get_next_frame()
                    self.next_animation_clock = -1


    
#############################################################################################
clock = pygame.time.Clock()

screen_layer = LayerSprite()
screen_layer.image = pygame.display.set_mode((screen_width, screen_height))
def aaa (self):
    self.image.fill((255,255,255))
screen_layer.update_myself = aaa.__get__(screen_layer, LayerSprite)
screen_layer.rect = screen_layer.image.get_rect()

sky_layer = LayerSprite()
def aaa(self):
    self.image = pygame.Surface((self.rect.width,self.rect.height), pygame.SRCALPHA)
sky_layer.update_myself = aaa.__get__(sky_layer, LayerSprite)

ground_layer = LayerSprite()
def aaa (self):
    self.image = pygame.Surface((self.rect.width,self.rect.height), pygame.SRCALPHA)
    pygame.draw.line(self.image, (0, 0, 0), (0, 0), (self.rect.width, 0), 3)
ground_layer.update_myself = aaa.__get__(ground_layer, LayerSprite)

screen_layer.add_child_vertical((sky_layer,ground_layer), (1,1))

sun_layer = LayerSpriteWithAnimation()
sky_layer.add_child_freestyle(sun_layer)
sun_layer.rect = pygame.Rect((0.8 * sun_layer.parent.rect.width,0.2 * sun_layer.parent.rect.height),(frame_width, frame_height))
sun_layer.set_animation((".\\asset\\sky\\sun.png",), 32, 32)

cloud_layer = Cloud()
sky_layer.add_child_freestyle(cloud_layer)
cloud_layer.rect = pygame.Rect((0.2 * sun_layer.parent.rect.width,0.22 * sun_layer.parent.rect.height),(frame_width, frame_height))
cloud_layer.set_animation((".\\asset\\sky\\cloud.png",), 32, 32)
cloud_layer.loop_time = 0.01

token_animation_links = (
    ".\\asset\\ngap.png",
    ".\\asset\\gaydau.png",
    ".\\asset\\ngoi1.png",
    ".\\asset\\ngoixom1.png",
    ".\\asset\\chao.png",
    ".\\asset\\ngu1.png",
    ".\\asset\\dabanh.png"
)
second_token_animation_links = (
    -1,
    -1,
    ".\\asset\\ngoi2.png",
    ".\\asset\\ngoixom2.png",
    -1,
    ".\\asset\\ngu2.png",
    -1
)
for x in range(40):
    if x < 2:
        color = (183, 17, 17)
    elif x < 5:
        color = (67, 190, 42)
    elif x < 6:
        color = (49, 138, 230)
    else:
        color = (140, 48, 224)
        
    token_layer = Token(color)
    token_layer.set_animation(token_animation_links, frame_width, frame_height)
    token_layer.set_second_animation(second_token_animation_links, frame_width, frame_height)
    ground_layer.add_child_freestyle(token_layer)
    rand_x = random.randint(frame_width, token_layer.parent.rect.width - frame_width)
    rand_y = random.randint(frame_height, token_layer.parent.rect.height - frame_height)
    token_layer.rect = pygame.Rect((rand_x,rand_y),(frame_width, frame_height))


ground_layer.child.sort(key=lambda s: s.rect.bottom)
screen_layer.update_one_time()

#############################################################################################
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen_layer.update()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
