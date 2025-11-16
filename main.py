import sys
import ctypes
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

WS_EX_TRANSPARENT = 0x20
WS_EX_LAYERED = 0x80000
GWL_EXSTYLE = -20


class TransparentWindow(QWidget):
    def __init__(self, img_path):
        super().__init__()

        self.locked = False
        self.dragging = False
        self.resizing = False

        self.start_pos = QPoint()
        self.start_box_pos = QPoint()
        self.start_size = QSize()

        self.pix = QPixmap(img_path)
        if self.pix.isNull():
            print("ERRO: imagem não carregou!")

        # posição e tamanho da imagem
        self.box_rect = QRect(200, 200, 350, 250)

        # janela transparente e fullscreen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.setFocus()

    # ----------------------------------
    # DESENHO MANUAL (SEM QLabel)
    # ----------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)

        # fundo escuro para saber se usa fullscreen (remova depois), ou deixa ativado pra bloquear o clique
        # painter.fillRect(self.rect(), QColor(0, 0, 0, 110))

        # caixa (bordas)
        painter.setPen(QPen(QColor(150, 0, 200), 2))
        painter.setBrush(QColor(255, 255, 255, 30))
        painter.drawRect(self.box_rect)

        # imagem
        if not self.pix.isNull():
            painter.drawPixmap(self.box_rect, self.pix)

        # handle (quadrado preto)
        handle = QRect(self.box_rect.right() - 20, self.box_rect.bottom() - 20, 20, 20)
        painter.fillRect(handle, QColor(0, 0, 0))

    # ----------------------------------
    # MOUSE
    # ----------------------------------
    def mousePressEvent(self, e):
        if self.locked:
            return

        pos = e.pos()

        # handle
        handle = QRect(self.box_rect.right() - 20, self.box_rect.bottom() - 20, 20, 20)
        if handle.contains(pos):
            self.resizing = True
            self.start_pos = pos
            self.start_size = self.box_rect.size()
            return

        # mover
        if self.box_rect.contains(pos):
            self.dragging = True
            self.start_pos = pos
            self.start_box_pos = self.box_rect.topLeft()

    def mouseMoveEvent(self, e):
        if self.locked:
            return

        if self.dragging:
            delta = e.pos() - self.start_pos
            self.box_rect.moveTopLeft(self.start_box_pos + delta)
            self.update()

        if self.resizing:
            delta = e.pos() - self.start_pos
            new_w = max(50, self.start_size.width() + delta.x())
            new_h = max(50, self.start_size.height() + delta.y())
            self.box_rect.setSize(QSize(new_w, new_h))
            self.update()

    def mouseReleaseEvent(self, e):
        self.dragging = False
        self.resizing = False

    # ----------------------------------
    # TECLADO
    # ----------------------------------
    def keyPressEvent(self, e):
        if e.modifiers() & Qt.AltModifier:

            # opacidade da janela
            if e.key() == Qt.Key_Up:
                self.setWindowOpacity(min(1.0, self.windowOpacity() + 0.05))

            if e.key() == Qt.Key_Down:
                self.setWindowOpacity(max(0.05, self.windowOpacity() - 0.05))

            if e.key() == Qt.Key_Left:
                self.toggle_lock()

    # ----------------------------------
    # CLICK THROUGH
    # ----------------------------------
    def toggle_lock(self):
        hwnd = int(self.winId())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        self.locked = not self.locked

        if self.locked:
            style |= WS_EX_TRANSPARENT | WS_EX_LAYERED
            print("LOCKED → click-through ativado")
        else:
            style &= ~WS_EX_TRANSPARENT
            print("UNLOCKED → janela interativa")

        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Use: python main.py caminho_da_imagem")
        sys.exit()

    app = QApplication(sys.argv)
    win = TransparentWindow(sys.argv[1])
    sys.exit(app.exec_())
