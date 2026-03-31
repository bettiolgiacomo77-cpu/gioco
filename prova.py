import arcade
import random

SCREEN_WIDTH = 920
SCREEN_HEIGHT = 620
SCREEN_TITLE = "Llama Lama"

GRAVITY = 1
PLAYER_JUMP_SPEED = 20
PLAYER_MOVEMENT_SPEED = 5

SUPER_SPEED = 15  # Velocità durante la super
SUPER_DURATION = 2.0  # Durata della super in secondi

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
        
        # variabili super
        self.grano_raccolto = 0
        self.super_attiva = False
        self.timer_super = 0

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
            self.babbo,
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
            
# --- FUNZIONI DI SUPPORTO (Helper) ---
    def crea_grano(self, x, y):
        moneta = arcade.Sprite("./assets/grano.webp", 0.2)
        moneta.position = [x, y]
        self.lista_moneta.append(moneta)

    def crea_ostacolo(self, x, y):
        wall = arcade.Sprite("./assets/tubo.png", 0.17)
        wall.position = [x, y]
        self.wall_list.append(wall)

    # --- I 10 MODULI DI PERCORSO ---
    def genera_pianura(self, start_x):
        for x in range(start_x + 200, start_x + 900, 200):
            self.crea_grano(x, 150)

    def genera_ostacoli_fitti(self, start_x):
        for x in range(start_x + 200, start_x + 900, 45):
            self.crea_ostacolo(x, 105)

    def genera_salti(self, start_x):
        for x in range(start_x + 300, start_x + 900, 300):
            self.crea_ostacolo(x, 150)
            self.crea_grano(x, 280)

    def genera_tunnel(self, start_x):
        for x in range(start_x + 100, start_x + 900, 200):
            self.crea_ostacolo(x, 100)
            self.crea_grano(x + 100, 110)

    def genera_super_grano(self, start_x):
        for x in range(start_x + 100, start_x + 900, 100):
            self.crea_grano(x, 150)
            self.crea_grano(x, 220)

    def genera_scalinata(self, start_x):
        for i, x in enumerate(range(start_x + 200, start_x + 500, 90)):
            self.crea_ostacolo(x, 100 + (i*50))
        for i, x in enumerate(range(start_x + 155, start_x + 500, 90)):
            self.crea_ostacolo(x, 100 + (i*50))
        for x in range(start_x + 515, start_x + 1000, 45):
            self.crea_ostacolo(x, 250)
        for x in range(start_x + 1150, start_x + 1250, 45):
            self.crea_ostacolo(x, 250)
        for x in range(start_x + 515, start_x + 950, 50):
            self.crea_grano(x, 315)
        for x in range(start_x + 1200, start_x + 1250, 50):
            self.crea_grano(x, 315)
        
        
        
            
    def genera_zig_zag(self, start_x):
        for x in range(start_x + 100, start_x + 900, 150):
            altezza = 120 if x % 300 == 0 else 250
            self.crea_grano(x, altezza)

    def genera_pericolo_alto(self, start_x):
        for x in range(start_x + 200, start_x + 900, 400):
            self.crea_ostacolo(x, 180) # Tubi sospesi o molto alti

    def genera_labirinto_base(self, start_x):
        self.crea_ostacolo(start_x + 200, 105)
        self.crea_ostacolo(start_x + 400, 105)
        self.crea_grano(start_x + 300, 250)

    def genera_vuoto_apparente(self, start_x):
        # Solo grano che fluttua, niente ostacoli
        for x in range(start_x + 100, start_x + 900, 50):
            self.crea_grano(x, 180)

    # --- FUNZIONE PRINCIPALE DI GENERAZIONE ---
    def genera_segmento_livello(self, start_x, end_x):
        # Genera Pavimento
        for x in range(start_x, end_x, 64):
            wall = arcade.Sprite("./assets/terra.png", 0.17)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        # Scelta casuale tra i 10 tipi
        tipo = random.randint(1, 10)

        if tipo == 1: self.genera_pianura(start_x)    #ci sono 3 di grano con spazio tra di loro               G             1
        elif tipo == 2: self.genera_ostacoli_fitti(start_x)     #ci sono 3 ostacoli con spazio tra di loro       O           1
        elif tipo == 3: self.genera_salti(start_x) # ci sono 2 tubi con sopra 2 di grano                       G O           2
        elif tipo == 4: self.genera_tunnel(start_x) # ci sono 4 tubi e 4 di grano tra i tubi                   G O           2
        elif tipo == 5: self.genera_super_grano(start_x) # ci sono 2 file di grano una sopra l'altra           G             1
        elif tipo == 6: self.genera_scalinata(start_x)# scala di tubi                                            O           1
        elif tipo == 7: self.genera_zig_zag(start_x)# riga di grano che per prenderla devi saltare             G             1
        elif tipo == 8: self.genera_pericolo_alto(start_x)# due tubi sopraelevarti                               O           1
        elif tipo == 9: self.genera_labirinto_base(start_x)# due tubi e un grano                               G O           2
        elif tipo == 10: self.genera_vuoto_apparente(start_x)# riga di grano                                   G             1

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
        
        self.camera.use()
        
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
        
        # Indicatore Super in alto a sinistra
        colore_super = arcade.color.GREEN if self.grano_raccolto >= 10 else arcade.color.GRAY
        testo_super = "SUPER PRONTA! (Premi E)" if self.grano_raccolto >= 10 else f"Carica Super: {self.grano_raccolto}/10"
        
        # Se la super è già attiva, mostra il timer
        if self.super_attiva:
            testo_super = f"SUPER ATTIVA: {self.timer_super:.1f}s"
            colore_super = arcade.color.GOLD

        arcade.draw_text(
            testo_super,
            coordinate_testo + 20,
            self.height - 60, # Un po' più in basso del punteggio
            colore_super, 
            14, 
            bold=True
        )

    def on_update(self, delta_time):
        
        if self.super_attiva:
            self.babbo.change_x = SUPER_SPEED
            self.timer_super -= delta_time
            if self.timer_super <= 0:
                self.super_attiva = False
        else:
            self.babbo.change_x = PLAYER_MOVEMENT_SPEED
        
        self.physics_engine.update()
        
        self.camera.position = self.babbo.position
        
        """..."""
        # per non far vedere il vuoto 
        camera_x = max(self.camera.position[0], self.width / 2) 
        self.camera.position = (camera_x, self.height / 2)
            
        #genera nuovi pezzi di mappa    
        if self.babbo.center_x > self.ultimo_x_generato - 2000:
            self.genera_segmento_livello(self.ultimo_x_generato, self.ultimo_x_generato + 2000)
            
        # rimuove gli sprite gia passati
        for sprite in self.wall_list:
            if sprite.right < self.babbo.center_x - 2000:
                sprite.remove_from_sprite_lists()
        
        # Collisioni
        collisioni = arcade.check_for_collision_with_list(self.babbo, self.lista_moneta)
                
        if len(collisioni) > 0: # Vuol dire che il personaggio si è scontrato con qualcosa
            arcade.play_sound(self.suono_munch)
            for moneta in collisioni:
                moneta.remove_from_sprite_lists()
                self.punteggio += 1
                if self.grano_raccolto < 10:
                        self.grano_raccolto += 1    
        
                
    def on_key_press(self, tasto, modificatori):
            
        if tasto in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            # Salta solo se il motore fisico dice che siamo a terra
            if self.physics_engine.can_jump():
                self.babbo.change_y = PLAYER_JUMP_SPEED
            
        if tasto == arcade.key.E:
            if self.grano_raccolto >= 10 and not self.super_attiva:
                self.super_attiva = True
                self.timer_super = SUPER_DURATION
                self.grano_raccolto = 0  # Consuma il grano
                
def main():
    gioco = giocoplatformer(SCREEN_WIDTH,SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()