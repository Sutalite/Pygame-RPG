from CONST import *
from Map import *
from UI import *
from Inventory import *
import WaveManager

class Player:

    Player_right = Map.LoadTexture(PLAYER_RIGHT)
    Player_left = Map.LoadTexture(PLAYER_LEFT)

    def TakeDamage(self, damage):
        if self.dead or self.CountDownShowDamage > 0:
            return
        self.health -= damage
        self.DamageTaken = str(damage)
        self.showDamage = True
        self.CountDownShowDamage = 1000
        self.CountDownRegen = 4000
        if self.health <= 0:
            self.dead = True

    def DrawPlayerLife(self):
        #DRAW HEALTH
        pygame.draw.rect(Globals.window, COLOR_WHITE, (20,10,100,10), 1)
        life = Clamp(self.health,0,self.maxHealth)
        if life > 0:
            healthRatio = life / self.maxHealth
            pygame.draw.rect(Globals.window, COLOR_GREEN, (21,11, int(98 * healthRatio), 8))

    def draw(self):
        if self.CountDownRegen is 0:
            self.health += Globals.deltaTime * RegenSpeed
            self.health = Clamp(self.health, 0, self.maxHealth)

        self.DrawPlayerLife()

        if self.ActiveWeapon is not None:
            self.ActiveWeapon.draw()

        #Draw taken damages
        if self.showDamage and not self.dead:
            DamageText = Damage_font.render(self.DamageTaken, True, (255,0,0))
            surface = pygame.Surface(DamageText.get_rect().size, pygame.SRCALPHA)
            surface.blit(DamageText,(0,0))
            Globals.window.blit(surface, (WINDOW_WIDTH / 2,self.y - 25))


        #Draw Player
        if not self.dead:
            x = WINDOW_WIDTH / 2

            sprite = Player.Player_left
            if self.velocity is not 0:
                sprite = Player.Player_right if self.velocity is 1 else Player.Player_left
            else:
                sprite = self.lastSprite

            self.lastSprite = sprite

            Globals.window.blit(sprite,(x,self.y))

            item = self.inventory.ItemsManager.CheckCollision()
            if item is not None:
                self.inventory.AddItem(item)


    def move(self):
        if self.dead: #Move only if alive
            return


        self.CanMoveLeft = not Globals.map.GetCollsionAt(int(self.x / TILE_SIZE + 25), int(self.y / TILE_SIZE))
        self.CanMoveRight = not Globals.map.GetCollsionAt(int(self.x / TILE_SIZE + 26), int(self.y / TILE_SIZE))

        if (self.velocity is 1 and self.CanMoveRight) or (self.velocity is -1 and self.CanMoveLeft):
            self.x += self.velocity * PlayerSpeed * Globals.deltaTime

        self.x = Clamp(self.x, -400, Globals.mapX)
        Globals.playerX = self.x
        Globals.playerY = self.y

        if not Globals.map.GetCollsionAt(int(self.x / TILE_SIZE + 25),int(self.y / TILE_SIZE + 1)):
            self.y += 1

        if self.CountDownShowDamage > 0:
            self.CountDownShowDamage -= Globals.deltaTime
        else:
            self.CountDownShowDamage = 0
            self.showDamage = False

        if self.CountDownRegen > 0:
            self.CountDownRegen -= Globals.deltaTime
            self.CountDownRegen = Clamp(self.CountDownRegen, 0, 5000)

    def handle_event(self,event):
        keys = pygame.key.get_pressed()

        #ON KEY PRESSED
        if event.type is pygame.KEYDOWN:
            if self.velocity is 0:
                if keys[KEY_LEFT]:
                    self.velocity = -1
                if keys[KEY_RIGHT]:
                    self.velocity = 1

            if event.key == pygame.K_r and self.ActiveWeapon is not None:
                self.ActiveWeapon.reload()

            self.ActiveWeapon = self.inventory.GetItem(chr(event.key), self.ActiveWeapon)

        #ON KEY RELEASED
        if event.type is pygame.KEYUP:
            if self.velocity is 1 and event.key is KEY_RIGHT:
                self.velocity = 0
            if self.velocity is -1 and event.key is KEY_LEFT:
                self.velocity = 0

        #ON MOUSE BUTTON CLICK
        if event.type is pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]: #LEFT CLICK
                    x = pygame.mouse.get_pos()[0] + int(Globals.playerX)
                    y = pygame.mouse.get_pos()[1] + int(Globals.playerY / TILE_SIZE - TILE_SIZE * 2)
                    if self.ActiveWeapon is not None:
                        if self.ActiveWeapon.ammo > 0:
                            self.Shoot(x,y)
                        else:
                            self.ActiveWeapon.reload()

    def Shoot(self,x,y):
        self.ActiveWeapon.ammo -= 1
        for e in WaveManager.Wave.Ennemies:
            e.IsShooted(x,y,self.attack)

    def __init__(self, window, map):
        self.x = 0
        self.y = WINDOW_HEIGHT - 6 * TILE_SIZE
        Globals.window = window
        self.velocity = 0

        self.map = map

        self.maxHealth = 100
        self.health = 0
        self.dead = False

        self.showDamage = False
        self.DamageTaken = ""
        self.CountDownShowDamage = 0
        self.CountDownRegen = 0

        self.lastSprite = Player.Player_left

        self.CanMoveLeft = True
        self.CanMoveRight = True

        self.inventory = Inventory(5)

        self.attack = 25
        self.ActiveWeapon = None

        self.draw()
