import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt, QTimer, QUrl, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QPixmap, QPainter
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

import random
import Settings
import math

ScreenSize = Settings.ScreenSize

class Game():
    def __init__(self):
        self.scores = [0, 0]
        self.player1_position = [round(ScreenSize[0] / 2), round(ScreenSize[1] - 75)]
        self.player2_position = [round(ScreenSize[0] / 2), 0]
        self.ball_position = [round(ScreenSize[0] / 2), round(ScreenSize[1] / 2)]
        self.ball_velocity = Settings.DefaultBallSpeed


class GameScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Ping Pong")
        self.setGeometry(100, 100, ScreenSize[0], ScreenSize[1])
        self.setFixedSize(ScreenSize[0], ScreenSize[1])

        self.paddle_radius = 45
        self.ShouldDrawInterface = False
        self.keys_pressed = set()
        self.game = Game()

        self.CurrentRandomEvent = ""
        self.EventsList = ["Transparent Rackets!","Fast Rackets!", "Faster Ball!"]

        self.player1_sprite = QPixmap("C:\\Projects\\Samples\\FinalProjectPingPong\\Sprites\\racket1.png")
        self.player2_sprite = QPixmap("C:\\Projects\\Samples\\FinalProjectPingPong\\Sprites\\racket2.png")
        self.ball_sprite = QPixmap("C:\\Projects\\Samples\\FinalProjectPingPong\\Sprites\\ball.png")

        if self.player1_sprite.isNull():
            print("Failed to load racket1.png")
            return

        if self.player2_sprite.isNull():
            print("Failed to load racket2.png")
            return

        if self.ball_sprite.isNull():
            print("Failed to load ball.png")
            return

        self.mainMenu = QWidget()
        self.gameWidget = QWidget()
        self.gameOverScreen = QWidget()

        self.currentWidget = self.mainMenu
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.currentWidget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(1000 // 60)

        self.event_timer = QTimer()
        self.event_timer.timeout.connect(self.clear_event)
        self.event_timer.setSingleShot(True)

        self.event_message_label = QLabel(self)
        self.event_message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.event_message_label.setStyleSheet("color: black; font-size: 16px;")
        self.event_message_label.setGeometry(0,ScreenSize[1] - 300 , ScreenSize[0], 30)

        self.event_message_timer = QTimer()
        self.event_message_timer.timeout.connect(self.clear_msg)
        self.event_message_timer.setSingleShot(True)

        self.background_music = QMediaPlayer()
        self.background_music_output = QAudioOutput()
        self.background_music.setAudioOutput(self.background_music_output)

        self.background_music.setSource(QUrl.fromLocalFile("Sounds\\mus_menu6.mp3"))
        self.background_music_output.setVolume(0.5)
        self.background_music.setLoops(2147483647)
        self.background_music.play()

        self.hit_sound = QMediaPlayer()
        self.hit_sound_ou = QAudioOutput()
        self.hit_sound.setAudioOutput(self.hit_sound_ou)
        self.hit_sound.setSource(QUrl.fromLocalFile("Sounds\\hit.mp3"))

        self.score_sound = QMediaPlayer()
        self.score_sound_ou = QAudioOutput()
        self.score_sound.setAudioOutput(self.score_sound_ou)
        self.score_sound.setSource(QUrl.fromLocalFile("Sounds\\score.mp3"))

        self.setupMainMenu()
        self.setupGameWidget()
        self.setupGameOverScreen()

    def reset(self):
        self.game = Game()
        self.game.scores = [0, 0]
        self.game.player1_position = [round(ScreenSize[0] / 2), round(ScreenSize[1] - 75)]
        self.game.player2_position = [round(ScreenSize[0] / 2), 0]
        self.game.ball_position = [round(ScreenSize[0] / 2), round(ScreenSize[1] / 2)]
        self.game.ball_velocity = Settings.DefaultBallSpeed

    def on_media_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.background_music.play()

    def clear_event(self):
        if self.CurrentRandomEvent == "Faster Ball!":
            self.game.ball_velocity[0] /= 2
            self.game.ball_velocity[1] /= 2

        if self.CurrentRandomEvent == "Fast Rackets!":
            Settings.PlayerSpeed /= 2

        self.CurrentRandomEvent = ""

    def clear_msg(self):
        self.event_message_label.setText("")

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QColor(255, 174, 66))
        painter.drawRect(0, 0, ScreenSize[0], ScreenSize[1])

        if self.ShouldDrawInterface:
            if self.CurrentRandomEvent == "Transparent Rackets!":
                painter.setOpacity(0.15)

            painter.drawPixmap(self.game.player1_position[0], self.game.player1_position[1], self.player1_sprite)
            painter.drawPixmap(self.game.player2_position[0], self.game.player2_position[1], self.player2_sprite)

            if self.CurrentRandomEvent == "Transparent Rackets!":
                painter.setOpacity(1)


            painter.drawPixmap(self.game.ball_position[0], self.game.ball_position[1], self.ball_sprite)

            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.setFont(QFont("ComicSans", 15))
            painter.drawText(10, round((ScreenSize[1]/2) - 30), f"P 1: {self.game.scores[0]}")
            painter.drawText(10, round((ScreenSize[1]/2) - 5), f"P 2: {self.game.scores[1]}")

            if Settings.HitboxesEnabled:
                painter.setBrush(QColor(255, 0, 255, 127))
                painter.drawEllipse(round(self.game.player1_position[0]), round(self.game.player1_position[1]),
                            round(self.paddle_radius), round(self.paddle_radius))

                painter.setBrush(QColor(255, 255, 0, 127))
                painter.drawEllipse(round(self.game.player2_position[0]), round(self.game.player2_position[1]),
                            round(self.paddle_radius), round(self.paddle_radius))

    def update_game(self):
        if self.currentWidget == self.gameWidget:
            self.ShouldDrawInterface = True
        elif self.currentWidget == self.gameOverScreen:
            self.ShouldDrawInterface = False
        elif self.currentWidget == self.mainMenu:
            self.ShouldDrawInterface = False
        else:
            print("what")

        if self.ShouldDrawInterface:
            if self.CurrentRandomEvent == "":
                if random.randint(1, 150) == 10:
                    self.CurrentRandomEvent = random.choice(self.EventsList)
                    self.event_timer.start(10000)
                    self.event_message_label.setText(self.CurrentRandomEvent)
                    self.event_message_timer.start(1000)

                    print(self.CurrentRandomEvent)
                    if self.CurrentRandomEvent == "Faster Ball!":
                        self.game.ball_velocity[0] *= 2
                        self.game.ball_velocity[1] *= 2
                    if self.CurrentRandomEvent == "Fast Rackets!":
                        Settings.PlayerSpeed *= 2

            if Settings.Player1Left in self.keys_pressed and self.game.player1_position[0] > 0:
                self.game.player1_position[0] -= Settings.PlayerSpeed
            if Settings.Player1Right in self.keys_pressed and self.game.player1_position[0] < round(
                    ScreenSize[0]) - self.player1_sprite.width():
                self.game.player1_position[0] += Settings.PlayerSpeed

            if Settings.Player2Left in self.keys_pressed and self.game.player2_position[0] > 0:
                self.game.player2_position[0] -= Settings.PlayerSpeed
            if Settings.Player2Right in self.keys_pressed and self.game.player2_position[0] < round(
                    ScreenSize[0]) - self.player2_sprite.width():
                self.game.player2_position[0] += Settings.PlayerSpeed

            self.game.ball_position[0] += round(self.game.ball_velocity[0])
            self.game.ball_position[1] += round(self.game.ball_velocity[1])

            self.game.ball_velocity = self.handle_collision(self.game.player1_position)
            self.game.ball_velocity = self.handle_collision(self.game.player2_position)

            if self.game.ball_position[1] <= 0:
                self.game.scores[0] += 1
                self.score_sound.play()
            if self.game.ball_position[1] >= round(ScreenSize[1]):
                self.game.scores[1] += 1
                self.score_sound.play()

            if self.game.scores[0] >= Settings.ScoreToWin or self.game.scores[1] >= Settings.ScoreToWin:
                self.showGameOverScreen()

            if self.game.ball_position[0] <= 0 or self.game.ball_position[0] >= round(ScreenSize[0]):
                self.game.ball_velocity[0] = -self.game.ball_velocity[0]
            if self.game.ball_position[1] <= 0 or self.game.ball_position[1] >= round(ScreenSize[1]):
                self.game.ball_velocity[1] = -self.game.ball_velocity[1]

        self.update()

    def handle_collision(self, paddle_position):
        ball_width, ball_height = self.ball_sprite.width(), self.ball_sprite.height()
        ball_radius = (ball_width ** 2 + ball_height ** 2) ** 0.5 / 2

        dx = self.game.ball_position[0] - paddle_position[0]
        dy = self.game.ball_position[1] - paddle_position[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.paddle_radius + ball_radius:
            angle = math.atan2(dy, dx)
            speed = math.sqrt(self.game.ball_velocity[0] ** 2 + self.game.ball_velocity[1] ** 2)
            new_speed_x = speed * math.cos(angle)
            new_speed_y = speed * math.sin(angle)
            self.hit_sound.play()
            return [new_speed_x, new_speed_y]
        else:
            return self.game.ball_velocity

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.key())

    def hideCurrentWidget(self):
        self.layout().removeWidget(self.currentWidget)
        self.currentWidget.hide()

    def setupMainMenu(self):
        layout = QVBoxLayout()

        label = QLabel("Welcome To Ping Pong!")
        label.setFont(QFont("Helvetica", 24))
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        play_button = QPushButton("Play Game")
        play_button.clicked.connect(self.showGameWidget)
        play_button.setFixedSize(250, 50)
        play_button.setStyleSheet("""
              QPushButton {
                  color: white; 
                  border: 2px solid white;
                  background-color: #000000; 
                  font-size: 16px; 
                  padding: 10px 20px; 
              }
          """)
        play_button.setFont(QFont("Helvetica", 14))
        layout.addWidget(play_button, alignment=Qt.AlignmentFlag.AlignCenter)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.quit)
        quit_button.setFixedSize(250, 50)
        quit_button.setStyleSheet("""
               QPushButton {
                   color: white; 
                   border: 2px solid white;
                   background-color: #000000; 
                   font-size: 16px; 
                   padding: 10px 20px; 
               }
           """)
        quit_button.setFont(QFont("Helvetica", 14))
        layout.addWidget(quit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mainMenu.setLayout(layout)

    def setupGameWidget(self):
        layout = QVBoxLayout()
        self.gameWidget.setLayout(layout)
    def setupGameOverScreen(self):
        layout = QVBoxLayout()

        texter = self.game.scores[0] >= Settings.ScoreToWin and "Player 1 Won!" or "Player 2 Won!"

        label = QLabel(texter)
        label.setFont(QFont("Helvetica", 24))
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        restart_button = QPushButton("Restart")
        restart_button.clicked.connect(self.showGameWidget)
        restart_button.setFixedSize(250, 50)
        restart_button.setStyleSheet("""
                      QPushButton {
                          color: white; 
                          border: 2px solid white;
                          background-color: #000000; 
                          font-size: 16px; 
                          padding: 10px 20px; 
                      }
                  """)
        restart_button.setFont(QFont("Helvetica", 14))
        layout.addWidget(restart_button, alignment=Qt.AlignmentFlag.AlignCenter)

        menu_button = QPushButton("Go Back To Menu")
        menu_button.clicked.connect(self.showMainMenu)
        menu_button.setFixedSize(250, 50)
        menu_button.setStyleSheet("""
                             QPushButton {
                                 color: white; 
                                 border: 2px solid white;
                                 background-color: #000000; 
                                 font-size: 16px; 
                                 padding: 10px 20px; 
                             }
                         """)
        menu_button.setFont(QFont("Helvetica", 14))
        layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.gameOverScreen.setLayout(layout)

    def showMainMenu(self):
        self.background_music.setSource(QUrl.fromLocalFile("Sounds\\mus_menu6.mp3"))
        self.background_music.play()
        self.hideCurrentWidget()
        self.currentWidget = self.mainMenu
        self.layout().addWidget(self.mainMenu)

    def showGameWidget(self):
        self.background_music.setSource(QUrl.fromLocalFile("Sounds\\mus_game.mp3"))
        self.background_music.play()
        self.hideCurrentWidget()
        self.currentWidget = self.gameWidget
        self.layout().addWidget(self.gameWidget)
    def showGameOverScreen(self):
        self.background_music.setSource(QUrl.fromLocalFile("Sounds\\mus_win.mp3"))
        self.background_music.play()
        self.hideCurrentWidget()
        self.reset()
        self.currentWidget = self.gameOverScreen
        self.layout().addWidget(self.gameOverScreen)

    def quit(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameScreen()
    window.show()
    sys.exit(app.exec())