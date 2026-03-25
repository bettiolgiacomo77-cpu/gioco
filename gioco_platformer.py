import arcade
import random

GRAVITY = 1
PLAYER_JUMP_SPEED = 20

"""  gioco platformer per scuola"""

class giocoplatformer(arcade.Window):

    def __init__(self, larghezza, altezza, titolo):
        super().__init__(larghezza, altezza, titolo)
        
        
        #gravità
        self.physics_engine = None
        # oggetti
        self.babbo = None
        self.moneta = None
        self.lista_babbo = arcade.SpriteList()
        self.lista_moneta = arcade.SpriteList()
        
        self.background = None
        self.suono_munch = arcade.load_sound("./assets/mangiare.mp3")

        # muri
        self.wall_list = None
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        
        # Movimento
        self.left_pressed = False
        self.right_pressed = False
        
        self.velocita = 4

        # Gioco
        self.punteggio = 0
        
        #camera
        self.camera = arcade.camera.Camera2D()
        
        """..."""
        # Variabile per tracciare fin dove abbiamo generato il terreno
        self.ultimo_x_generato = 0

        self.setup()

    def setup(self):
        
        self.babbo = arcade.Sprite("./assets/lama.gif", scale=0.1)
        self.babbo.center_x = 50
        self.babbo.center_y = 115
        self.lista_babbo.append(self.babbo)
        
        self.background = arcade.load_texture("./assets/foresta.jpg")
        
        """..."""
        # Generazione iniziale del terreno (primi 2000 pixel)
        self.genera_segmento_livello(0, 2000)
        
        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.lista_babbo,
            gravity_constant=GRAVITY,
            walls= self.wall_list
        )
        
    """..."""    
    def genera_segmento_livello(self, start_x, end_x):
        """Genera terreno e oggetti in un intervallo X specifico"""
        # Genera Pavimento
        for x in range(start_x, end_x, 64):
            wall = arcade.Sprite("./assets/terra.png", 0.17)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)    
            
        # generazione ostacoli casuali (tubi)    
        for x in range(start_x + 300, end_x, 400):
            if random.random() > 0.02: # 200% di probabilità di avere un tubo
                wall = arcade.Sprite("./assets/tubo.png", 0.17)
                wall.position = [x, 105]
                self.wall_list.append(wall)

        # Genera grano in modo casuale
        for x in range(start_x + 100, end_x, 150):
            moneta = arcade.Sprite("./assets/grano.webp", 0.2)
            moneta.position = [x, random.randint(100, 200)]
            self.lista_moneta.append(moneta)
            
        self.ultimo_x_generato = end_x

    def on_draw(self):
                
        self.clear()

        # disegna lo sfondo
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(self.camera.position[0] - self.width/2, 0, 1060, 720)
        )
        
        self.lista_moneta.draw()
        
        self.lista_babbo.draw()
        
        self.wall_list.draw()
        
        # fa in modo che le scritte si muovano con la camera
        coordinate_testo = self.camera.position[0] - self.width/2
        arcade.draw_text(
            f"Punteggio: {self.punteggio}",
            coordinate_testo + 20,
            self.height - 30,
            arcade.color.WHITE, 15
            )
        
        arcade.draw_text(
            f"Llama lama",
            coordinate_testo + 180,
            self.height - 30,
            arcade.color.BLACK, 15
            )
        
        arcade.draw_text(
            f"Distanza: {int(self.babbo.center_x)}m",
            coordinate_testo + 450,
            self.height - 30,
            arcade.color.BLACK, 15
            )
        
        self.camera.use()
        
        # serve per mette il testo che si muove con la camera
        pos_x = self.camera.position[0] - self.width/2
        arcade.draw_text(f"Punteggio: {self.punteggio}", pos_x + 20, self.height - 40, arcade.color.WHITE, 16, bold=True)
        arcade.draw_text(f"Distanza: {int(self.babbo.center_x)}m", pos_x + 250, self.height - 40, arcade.color.BLACK, 16)

    def on_update(self, delta_time):
        
        # Calcola movimento in base ai tasti premuti
        
        change_x = 0
        change_y = 0
        
        self.camera.position = self.babbo.position
        
        """..."""
        # per non far vedere il vuoto 
        camera_x = max(self.camera.position[0], self.width / 2) 
        self.camera.position = (camera_x, self.height / 2)

        #gestisce il movimento
        self.babbo.change_x = 0
        if self.left_pressed:
            self.babbo.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed:
            self.babbo.change_x = PLAYER_MOVEMENT_SPEED
            
        #genera nuovi pezzi di mappa    
        if self.babbo.center_x > self.ultimo_x_generato - 1000:
            self.genera_segmento_livello(self.ultimo_x_generato, self.ultimo_x_generato + 1000)
            
        # rimuove gli sprite gia passati
        for sprite in self.wall_list:
            if sprite.right < self.babbo.center_x - 1000:
                sprite.remove_from_sprite_lists()
            
        # Applica movimento
        
        self.babbo.center_x += change_x
        self.babbo.center_y += change_y
        
        # Flip orizzontale in base alla direzione
        """if change_x < 0: 
            self.babbo.scale = (-0.1, 0.1)
        elif change_x > 0:
            self.babbo.scale = (0.1, 0.1)"""

        if self.babbo.change_x < 0: 
            self.babbo.scale = -0.1 # Nota: arcade 3.0 gestisce il flip meglio con scale_x
        elif self.babbo.change_x > 0:
            self.babbo.scale = 0.1

        # Collisioni
        collisioni = arcade.check_for_collision_with_list(self.babbo, self.lista_moneta)
                
        if len(collisioni) > 0: # Vuol dire che il personaggio si è scontrato con qualcosa
            arcade.play_sound(self.suono_munch)
            for moneta in collisioni:
                moneta.remove_from_sprite_lists()
                self.punteggio += 1
                
        self.physics_engine.update()
                
    def on_key_press(self, tasto, modificatori):
            
        if tasto in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            # Salta solo se il motore fisico dice che siamo a terra
            if self.physics_engine.can_jump():
                self.babbo.change_y = PLAYER_JUMP_SPEED
        if tasto in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif tasto in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
    def on_key_release(self, tasto, modificatori):
        """Gestisce il rilascio dei tasti"""
        if tasto in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif tasto in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False



def main():
    gioco = giocoplatformer(920,620, "Llama lama")
    arcade.run()


if __name__ == "__main__":
    main()