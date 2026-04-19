import arcade
import random

#  costanti schermo
SCREEN_WIDTH = 920
SCREEN_HEIGHT = 620
SCREEN_TITLE = "Llama Lama - Survival Runner"

# costanti gioco
GRAVITY = 1
PLAYER_JUMP_SPEED = 18
JETPACK_SPEED = 6

# parametri velocità progressiva
VELOCITA_MIN = 4.0
VELOCITA_MAX = 7.0
DISTANZA_INCREMENTO = 350

class GiocoPlatformer(arcade.Window):

    def __init__(self, larghezza, altezza, titolo):
        super().__init__(larghezza, altezza, titolo)
        
        # Liste sprite
        self.lista_lama = arcade.SpriteList()
        self.lista_grano = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.lista_spuntoni = arcade.SpriteList()
        self.lista_tubi = arcade.SpriteList()
        self.lista_jetpack = arcade.SpriteList() 
        
        # Fisica e stato del gioco
        self.physics_engine = None
        self.gioco_attivo = False
        self.morto_schermata = False 
        self.punti_finali = 0 
        
        # Logica jepak
        self.jetpack_attivo = False
        self.jetpack_timer = 0.0
        
        # logica salti e velocità
        self.salti_effettuati = 0 
        self.velocita_attuale = VELOCITA_MIN
        
        # suoni    
        self.suono_mangiare = arcade.load_sound("./assets/mangiare.mp3")
        self.suono_salto = arcade.load_sound("./assets/salto.wav")
        self.suono_morte = arcade.load_sound("./assets/morte.mp3") 
        
        # sfondi
        self.percorso_sfondi = [
            "./assets/città.jpg", "./assets/cielo.jpg", "./assets/foresta.jpg"
            ]
        self.sfondo_attuale = "./assets/città.jpg"
        self.background = arcade.load_texture(self.sfondo_attuale)
        
        # skin
        self.skin_disponibili = [
            arcade.load_texture("./assets/lama.png"),
            arcade.load_texture("./assets/lama2.png"),
            arcade.load_texture("./assets/lama3.png"),
            arcade.load_texture("./assets/lama4.png"),
            arcade.load_texture("./assets/lama5.png")
        ]
        self.indice_skin_attuale = 0
        
        # camera
        self.camera = arcade.camera.Camera2D()

    def setup(self):
        
        # reset
        self.wall_list.clear()
        self.lista_grano.clear()
        self.lista_spuntoni.clear()
        self.lista_tubi.clear()
        self.lista_lama.clear()
        self.lista_jetpack.clear()

        # variabili
        #(percorso)
        self.ultimo_x_generato = 0
        self.ultimo_x_grano = 0
        self.ultimo_x_jetpack = 0
        self.ultima_y_piattaforma = 150
        self.primo_avvio = True
        
        #(sfondo)
        self.ultimo_cambio_sfondo = 0
        self.morto_schermata = False
        
        #(jetpak)
        self.jetpack_attivo = False
        self.jetpack_timer = 0.0
        
        #(salti e velocità)
        self.salti_effettuati = 0
        self.velocita_attuale = VELOCITA_MIN
        
        # camera
        self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        
        # lama
        self.lama = arcade.Sprite()
        self.lama.texture = self.skin_disponibili[self.indice_skin_attuale]
        self.lama.scale = 0.15
        self.lama.center_x = 100
        self.lama.center_y = 250
        self.lista_lama.append(self.lama)
        
        # Generazione iniziale del percorso
        self.genera_segmento_livello(0, 1500)
        
        # fisica
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.lama,
            gravity_constant=GRAVITY,
            walls=self.wall_list
        )
        
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
            
    def genera_segmento_livello(self, start_x, end_x):
        
        # logica creazione inizio gioco
        x_corrente = start_x
        while x_corrente < end_x:
            if self.primo_avvio and x_corrente == 0:
                y = 200
                lunghezza_pedana = 12
                for i in range(lunghezza_pedana):
                    self.crea_ostacolo(x_corrente + (i * 50), y)
                self.ultima_y_piattaforma = y
                x_corrente += lunghezza_pedana * 50
                self.primo_avvio = False
                continue
            
            # logica creazione terreno
            if self.jetpack_attivo:
                y = self.ultima_y_piattaforma 
                lunghezza_pedana = 5
                distanza_salto = 0 
            else:
                y = self.ultima_y_piattaforma
                for _ in range(10):
                    variazione = random.randint(-150, 150)
                    nuova_y = max(150, min(self.ultima_y_piattaforma + variazione, 500))
                    if abs(nuova_y - self.ultima_y_piattaforma) >= 80:
                        y = nuova_y
                        break
                # altezza e  lenghezza random
                lunghezza_pedana = random.randint(1, 6)
                distanza_salto = random.randint(130, 170)

            x_corrente += distanza_salto

            tipo_spawn = "nulla"
            indice_centrale = lunghezza_pedana // 2
            
            if not self.jetpack_attivo and x_corrente > 600:
                prob = random.random()
                
                # 1 spown Jetpack ?
                if x_corrente > self.ultimo_x_jetpack + 5500:
                    tipo_spawn = "jetpack"
                
                # 2 spown ostacoli? (Logica tubi su 6 blocchi e cactus su 4 o 5)
                elif prob < 0.40:
                    if lunghezza_pedana == 6:
                        tipo_spawn = "tubo"
                    elif lunghezza_pedana in [4, 5]:
                        tipo_spawn = "spina"
                
                # 3 spown grano?
                elif prob < 0.75:
                    if x_corrente > self.ultimo_x_grano + 500:
                        tipo_spawn = "grano"

            # Creazione della pedana
            for i in range(lunghezza_pedana):
                pos_x = x_corrente + (i * 50)
                
                si_tubo = False
                si_spina = False
                
                # applica l'oggetto sulla pedana
                if i == indice_centrale:
                    if tipo_spawn == "tubo":
                        si_tubo = True
                    elif tipo_spawn == "spina":
                        si_spina = True
                    elif tipo_spawn == "jetpack":
                        jet = arcade.Sprite("./assets/jetpak.png", 0.12)
                        jet.center_x = pos_x
                        jet.bottom = y + 50
                        self.lista_jetpack.append(jet)
                        self.ultimo_x_jetpack = pos_x
                    elif tipo_spawn == "grano":
                        grano = arcade.Sprite("./assets/grano.webp", 0.3)
                        grano.center_x = pos_x
                        grano.bottom = y + 40
                        self.lista_grano.append(grano)
                        self.ultimo_x_grano = pos_x

                self.crea_ostacolo(pos_x, y, con_spuntone=si_spina, con_tubo=si_tubo)

            self.ultima_y_piattaforma = y
            x_corrente += (lunghezza_pedana * 50)
        
        self.ultimo_x_generato = x_corrente
            
    def on_draw(self):
        
        self.clear()
        
        # scermata di morte
        if self.morto_schermata:
            self.camera.use()
            arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50, arcade.color.RED, 50, align="center", anchor_x="center", bold=True)
            arcade.draw_text(f"PUNTEGGIO: {self.punti_finali}m", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20, arcade.color.WHITE, 30, align="center", anchor_x="center")
            arcade.draw_text("Premi SPAZIO per ricominciare", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 80, arcade.color.YELLOW, 20, align="center", anchor_x="center")
            return
        
        # schermata di start
        if not self.gioco_attivo:
            self.camera.use()
            arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            arcade.draw_text("LLAMA LAMA SURVIVAL", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50, arcade.color.WHITE, 40, align="center", anchor_x="center", bold=True)
            arcade.draw_text("Premi SPAZIO per iniziare", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, arcade.color.YELLOW, 20, align="center", anchor_x="center")
            return

        # lo sfondo segue la telecamera
        coordinate_x = self.camera.position[0] - SCREEN_WIDTH/2
        arcade.draw_texture_rect(self.background, arcade.LBWH(coordinate_x - 5, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # disegno oggetti
        self.camera.use()
        self.wall_list.draw()
        self.lista_grano.draw()
        self.lista_spuntoni.draw()
        self.lista_tubi.draw()
        self.lista_jetpack.draw()
        self.lista_lama.draw()
        
        # disegno scritte
        metri = int(self.lama.center_x // 10)
        arcade.draw_text(f"PERCORSO: {metri}m", coordinate_x + 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 16, bold=True)
        arcade.draw_text(f"VELOCITÀ: {self.velocita_attuale:.1f}", coordinate_x + 20, SCREEN_HEIGHT - 70, arcade.color.CYAN, 14)
        
        # disegno scritte jetpak
        if self.jetpack_attivo:
            arcade.draw_text(f"JETPACK: {self.jetpack_timer:.1f}s", coordinate_x + 750, SCREEN_HEIGHT - 40, arcade.color.RED, 18, bold=True)

    def on_update(self, delta_time):
        
        if not self.gioco_attivo:
            return
        
        # cambio velocità
        metri_percorsi = self.lama.center_x / 10
        self.velocita_attuale = VELOCITA_MIN + (metri_percorsi / DISTANZA_INCREMENTO)
        
        if self.velocita_attuale > VELOCITA_MAX:
            self.velocita_attuale = VELOCITA_MAX
            
        self.lama.change_x = self.velocita_attuale
        
        # jetpak
        if self.jetpack_attivo:
            self.jetpack_timer -= delta_time
            if self.jetpack_timer <= 0:
                self.jetpack_attivo = False
                self.lama.change_y = 0
            self.lama.center_y += self.lama.change_y
            self.lama.center_x += self.lama.change_x
            if self.lama.top > SCREEN_HEIGHT: self.lama.top = SCREEN_HEIGHT
        else:
            self.physics_engine.update()
            if self.physics_engine.can_jump():
                self.salti_effettuati = 0

        # logica cambio sfondo
        distanza_metri = int(metri_percorsi)
        if distanza_metri >= self.ultimo_cambio_sfondo + 250:
            sfondi_disponibili = [s for s in self.percorso_sfondi if s != self.sfondo_attuale]
            self.sfondo_attuale = random.choice(sfondi_disponibili)
            self.background = arcade.load_texture(self.sfondo_attuale)
            self.ultimo_cambio_sfondo = distanza_metri

        # collisioni jetpak
        get_jetpack = arcade.check_for_collision_with_list(self.lama, self.lista_jetpack)
        if get_jetpack:
            for j in get_jetpack: j.remove_from_sprite_lists()
            self.jetpack_attivo = True
            self.jetpack_timer = 5.0

        if not self.jetpack_attivo:
            # Controllo collisioni morte
            for tubo in self.lista_tubi:
                if (self.lama.right + self.velocita_attuale > tubo.left and 
                    self.lama.left < tubo.left and self.lama.bottom < tubo.top - 5):
                    self.morte_gioco()
                    return

            if self.lama.top < -100 or arcade.check_for_collision_with_list(self.lama, self.lista_spuntoni):
                self.morte_gioco()
                return
            
        # collisioni grano
        collisione_grano = arcade.check_for_collision_with_list(self.lama, self.lista_grano)
        for g in collisione_grano:
            g.remove_from_sprite_lists()
            try: arcade.play_sound(self.suono_mangiare)
            except: pass
            self.indice_skin_attuale = (self.indice_skin_attuale + 1) % len(self.skin_disponibili)
            self.lama.texture = self.skin_disponibili[self.indice_skin_attuale]
            
        # Gestione camera
        self.camera.position = (self.lama.center_x + 200, SCREEN_HEIGHT / 2)
        
        # rigenerazione livello
        if self.lama.center_x > self.ultimo_x_generato - 1000:
            self.genera_segmento_livello(self.ultimo_x_generato, self.ultimo_x_generato + 1000)

    def morte_gioco(self):
        
        self.punti_finali = int(self.lama.center_x // 10)
        self.gioco_attivo = False
        self.morto_schermata = True
        self.camera.position = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        arcade.play_sound(self.suono_morte)
        

    def on_key_press(self, tasto, modificatori):
        
        if not self.gioco_attivo:
            if tasto == arcade.key.SPACE:
                if self.morto_schermata: self.setup()
                self.gioco_attivo = True
            return

        if tasto in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.jetpack_attivo:
                self.lama.change_y = JETPACK_SPEED
            else:
                if self.physics_engine.can_jump():
                    self.lama.change_y = PLAYER_JUMP_SPEED
                    self.salti_effettuati = 1
                    arcade.play_sound(self.suono_salto) # suono
                    
                elif self.salti_effettuati == 1:
                    self.lama.change_y = PLAYER_JUMP_SPEED
                    self.salti_effettuati = 2
                    arcade.play_sound(self.suono_salto) # suono
                    

    def on_key_release(self, tasto, modificatori):
        
        if self.jetpack_attivo and tasto in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            self.lama.change_y = -JETPACK_SPEED / 2

def main():
    gioco = GiocoPlatformer(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    gioco.setup()
    arcade.run()

if __name__ == "__main__":
    main()