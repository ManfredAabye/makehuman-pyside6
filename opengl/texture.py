from PySide6.QtOpenGL import QOpenGLTexture
from PySide6.QtGui import QImage, QColor
from PySide6.QtCore import QSize

class TextureRepo():
    def __init__(self):
        self.textures = {}

    def getTextures(self):
        return self.textures

    def show(self):
        for t in self.textures.keys():
            print (t, self.textures[t][1])

    def add(self, path, texture):
        if path not in self.textures:
            self.textures[path] = [texture, 1]

    def exists(self, path):
        if path in self.textures:
            return self.textures[path][0]

    def inc(self, path):
        if path in self.textures:
            self.textures[path][1] += 1

    def delete(self, texture):
        t = self.textures
        for elem in t:
            if t[elem][0] == texture:
                if t[elem][1] > 1:
                    t[elem][1] -= 1
                else:
                    t[elem][0].destroy()
                    del t[elem]
                return

    def cleanup(self):
        """
        central location to delete textures
        """
        t = self.textures
        for elem in t:
            t[elem][0].destroy()
        self.textures = {}

class MH_Texture():
    def __init__(self, repo):
        self.repo = repo
        self.texture = QOpenGLTexture(QOpenGLTexture.Target2D)

    def create(self, name, image):
        """
        :param image: QImage
        :param name: image path, used in repo to identify object
        """
        self.texture.create()
        self.texture.setData(image)
        self.texture.setMinMagFilters(QOpenGLTexture.Linear, QOpenGLTexture.Linear)
        self.texture.setWrapMode(QOpenGLTexture.ClampToEdge)

        return self.texture

    def destroy(self):
        self.texture.destroy()

    def delete(self):
        self.repo.delete(self.texture)

    def unicolor(self, rgb = [0.5, 0.5, 0.5]):
        color = QColor.fromRgbF(rgb[0], rgb[1], rgb[2])
        name = "Generated color [" + hex(color.rgb()) + "]"
        texture = self.repo.exists(name)
        if texture is not None:
            self.repo.inc(name)
            return texture

        image = QImage(QSize(1,1),QImage.Format_ARGB32)
        image.fill(color)
        self.texture = self.create(name, image)
        self.repo.add(name, self.texture)
        return self.texture


    def load(self, path):
        """
        load textures
        """
        texture = self.repo.exists(path)
        if texture is not None:
            self.repo.inc(path)
            return texture

        image = QImage(path)
        self.create(path, image)
        self.repo.add(path, self.texture)
        return self.texture
