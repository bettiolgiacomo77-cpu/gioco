import arcade
import random

# costanti
SCREEN_WIDTH = 920
SCREEN_HEIGHT = 620
SCREEN_TITLE = "Llama Lama - Survival Runner"

GRAVITY = 1
PLAYER_JUMP_SPEED = 19
PLAYER_AUTO_SPEED = 5 

class giocoplatformer(arcade.Window):

    def __init__(self, larghezza, altezza, titolo):
        super().__init__(larghezza, altezza, titolo)
        
        # sprite
        self.lista_lama = arcade.SpriteList()
        self.lista_grano = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.lista_spuntoni = arcade.SpriteList()
        self.lista_tubi = arcade.SpriteList() 
        
        # fisica
        self.physics_engine = None
        
        # Stato del gioco
        self.gioco_attivo = False
        self.morto_schermata = False # per la morte
        self.punti_finali = 0 # per il punteggio
        
        # suoni
        self.suono_mangiare = arcade.load_sound("./assets/mangiare.mp3")
        self.suono_salto = arcade.load_sound("./assets/salto.wav")
        self.suono_morte = arcade.load_sound("./assets/morte.mp3") # suono di morte
        
        # gestione sfondi
        self.percorso_sfondi = ["./assets/città.jpg", "./assets/cielo.jpg", "./assets/foresta.jpg"]
        self.sfondo_attuale = "./assets/città.jpg"
        self.background = arcade.load_texture(self.sfondo_attuale)
        self.ultimo_cambio_sfondo = 0 # per gestire i 500m
        
        # camera
        self.camera = arcade.camera.Camera2D()
        

    def setup(self):
        
        # Svuota le liste
        self.wall_list.clear()
        self.lista_grano.clear()
        self.lista_spuntoni.clear()
        self.lista_tubi.clear() 
        self.lista_lama.clear()

        # variabili percorso
        self.ultimo_x_generato = 0
        self.ultimo_x_grano = 0
        self.ultima_y_piattaforma = 150 
        self.primo_avvio = True 
        self.ultimo_cambio_sfondo = 0
        self.morto_schermata = False
        
        # Reset camera (BUG FIX: la camera deve tornare a 0 al restart)
        self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        
        # timer
        self.timer = 15.0

        # lama
        self.lama = arcade.Sprite("./assets/lama.gif", scale=0.1)
        self.lama.center_x = 100
        self.lama.center_y = 250
        self.lista_lama.append(self.lama)
        
        # genera percorso
        self.genera_segmento_livello(0, 2000)
        
        # fisica
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.lama,
            gravity_constant=GRAVITY,
            walls=self.wall_list
        )
        
    # genera ostacolo
    def crea_ostacolo(self, x, y, con_spuntone=False, con_tubo=False):
        
        wall = arcade.Sprite("./assets/terra.png", 0.17)
        wall.position = [x, y]
        self.wall_list.append(wall)
        
        if con_spuntone:
            spina = arcade.Sprite("./assets/cactus.png", 0.08) 
            spina.center_x = x
            spina.bottom = wall.top
            self.lista_spuntoni.append(spina)

        if con_tubo:
            tubo = arcade.Sprite("./assets/tubo.png", 0.5)
            tubo.center_x = x
            tubo.bottom = wall.top
            self.lista_tubi.append(tubo)
            self.wall_list.append(tubo)
            
    # genera percorso
    def genera_segmento_livello(self, start_x, end_x):
        
        x_corrente = start_x
        while x_corrente < end_x:
            if self.primo_avvio and x_corrente == 0:
                y = 200
                lunghezza_pedana = 12
                for i in range(lunghezza_pedana):
                    pos_x = x_corrente + (i * 50)
                    self.crea_ostacolo(pos_x, y, con_spuntone=False, con_tubo=False)
                self.ultima_y_piattaforma = y
                x_corrente += lunghezza_pedana * 50
                self.primo_avvio = False
                continue

            # LOGICA PER EVITARE CHE LE PIATTAFORME SIANO UNA SOPRA L'ALTRA
            y = self.ultima_y_piattaforma
            # Tentativi limitati per evitare loop infiniti
            for _ in range(10):
                variazione = random.randint(-150, 150) # Limitato a 150 per salti fattibili
                nuova_y = max(150, min(self.ultima_y_piattaforma + variazione, 500))
                if abs(nuova_y - self.ultima_y_piattaforma) >= 80: # Ridotto leggermente per varietà
                    y = nuova_y
                    break

            # Pedane da 1 a 6 blocchi
            lunghezza_pedana = random.randint(1, 6)
            
            # Fix Bug: Se la piattaforma è più alta, accorciamo il salto per renderlo possibile
            if y > self.ultima_y_piattaforma:
                distanza_salto = random.randint(100, 140)
            else:
                distanza_salto = random.randint(130, 170)

            # --- FIX SOVRAPPOSIZIONE ---
            # Avanziamo X prima di creare i blocchi per non sovrapporre le y diverse
            x_corrente += distanza_salto

            for i in range(lunghezza_pedana):
                pos_x = x_corrente + (i * 50)
                
                si_spina = False
                si_tubo = False
                
                # Regole Spawn Ostacoli (Logica Lunghezze):
                if i == lunghezza_pedana // 2 and x_corrente > 600:
                    prob = random.random()
                    if prob < 0.50:
                        # Tubi solo se la pedana è lunga 6
                        if lunghezza_pedana == 6:
                            si_tubo = True
                        # Cactus solo se la pedana è lunga 4 o 5
                        elif lunghezza_pedana in [4, 5]:
                            si_spina = True

                self.crea_ostacolo(pos_x, y, con_spuntone=si_spina, con_tubo=si_tubo)
                
                # Regole Spawn Grano:
                # Grano solo se la pedana è lunga 1, 2 o 3
                if lunghezza_pedana in [1, 2, 3] and i == lunghezza_pedana // 2:
                    if pos_x > self.ultimo_x_grano + 500:
                        grano = arcade.Sprite("./assets/grano.webp", 0.3)
                        grano.center_x = pos_x
                        grano.bottom = y + 40
                        self.lista_grano.append(grano)
                        self.ultimo_x_grano = pos_x

            self.ultima_y_piattaforma = y
            x_corrente += (lunghezza_pedana * 50) 
        
        self.ultimo_x_generato = x_corrente
            
    def on_draw(self):
        
        self.clear()
        
        # disegna la schermata di morte
        if self.morto_schermata:
            # Forza la camera a stare ferma per i menu
            self.camera.use() 
            arcade.draw_texture_rect(self.background,
                                     arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50,
                             arcade.color.RED, 50, align="center", anchor_x="center", bold=True)
            arcade.draw_text(f"PUNTEGGIO: {self.punti_finali}m", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20,
                             arcade.color.WHITE, 30, align="center", anchor_x="center")
            arcade.draw_text("Premi SPAZIO per ricominciare", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 80,
                             arcade.color.YELLOW, 20, align="center", anchor_x="center")
            return

        # disegna il menu
        if not self.gioco_attivo:
            self.camera.use()
            arcade.draw_texture_rect(self.background,
                                     arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            arcade.draw_text("LLAMA LAMA SURVIVAL", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50,
                             arcade.color.WHITE, 40, align="center", anchor_x="center", bold=True)
            
            arcade.draw_text("Premi SPAZIO per iniziare", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50,
                             arcade.color.YELLOW, 20, align="center", anchor_x="center")
            return

        # Disegna il gioco
        # Usiamo la camera per ottenere la coordinata corretta del background
        coordinate = self.camera.position[0] - SCREEN_WIDTH/2
        
        # disegna lo sfondo
        arcade.draw_texture_rect(self.background,
                                 arcade.LBWH(coordinate, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.camera.use()
        
        self.wall_list.draw()
        self.lista_grano.draw()
        self.lista_spuntoni.draw()
        self.lista_tubi.draw() 
        self.lista_lama.draw()
        
        # cambia il colore del timer
        colore_timer = arcade.color.WHITE if self.timer > 5 else arcade.color.RED
        
        # disegna le scritte
        arcade.draw_text(f"PERCORSO: {int(self.lama.center_x // 10)}m", coordinate + 700, SCREEN_HEIGHT - 50,
                         arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        
        if not self.gioco_attivo:
            return

        # il lama va avanti da solo
        self.lama.change_x = PLAYER_AUTO_SPEED
        
        # LOGICA CAMBIO SFONDO OGNI 250m (nel tuo codice avevi 250 nel calcolo e 500 nel commento)
        distanza_metri = int(self.lama.center_x // 10)
        if distanza_metri >= self.ultimo_cambio_sfondo + 250:
            # Sceglie uno sfondo diverso da quello attuale tra i 3 disponibili
            sfondi_disponibili = [s for s in self.percorso_sfondi if s != self.sfondo_attuale]
            self.sfondo_attuale = random.choice(sfondi_disponibili)
            self.background = arcade.load_texture(self.sfondo_attuale)
            self.ultimo_cambio_sfondo = distanza_metri

        # CONTROLLO COLLISIONE TUBO (MORTALE DI LATO)
        for tubo in self.lista_tubi:
            if (self.lama.right + PLAYER_AUTO_SPEED > tubo.left and 
                self.lama.left < tubo.left and
                self.lama.bottom < tubo.top - 5): # Tolleranza per salti al pelo
                self.morte_gioco()
                return

        # fisica
        self.physics_engine.update()
        
        # camera
        self.camera.position = (self.lama.center_x + 200, SCREEN_HEIGHT / 2)
        
        # Rimuove gli oggetti lontani (ottimizzazione)
        for muro in self.wall_list:
            if muro.right < self.lama.left - 500:
                muro.remove_from_sprite_lists()

        # se non mangi il grano muori
        if self.lama.top < -100:
            self.morte_gioco()
        
        # se tocca i cactus muore
        if arcade.check_for_collision_with_list(self.lama, self.lista_spuntoni):
            self.morte_gioco()
            
        # collisine grano
        collisione = arcade.check_for_collision_with_list(self.lama, self.lista_grano)
        for i in collisione:
            i.remove_from_sprite_lists()
            arcade.play_sound(self.suono_mangiare)
            
        # genera percorso
        if self.lama.center_x > self.ultimo_x_generato - 2000:
            self.genera_segmento_livello(self.ultimo_x_generato, self.ultimo_x_generato + 2000)

    # funzione interna per gestire la morte
    def morte_gioco(self):
        self.punti_finali = int(self.lama.center_x // 10)
        self.gioco_attivo = False
        self.morto_schermata = True
        # Riporta la camera all'inizio per vedere bene il Game Over
        self.camera.position = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        arcade.play_sound(self.suono_morte)

    # tasti
    def on_key_press(self, tasto, modificatori):
        if not self.gioco_attivo:
            if tasto == arcade.key.SPACE:
                if self.morto_schermata:
                    self.setup() # resetta se era morto
                self.gioco_attivo = True
            return

        if tasto in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.physics_engine.can_jump():
                self.lama.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.suono_salto)

def main():
    gioco = giocoplatformer(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    gioco.setup()
    arcade.run()

if __name__ == "__main__":
    main()