import arcade


"""  gioco platformer per scuola"""



PLAYER_MOVEMENT_SPEED = 5

class giocoplatformer(arcade.Window):

    def __init__(self, larghezza, altezza, titolo):
        super().__init__(larghezza, altezza, titolo)
        
        self.percorso = 0
        
        self.babbo = None
        self.moneta = None
        self.lista_babbo = arcade.SpriteList()
        self.lista_moneta = arcade.SpriteList()
        
        # muri
        self.wall_list = None
        self.background = None
        self.suono_munch = arcade.load_sound("./assets/mangiare.mp3")

        # Movimento
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        
        self.velocita = 4

        # Gioco
        self.punteggio = 0
        
        #camera
        self.camera = arcade.camera.Camera2D()

        self.setup()

    def setup(self):
        
        self.babbo = arcade.Sprite("./assets/lama.gif", scale=0.1)
        self.babbo.center_x = 50
        self.babbo.center_y = 115
        self.lista_babbo.append(self.babbo)
        
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        
        self.background = arcade.load_texture("./assets/foresta.jpg")
                
        self.lista_moneta.clear()
        
        # creazione pavimento
        for x in range(0, 1250, 64):
            wall = arcade.Sprite("./assets/terra.png", 0.17)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)
            
        # crea gli ostacoli
        coordinate_list = [[250, 105], [500, 105], [750, 105]]
        
        for coordinate in coordinate_list:
            wall = arcade.Sprite("./assets/tubo.png", 0.17)
            wall.position = coordinate
            self.wall_list.append(wall)


        self.crea_moneta()

        
    def crea_moneta(self):
        
        coordinate_ = [[150, 105], [180, 105], [810, 105], [840,105], [870,105], [250,150]]
        
        for coordinate in coordinate_:
            self.moneta = arcade.Sprite("./assets/grano.webp",0.2)
            self.moneta.position = coordinate
            self.lista_moneta.append(self.moneta)

    def on_draw(self):
                
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, 1060, 720)
        )
        
        self.camera
        
        self.lista_moneta.draw()
        
        self.lista_babbo.draw()
        
        self.wall_list.draw()

        arcade.draw_text(
            f"Punteggio: {self.punteggio}",
            20, 
            self.height - 30,
            arcade.color.WHITE, 15
        )
        
        arcade.draw_text(
            f"gioco platformer",
            180,
            self.height - 30,
            arcade.color.BLACK, 15
        )
        
        arcade.draw_text(
            f"percorso: {int(self.percorso)}",
            350,
            self.height - 30,
            arcade.color.BLACK, 15
        )
        
        self.camera.use()

    def on_update(self, delta_time):
        
        # calcola il percorso fatto 
        self.percorso += delta_time
        
        # Calcola movimento in base ai tasti premuti
        
        change_x = 0
        change_y = 0
        
        self.camera.position = self.babbo.position
        
        """..."""
        # per non far vedere il vuoto 
        camera_x = max(self.camera.position[0], self.width / 2) 
        self.camera.position = (camera_x, self.height / 2)

        if self.up_pressed:
            change_y += self.velocita
        if self.down_pressed:
            change_y -= self.velocita
        if self.left_pressed:
            change_x -= self.velocita
        if self.right_pressed:
            change_x += self.velocita
            
        # Applica movimento
        
        self.babbo.center_x += change_x
        self.babbo.center_y += change_y
        
        # Flip orizzontale in base alla direzione
        if change_x < 0: 
            self.babbo.scale = (-0.1, 0.1)
        elif change_x > 0:
            self.babbo.scale = (0.1, 0.1)
        
            
        # Limita movimento dentro lo schermo
        if self.babbo.center_x < 0:
            self.babbo.center_x = 0
        elif self.babbo.center_x > self.width:
            self.babbo.center_x = self.width
        
        if self.babbo.center_y < 0:
            self.babbo.center_y = 0
        elif self.babbo.center_y > self.height:
            self.babbo.center_y = self.height

        # Collisioni
        collisioni = arcade.check_for_collision_with_list(self.babbo, self.lista_moneta)
                
        if len(collisioni) > 0: # Vuol dire che il personaggio si è scontrato con qualcosa
            arcade.play_sound(self.suono_munch,)
            for moneta in collisioni:
                moneta.remove_from_sprite_lists()
                self.punteggio += 1
                
        
    def on_key_press(self, tasto, modificatori):
    
            
        if tasto in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif tasto in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True
        elif tasto in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif tasto in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
    
    def on_key_release(self, tasto, modificatori):
        """Gestisce il rilascio dei tasti"""
        if tasto in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif tasto in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False
        elif tasto in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif tasto in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False



def main():
    gioco = giocoplatformer(920,620, "Babbo Natale")
    arcade.run()


if __name__ == "__main__":
    main()