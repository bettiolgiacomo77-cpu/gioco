import arcade
import random
import time


"""  gioco platformer per scuola"""



class SuperMaincraft(arcade.Window):

    def __init__(self, larghezza, altezza, titolo):
        super().__init__(larghezza, altezza, titolo)
        
        self.physics_engine = None
        self.babbo = None
        self.lista_babbo = arcade.SpriteList()
        self.lista_moneta = arcade.SpriteList()
        self.lista_wall = None

        self.background = None
        self.suono_munch = arcade.load_sound("./assets/audio.mp3")

        # Movimento
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.velocita = 4

        # Gioco
        self.soundOnOff = True
        self.moneta_spawn_count = 5
        self.punteggio = 0

        self.setup()

    def setup(self):

        self.background = arcade.load_texture("./assets/sfondo-2.jpg")
        self.babbo = arcade.Sprite("./assets/mario.png", scale=0.1)
        self.babbo.center_x = 275
        self.babbo.center_y = 100
        self.lista_babbo.append(self.babbo)
        self.lista_moneta.clear()

        
        for i in range(self.moneta_spawn_count):
            self.crea_moneta()

    def crea_moneta(self):

        self.moneta = arcade.Sprite("./assets/moneta.gif",0.06)
        self.moneta.center_x = random.randint(350, 500,)
        self.moneta.center_y = 100
        self.lista_moneta.append(self.moneta)

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, 600, 600)
        )

        self.lista_moneta.draw()
        self.lista_babbo.draw()

        arcade.draw_text(
            f"Punteggio: {self.punteggio}",
            20, self.height - 30,
            arcade.color.WHITE, 15
        )
        
        arcade.draw_text(
            f"SUPER MAINCRAFT",50,
            self.width -360,
            self.height - 30,
            arcade.color.BLACK, 15
        )

    def on_update(self, delta_time):
        change_x = 0
        change_y = 0

        if self.up_pressed:
            change_y += self.velocita
        if self.down_pressed:
            change_y -= self.velocita
        if self.left_pressed:
            change_x -= self.velocita
        if self.right_pressed:
            change_x += self.velocita

        self.babbo.center_x += change_x
        self.babbo.center_y += change_y

        self.babbo.center_x = max(0, min(self.width, self.babbo.center_x))
        self.babbo.center_y = max(0, min(self.height, self.babbo.center_y))
        
        if change_x < 0: 
            self.babbo.scale = (-0.1, 0.1)
        elif change_x > 0:
            self.babbo.scale = (0.1, 0.1)

        # Collisioni
        collisioni = arcade.check_for_collision_with_list(
            self.babbo, self.lista_moneta
        )

        if collisioni:
            if self.soundOnOff:
                arcade.play_sound(self.suono_munch)

            for moneta in collisioni:
                moneta.remove_from_sprite_lists()
                self.punteggio += 1

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = True
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = True
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = False
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = False
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = False


def main():
    gioco = SuperMaincraft(600, 600, "Babbo Natale")
    arcade.run()


if __name__ == "__main__":
    main()