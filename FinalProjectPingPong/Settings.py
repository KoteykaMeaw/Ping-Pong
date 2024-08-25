from PyQt6.QtCore import Qt

#MAIN GAME SETTINGS
ScreenSize = [400,600]
HitboxesEnabled = False
DefaultBallSpeed = [5,5]

#PLAYER SETTINGS
PlayerSpeed = 10
Player1Left,Player1Right = Qt.Key.Key_J,Qt.Key.Key_L
Player2Left,Player2Right = Qt.Key.Key_A,Qt.Key.Key_D

#SCORE SETTINGS
DefaultScore = [0,0]
ScoreToWin = 10