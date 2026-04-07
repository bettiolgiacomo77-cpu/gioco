import arcade
import random

# --- COSTANTI ---
SCREEN_WIDTH = 920
SCREEN_HEIGHT = 620
SCREEN_TITLE = "Llama Lama - Survival Runner"

GRAVITY = 1
PLAYER_JUMP_SPEED = 18
PLAYER_AUTO_SPEED = 5 

class giocoplatformer(arcade.Window):

    def __init__(self, larghezza, altezza, titolo):
        super().__init__(larghezza, altezza, titolo)
        
        self.lista_babbo = None
        self.lista_grano = None
        self.wall_list = None
        self.lista_spuntoni = None
        
        self.babbo = None
        self.physics_engine = None
        self.ultimo_x_generato = 0
        self.ultimo_x_grano = 0
        self.timer_fame = 20.0
        
        # Stato del gioco
        self.gioco_attivo = False 
        
        self.camera = arcade.camera.Camera2D()
        self.background = arcade.load_texture("./assets/foresta.jpg")
        self.suono_munch = arcade.load_sound("./assets/mangiare.mp3")

    def setup(self):
        self.ultimo_x_generato = 0
        self.ultimo_x_grano = 0
        self.ultima_y_piattaforma = 150 
        self.timer_fame = 20.0
        self.primo_avvio = True 

        self.lista_babbo = arcade.SpriteList()
        self.lista_grano = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.lista_spuntoni = arcade.SpriteList()

        self.babbo = arcade.Sprite("./assets/lama.gif", scale=0.1)
        self.babbo.center_x = 100
        self.babbo.center_y = 250
        self.lista_babbo.append(self.babbo)

        self.genera_segmento_livello(0, 2000)
        
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.babbo, gravity_constant=GRAVITY, walls=self.wall_list
        )

    def crea_ostacolo(self, x, y, con_spuntone=False):
        wall = arcade.Sprite("./assets/terra.png", 0.17)
        wall.position = [x, y]
        self.wall_list.append(wall)
        
        if con_spuntone:
            spina = arcade.Sprite("./assets/cactus.png", 0.08) 
            spina.center_x = x
            spina.bottom = wall.top
            self.lista_spuntoni.append(spina)

    def genera_segmento_livello(self, start_x, end_x):
        x_corrente = start_x
        while x_corrente < end_x:
            if self.primo_avvio and x_corrente == 0:
                y = 200
                lunghezza_pedana = 12
                for i in range(lunghezza_pedana):
                    pos_x = x_corrente + (i * 50)
                    self.crea_ostacolo(pos_x, y, con_spuntone=False)
                self.ultima_y_piattaforma = y
                x_corrente += lunghezza_pedana * 50
                self.primo_avvio = False
                continue

            variazione = random.randint(-100, 100)
            y = max(150, min(self.ultima_y_piattaforma + variazione, 500))
            lunghezza_pedana = random.randint(1, 5)
            distanza_salto = random.randint(100, 120)

            for i in range(lunghezza_pedana):
                pos_x = x_corrente + (i * 50)
                si_spina = (lunghezza_pedana > 4 and random.random() < 0.25 and 
                            i == lunghezza_pedana // 2 and x_corrente > 500)
                self.crea_ostacolo(pos_x, y, con_spuntone=si_spina)

            if x_corrente > self.ultimo_x_grano + 1500:
                grano = arcade.Sprite("./assets/grano.webp", 0.3)
                grano.center_x = x_corrente + 50
                grano.bottom = y + 40
                self.lista_grano.append(grano)
                self.ultimo_x_grano = x_corrente

            self.ultima_y_piattaforma = y
            x_corrente += (lunghezza_pedana * 50) + distanza_salto
        self.ultimo_x_generato = end_x
            
    def on_draw(self):
        self.clear()
        
        # Se il gioco non è attivo, disegna il menu
        if not self.gioco_attivo:
            arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            arcade.draw_text("LLAMA LAMA SURVIVAL", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50,
                             arcade.color.WHITE, 40, align="center", anchor_x="center", bold=True)
            arcade.draw_text("Premi SPAZIO per iniziare", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50,
                             arcade.color.YELLOW, 20, align="center", anchor_x="center")
            return

        # Disegno del gioco vero e proprio
        coordinate_ui = self.camera.position[0] - self.width/2
        arcade.draw_texture_rect(self.background, arcade.LBWH(coordinate_ui, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.camera.use()
        self.wall_list.draw()
        self.lista_grano.draw()
        self.lista_spuntoni.draw()
        self.lista_babbo.draw()
        
        colore_timer = arcade.color.WHITE if self.timer_fame > 5 else arcade.color.RED
        arcade.draw_text(f"ENERGIA: {self.timer_fame:.1f}s", coordinate_ui + 20, self.height - 50,
                         colore_timer, 16, bold=True)
        arcade.draw_text(f"Distanza: {int(self.babbo.center_x // 10)}m", coordinate_ui + 700, self.height - 50,
                         arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        if not self.gioco_attivo:
            return

        self.babbo.change_x = PLAYER_AUTO_SPEED
        self.physics_engine.update()
        self.camera.position = (self.babbo.center_x, self.height / 2)
        self.timer_fame -= delta_time
        
        if self.timer_fame <= 0 or self.babbo.top < 0:
            self.gioco_attivo = False # Torna al menu se muori
            self.setup()

        if arcade.check_for_collision_with_list(self.babbo, self.lista_spuntoni):
            self.gioco_attivo = False
            self.setup()

        tocca_grano = arcade.check_for_collision_with_list(self.babbo, self.lista_grano)
        for g in tocca_grano:
            g.remove_from_sprite_lists()
            self.timer_fame = 20.0
            arcade.play_sound(self.suono_munch)

        if self.babbo.center_x > self.ultimo_x_generato - 1500:
            self.genera_segmento_livello(self.ultimo_x_generato, self.ultimo_x_generato + 2000)

        for lista in [self.wall_list, self.lista_grano, self.lista_spuntoni]:
            for s in lista:
                if s.right < self.camera.position[0] - 1000:
                    s.remove_from_sprite_lists()

    def on_key_press(self, tasto, modificatori):
        if not self.gioco_attivo:
            if tasto == arcade.key.SPACE:
                self.gioco_attivo = True
            return

        if tasto in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.physics_engine.can_jump():
                self.babbo.change_y = PLAYER_JUMP_SPEED

def main():
    gioco = giocoplatformer(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    gioco.setup()
    arcade.run()

if __name__ == "__main__":
    main()