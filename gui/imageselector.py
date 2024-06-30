import sys
import typing
import os
from PySide6.QtCore import Qt, QPoint, QRect, QSize
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QStandardItemModel, QStandardItem

from PySide6.QtWidgets import (
        QWidget, QLayout, QLayoutItem, QStyle, QSizePolicy, QPushButton, QAbstractButton, QRadioButton, QCheckBox,
        QGroupBox, QVBoxLayout, QLabel, QLineEdit, QTreeView, QAbstractItemView, QScrollArea, QPlainTextEdit, QHBoxLayout
        )

from gui.materialwindow import  MHMaterialWindow, MHAssetWindow
from gui.common import IconButton
from core.taglogic import tagLogic

class MHPictSelectable:
    def __init__(self, name: str, icon: str, filename: str, author: str, tags: list):
        self.name = name
        self.filename = filename
        self.author = author
        self.basename = os.path.split(filename)[1].lower()
        self.icon = icon
        self.newTags(tags)
        #
        # append filename, author and  name as tags as well
        #
        self.status = 0

    def newTags(self, tags):
        self.tags = tags
        self.tags.append(self.name.lower())
        self.tags.append(self.basename)    # only name, not path
        if self.author is not None:
            self.tags.append(self.author.lower())

    def newIcon(self, icon):
        self.icon = icon

    def __str__(self):
        return('\n'.join("%s: %s" % item for item in vars(self).items()))

class PictureButton(QPushButton):
    """
    tri-state picture button
    holds state in asset.status to be be reachable from outside
    :param asset: asset to be shown (used for name)
    """
    def __init__(self, asset: MHPictSelectable, scale, emptyicon):

        self.asset = asset
        self.scale = scale
        self.icon = None

        super().__init__()
        if asset.icon is None:                 # will not be constant
            self.icon = emptyicon
            self.picture_added = False
        else:
            self.picture_added = True
            self.icon = asset.icon
        self.setCheckable(True)
        self.framecol  = (Qt.black, Qt.yellow, Qt.green)
        self.setToolTip(asset.name + "\n" + asset.basename)
        self.update()

    #def __del__(self):
    #    print (self.asset.name + " deleted")

    def update(self):
        self.picture = QPixmap(self.icon).scaled(self.scale,self.scale, Qt.AspectRatioMode.KeepAspectRatio)
        super().update()

    def setScale(self, scale):
        self.scale=scale
        self.update()

    def sizeHint(self):
        return self.picture.size()

    def paintEvent(self, e):
        painter = QPainter(self)
        if self.asset.status != 0:
            painter.setOpacity(1)
            painter.drawPixmap(0, 0, self.picture)
            pen = QPen()
            pen.setColor(self.framecol[self.asset.status])
            pen.setWidth(5)

            painter.setPen(pen)
            painter.drawRect(self.rect())
        else:
            painter.setOpacity(0.4)
            painter.drawPixmap(0, 0, self.picture)

        if self.picture_added is False:
            painter.setPen(Qt.black)
            painter.drawText(5, 15, self.asset.name)

        painter.end()

class PicFlowLayout(QLayout):
    """
    parent.selmode: multiple selection, will change refresh method
    """
    def __init__(self, parent, assets, callback, printinfo, margin: int=-1, hSpacing: int=-1, vSpacing: int=-1):

        super().__init__()
        self.itemList = list()
        self.wList = list()
        self.m_hSpace = hSpacing
        self.m_vSpace = vSpacing
        self.selmode = parent.selmode
        self.imagescale = parent.imagescale
        self.empty = parent.emptyIcon
        self.callback = callback
        self.printinfo = printinfo
        self.assetlist = assets
        self.filter = None
        self.ruleset = None
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        # copied for consistency, not sure this is needed or ever called
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item: QLayoutItem):
        self.itemList.append(item)

    def addWidget(self, widget: QWidget):
        self.wList.append(widget)
        super().addWidget(widget)

    def removeAllWidgets(self):
        while ((child := self.takeAt(0)) != None):
            if child.widget() is not None:
                child.widget().deleteLater()
        self.itemList = list()
        self.wList = list()

    def refreshAllWidgets(self):
        for widget in self.wList:
            widget.update()

    def deselectAllWidgets(self):
        for widget in self.wList:
             widget.asset.status = 0
             widget.update()

    def horizontalSpacing(self) -> int:
        if self.m_hSpace >= 0:
            return self.m_hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self) -> int:
        if self.m_vSpace >= 0:
            return self.m_vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self) -> int:
        return len(self.itemList)

    def itemAt(self, index: int) -> typing.Union[QLayoutItem, None]:
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        else:
            return None

    def takeAt(self, index: int) -> typing.Union[QLayoutItem, None]:
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        else:
            return None

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def smartSpacing(self, pm: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()

    def doLayout(self, rect: QRect, testOnly: bool) -> int:
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(+left, +top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y() + bottom

    def updateAsset(self):
        current = self.sender()
        print (current.asset.name + " update")

        if current.asset.status == 0 or current.asset.status == 2:
            #print ("button " + str (self.text) + " pressed")
            current.asset.status = 1
            if self.printinfo is not None:
                self.printinfo(current.asset)
        else:
            #print ("button released")
            current.asset.status = 0
        self.callback(current.asset)
        self.refreshAllWidgets()

    def redisplayWidgets(self, ruleset=None, filtfunc=None):
        self.removeAllWidgets()
        self.populate(ruleset, filtfunc)

    def setImageScale(self, scale):
        self.imagescale = scale
        self.redisplayWidgets(self.ruleset, self.filter)

    def getSelected(self):
        for widget in self.wList:
            if widget.asset.status & 1:
                return(widget.asset)
        return(None)
    
    def newAssetList(self, assets):
        self.assetlist = assets
        
    def populate(self, ruleset, filtertext):
        """
        :assetlist: complete asset list to be considered
        :ruleset: list for comparison or None
        :param filtertext: additional filter text or None
        """
        if filtertext == "":
            filtertext = None

        self.filter = filtertext
        self.ruleset = ruleset

        for asset in self.assetlist:
            #
            # when ruleset in not empty or none check rules per base
    
            if ruleset is not None and bool(ruleset) == True :
                display = True
                for tagelem in asset.tags:
                    basedisplay = False
                    if ":" in tagelem:
                        [base, rest]= tagelem.split(":", 1)
                        if base in ruleset:
                            for rule in ruleset[base]:
                                #
                                # rule as a string is found

                                if rest.startswith(rule):
                                    basedisplay = True
                        else:
                            # no base tag given in rules
                            #
                            basedisplay = True
                    else:
                        # no ':' in tag, no test (should be for wildcards later)
                        #
                        basedisplay = True

                    # all bases form the summary
                    #
                    display = basedisplay & display

            else:
                display = True

            if filtertext is not None:
                fdisplay = False
                for tagelem in asset.tags:
                    if filtertext in tagelem:
                        fdisplay = True
                display = fdisplay & display

            if display:
                button1 = PictureButton(asset, self.imagescale, self.empty)
                button1.pressed.connect(self.updateAsset)
                self.addWidget (button1)

class PicSelectWidget(QWidget):
    """
    PicSelectWidget is a PicFlowLayout embedded in a QGroupBox with a QScrollArea
    addWidget will add a button to the PicFlowLayout
    :param parent: for empty image, selection-mode
    :param callback: function to call when clicked
    """
    def __init__(self, parent, assets, callback, printinfo):
        self.layout = PicFlowLayout(parent, assets, callback, printinfo)
        super().__init__()

    def __del__(self):
        """
        this is a must, otherwise the widgets will use up complete memory
        """
        self.layout.removeAllWidgets()

    def refreshAllWidgets(self):
        self.layout.refreshAllWidgets()

    def deselectAllWidgets(self):
        self.layout.deselectAllWidgets()

    def populate(self, ruleset, filtertext):
        self.layout.populate(ruleset, filtertext)

    def getSelected(self):
        return(self.layout.getSelected())

    def addWidget(self, button):
        self.layout.addWidget (button)

    def setImageScale(self, scale):
        self.layout.setImageScale(scale)

    def redisplayWidgets(self):
        self.layout.redisplayWidgets()

class InformationBox(QWidget):
    def __init__(self, layout):
        super().__init__()
        self.layout = layout
        self.selectedName = QLabel("Name:\nAuthor:")
        self.layout.addWidget(self.selectedName)
        self.layout.addWidget(QLabel("Tags:"))
        self.tagbox = QPlainTextEdit()
        self.tagbox.setPlainText("")
        self.tagbox.setReadOnly(True)
        self.tagbox.setFixedHeight(120)
        self.layout.addWidget(self.tagbox)

    def setInformation(self, asset):
        self.selectedName.setText("Name: " + asset.name + "\n" + "Author: " + asset.author)
        self.tagbox.setPlainText("\n".join(l.replace(":", " \u23f5 ") for l in asset.tags)) # triangle as arrow

class FilterTree(QTreeView):

    def  __init__(self, assets, searchByFilterText, iconpath):
        self.assets = assets
        self.searchByFilterText = searchByFilterText
        self.flowLayout = None
        self.iconpath = iconpath
        self.shortcut = []
        self.shortcutbutton = []

        super().__init__()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.model = QStandardItemModel()
        self.setHeaderHidden(True)
        self.setModel(self.model)
        self.setUniformRowHeights(True)
        self.setFirstColumnSpanned(1, self.rootIndex(), True)

    def setPicLayout(self, layout):
        self.flowLayout = layout

    def addTree(self, subtree, layer=None, base="", search=""):
        """
        recursively try to create a tree from definition, could change depending on structure
        """
        for elem in subtree:
            #
            # set base when layer is None, otherwise keep old one and create substring by appending layer
            find = elem.lower()
            if find == "shortcut":
                for subelem in subtree[elem]:
                    self.shortcut.append(subelem)
                continue
            if find in ( "translate", "guessname"):
                continue
            if base == "":
                substring = ""
                nbase = find
            else:
                nbase = base
                substring = find if search =="" else  search + ":" + find

            if type(elem) is dict:
                self.addTree(elem, layer, nbase, substring)
            else:
                child = QStandardItem(elem)
                if layer is None:
                    child.setSelectable(False)
                    self.model.appendRow([child])
                    child.searchbase = None
                    child.searchpattern = None
                else:
                    layer.appendRow([child])
                    child.searchbase = nbase
                    child.searchpattern = substring
                if type(subtree) is dict:
                    self.addTree(subtree[elem], child, nbase, substring)

    def markSelectedButtons(self, funcid):
        for elem in self.shortcutbutton:
            elem.setChecked(elem._funcid == funcid)

    def shortCutPressed(self):
        """
        create a ruleset by a macro from button, so for an icon lingerie one has:
            gender:female&slot:top:layer1:bra|slot:bottom:layer1:panties
        what creates:
            {'gender': ['female'], 'slot': ['top:layer1:bra', 'bottom:layer1:panties']}
        """
        funcid = self.sender()._funcid
        text = self.shortcut[funcid][1]
        print ("Shortcut pressed: " + text)
        andOps = text.split("&")
        ruleset = {}
        for aelem in andOps:
            orOps = aelem.split("|")
            for oelem in orOps:
                layers = oelem.split(":")
                if len(layers) > 1:
                    key = layers[0]
                    if key in ruleset:
                        ruleset[key].append(":".join(layers[1:]))
                    else:
                        ruleset[key] = [ ":".join(layers[1:]) ]

        self.clearSelection()
        self.setSelectedByRuleset(ruleset)
        self.markSelectedButtons(funcid)
        self.flowLayout.removeAllWidgets()
        self.flowLayout.populate(ruleset, "")


    def addShortCuts(self):
        numicons = len(self.shortcut)
        if numicons == 0:
            return None
        i_per_row = 7

        layout=QVBoxLayout() if numicons > i_per_row else None
        row=QHBoxLayout()
        cnt = 0
        for funcid, elem in enumerate(self.shortcut):
            button = IconButton(funcid, os.path.join(self.iconpath, elem[0]), elem[2], self.shortCutPressed)
            row.addWidget(button)
            self.shortcutbutton.append(button)
            cnt += 1
            if cnt == i_per_row and layout is not None:
                row.addStretch()
                layout.addLayout(row)
                row =QHBoxLayout()
                cnt = 0
        if cnt != 0:
            row.addStretch()
            if layout is not None:
                layout.addLayout(row)

        return ( layout if numicons > i_per_row else row)

    def setSelectedByRuleset(self, ruleset, root=None):
        if root is None:
            root = self.model.invisibleRootItem()
            base = None
        else:
            base = root.searchbase
        if root.hasChildren():
            for index in range (root.rowCount()):
                child = root.child(index,0)
                if base is None:
                    base = child.searchbase
                if base is not None:
                    # must match base:
                    if base in ruleset:
                        if child.searchpattern in ruleset[base]:
                            cindex = self.model.indexFromItem(child)
                            self.setCurrentIndex(cindex)

                self.setSelectedByRuleset(ruleset, child)



    def filterChanged(self):
        """
        create a ruleset from selected items and repopulate the flow-Layout
        """
        if self.flowLayout is None:
            return
        ruleset = {}
        for ix in self.selectedIndexes():
            item = self.model.itemFromIndex(ix)
            base = item.searchbase
            if base not in ruleset:
                ruleset[base] = []
            ruleset[base].append(item.searchpattern)
        filtertext = self.searchByFilterText.text().lower()
        self.markSelectedButtons(-1)
        self.flowLayout.removeAllWidgets()
        self.flowLayout.populate(ruleset, filtertext)

class editBox(QLineEdit):
    def  __init__(self, slayout, sweep):
        super().__init__()
        self.changeFilter = None
        self.empty = IconButton(0, sweep, "Clear filter", self.clearEditBox)
        slayout.addWidget(QLabel("Filter:"))
        slayout.addWidget(self)
        slayout.addStretch()
        slayout.addWidget(self.empty)
        self.setMaximumWidth(170)
        self.setFixedWidth(190)

    def addConnect(self, changeFilter):
        self.changeFilter = changeFilter
        self.returnPressed.connect(changeFilter)

    def clearEditBox(self):
        self.clear()
        if self.changeFilter is not None:
            self.changeFilter()

class ImageSelection():
    def __init__(self, parent, assetrepo, eqtype, selmode, callback, scale=2):
        self.parent = parent
        self.env = parent.glob.env
        self.assetrepo = assetrepo
        self.type = eqtype
        self.selmode = selmode
        self.callback = callback
        self.infobox = None
        self.taglogic = None
        self.filterjson = None
        self.picwidget = None
        self.filterview = None
        self.scales = [48, 64, 96, 128]
        self.emptyIcon = os.path.join(self.env.path_sysdata, "icons", "empty_" + self.type + ".png")
        self.scaleindex = scale
        self.imagescale = self.scales[scale]
        self.rightpanelbuttons = []
        self.button_none = None
        self.button_info = None
        self.button_add = None
        self.button_delete = None
        self.button_mat = None
        if not os.path.isfile(self.emptyIcon):
            self.emptyIcon = os.path.join(self.env.path_sysdata, "icons", "noidea.png")

    def prepareRepo(self):
        self.asset_category = []
        for elem in self.assetrepo:
            if elem.folder == self.type:
                elem.tag = self.taglogic.completeTags(elem.name, elem.tag)
                self.asset_category.append(MHPictSelectable(elem.name, elem.thumbfile, elem.path,  elem.author, elem.tag))

    def prepare(self):
        #
        # load filter from file according to base mesh
        # then create an asset-category repo for this folder and convert it by taglogic
        #
        path = self.env.stdSysPath(self.type, "selection_filter.json")
        self.filterjson = self.env.readJSON(path)
        if self.filterjson is None:
            self.filterjson =  {}

        self.taglogic = tagLogic(self.filterjson)
        self.taglogic.create()
        self.prepareRepo()

    def getTagProposals(self):
        return(self.taglogic.proposals())

    def changeStatus(self):
        checked = []
        for elem in self.assetrepo:
            if elem.folder == self.type and elem.used is True:
                checked.append(elem.path)

        on = 2 if self.selmode == 1 else 1

        for elem in self.asset_category:
            elem.status = 2 if elem.filename in checked else 0

    def picButtonChanged(self, asset):
        multi = (self.selmode == 1)
        print ("********** changed:" + asset.name + " ************")

        # yellow 
        if asset.status == 1:
            self.materialCallback(update=True)
            self.assetCallback(update=True)

            # set all yellow ones back to green or nothing
            #
            self.changeStatus()
            asset.status = 1
            self.picwidget.refreshAllWidgets()

        # deselect
        #
        elif asset.status == 0:
            found = self.parent.glob.baseClass.getAttachedByFilename(asset.filename)
            if multi is True:
                asset.status = 2 if found is not None else 0
            else:
                if found:
                    self.callback(asset, self.type, multi)

        self.refreshButtons()

        if self.type == "models":
            print ("in models")
            if self.button_add is None:
                print ("add is none")
                self.callback(asset, self.type, False)

    def scaleImages(self):
        # toggle through 4 scales
        self.scaleindex = (self.scaleindex + 1) % 4
        self.imagescale = self.scales[self.scaleindex]
        self.picwidget.setImageScale(self.imagescale)

    def rescanFolder(self):
        """
        rescan folder:
        - get new assetrepo (only for type)
        - remove widgets
        - prepare new Repo (tags), send new repo and populate widget
        """
        self.assetrepo = self.parent.glob.rescanAssets(self.type)

        self.picwidget.layout.removeAllWidgets()
        for elem in self.parent.glob.baseClass.attachedAssets:
            self.parent.glob.markAssetByFileName(elem.filename, True)
        self.prepareRepo()
        self.picwidget.layout.newAssetList(self.asset_category)
        self.picwidget.populate(None, None)
        self.changeStatus()

    def getSelectFromAttachedAssets(self):
        selected = self.picwidget.getSelected()
        if selected is not None:
            elem = self.parent.glob.baseClass.getAttachedByFilename(selected.filename)
            if elem is not None:
                return(elem, selected)

        return(None, None)

    def getSelectedFromRepo(self):
        selected = self.picwidget.getSelected()
        if selected is not None:
            elem = self.parent.glob.getAssetByFilename(selected.filename)
            if elem is not None:
                return(elem, selected)
        return(None, None)

    def loadCallback(self):
        (elem, asset) = self.getSelectedFromRepo()
        multi = (self.selmode == 1)
        self.callback(asset, self.type, multi)
        self.changeStatus()
        if multi:
            asset.status = 2
        else:
            asset.status = 1
        self.refreshButtons()
        self.picwidget.refreshAllWidgets()

    def deleteCallback(self):
        (elem, asset) = self.getSelectedFromRepo()
        if asset is None:
            return
        asset.status = 0
        multi = (self.selmode == 1)
        self.callback(asset, self.type, multi)
        self.changeStatus()
        self.refreshButtons()
        self.picwidget.refreshAllWidgets()

    def noneCallback(self):
        (elem, asset) = self.getSelectedFromRepo()
        multi = (self.selmode == 1)
        if multi is True:
            names = []
            for elem in self.parent.glob.baseClass.attachedAssets:
                if elem.type == self.type:
                    names.append(elem.filename)

            for name in names:
                self.callback(name, self.type, multi)  # for clothes all clothes
        else:
            if asset is None:
                return
            print (asset.filename)
            asset.status = 0
            self.callback(asset, self.type, multi)
        self.refreshButtons()
        self.picwidget.deselectAllWidgets()

    def materialCallback(self, status=False, update=False):
        """
        status is internal from PushButton
        """

        # without window visible no update
        #
        if update and (self.parent.material_window is None or self.parent.material_window.isVisible() is False):
            return

        found, dummy = self.getSelectFromAttachedAssets()
        if found is None:
            if self.parent.material_window is not None and self.parent.material_window.isVisible():
                self.parent.material_window.updateWidgets([], None)
            return

        matimg = []
        oldmaterial = found.material
        matfiles = found.obj.listAllMaterials()
        for elem in matfiles:
            (folder, name) = os.path.split(elem)
            thumb = elem[:-6] + ".thumb"
            if not os.path.isfile(thumb):
                thumb = None
            p = MHPictSelectable(name[:-6], thumb, elem, None, [])
            if elem == oldmaterial:
                p.status = 1
            matimg.append(p)
        if self.parent.material_window is None:
            self.parent.material_window = MHMaterialWindow(self.parent, PicSelectWidget, matimg, found)
        else:
            self.parent.material_window.updateWidgets(matimg, found)

        mw = self.parent.material_window
        mw.show()
        mw.activateWindow()

    def changeTags(self, asset, iconpath):
        for elem in self.asset_category:
            if elem.filename == asset.path:
                newtags= self.taglogic.completeTags(elem.name, asset.tags)
                elem.newTags(newtags)
                self.infobox.setInformation(elem)
                if iconpath is not None:
                    elem.newIcon(iconpath)
                    self.picwidget.setImageScale(self.imagescale)

    def assetCallback(self, status=False, update=False):

        # without window visible no update
        #
        if update and (self.parent.asset_window is None or self.parent.asset_window.isVisible() is False):
            return

        found, selected  = self.getSelectedFromRepo()
        if found is None:
            if self.parent.asset_window is not None and self.parent.asset_window.isVisible():
                self.parent.asset_window.updateWidgets(None, None, self.emptyIcon)
            return

        if self.parent.asset_window is None:
            self.parent.asset_window = MHAssetWindow(self.parent, self.changeTags, found, selected, self.emptyIcon, self.taglogic.proposals())
        else:
            self.parent.asset_window.updateWidgets(found, selected, self.emptyIcon, self.taglogic.proposals())

        mw = self.parent.asset_window
        mw.show()
        mw.activateWindow()


    def leftPanel(self):
        """
        done first
        """
        iconpath = os.path.join(self.env.stdSysPath(self.type), "icons")
        
        v1layout = QVBoxLayout()    # this is for searching
        self.infobox = InformationBox(v1layout)

        slayout = QHBoxLayout()  # layout for textbox + empty button
        filteredit = editBox(slayout, os.path.join(self.env.path_sysicon, "sweep.png" ))
        self.filterview = FilterTree(self.asset_category, filteredit, iconpath)
        self.filterview.addTree(self.filterjson)
        self.filterview.selectionModel().selectionChanged.connect(self.filterview.filterChanged)
        shortcuts = self.filterview.addShortCuts()
        filteredit.addConnect(self.filterview.filterChanged)

        v1layout.addWidget(self.filterview)
        if shortcuts is not None:
            v1layout.addLayout(shortcuts)
        v1layout.addLayout(slayout)

        return(v1layout)

    def rightPanelButtons(self, bitmask):
        hlayout = QHBoxLayout()

        if bitmask & 4:
            path = os.path.join(self.env.path_sysicon, "use.png" )
            self.button_add = IconButton(0, path, "Load/Use asset", self.loadCallback)
            hlayout.addWidget(self.button_add )
        else:
            self.button_add = None

        if bitmask & 8:
            if self.selmode == 1:
                path = os.path.join(self.env.path_sysicon, "none.png" )
                self.button_none = IconButton(0, path, "Drop all assets", self.noneCallback)
                hlayout.addWidget(self.button_none)

            path = os.path.join(self.env.path_sysicon, "delete.png" )
            self.button_delete = IconButton(0, path, "Drop this asset", self.deleteCallback)
            hlayout.addWidget(self.button_delete)
        else:
            self.button_none = None
            self.button_delete = None

        if bitmask & 1:
            path = os.path.join(self.env.path_sysicon, "information.png" )
            self.button_info = IconButton(0, path, "Change asset information", self.assetCallback)
            hlayout.addWidget(self.button_info )
        else:
            self.button_info = None

        if bitmask & 2:
            path = os.path.join(self.env.path_sysicon, "materials.png" )
            self.button_mat = IconButton(0, path, "Change material", self.materialCallback)
            hlayout.addWidget(self.button_mat)
        else:
            self.button_mat = None

        hlayout.addStretch()

        resize = os.path.join(self.env.path_sysicon, "resize.png" )
        sizebutton = IconButton(0, resize, "Resize thumbnails", self.scaleImages)
        hlayout.addWidget(sizebutton)

        rescan = os.path.join(self.env.path_sysicon, "rescan.png" )
        rescanbutton = IconButton(0, rescan, "Rescan folder", self.rescanFolder)
        hlayout.addWidget(rescanbutton)

        return (hlayout)

    def refreshButtons(self):

        # none button: enabled when one asset is supplied
        #
        if self.button_none:
            cnt = self.parent.glob.baseClass.countAttachedByType(self.type)
            self.button_none.setEnabled(cnt != 0)

        # must be yellow (selected) for add and info
        #
        selected = self.picwidget.getSelected()
        if self.button_info:
            self.button_info.setEnabled(selected is not None)

        # must be selected and supplied for delete, material
        # reuse selected

        if self.selmode == 1:
            if self.button_add:
                self.button_add.setEnabled(selected is not None)

        used = False
        if selected is not None:
            if self.parent.glob.baseClass.isLinkedByFilename(selected.filename) is not None:
                used  = True

        if self.selmode == 0:
            if self.button_add:
                self.button_add.setEnabled((selected is not None)  and not used)

        if self.button_delete:
            self.button_delete.setEnabled(used)

        if self.button_mat:
            self.button_mat.setEnabled(used)


    def rightPanel(self, bitmask=3):
        """
        draw right Panel
        """
        layout = QVBoxLayout()
        layout.addLayout(self.rightPanelButtons(bitmask))

        widget = QWidget()
        infocallback = self.infobox.setInformation if self.infobox is not None else None
        self.picwidget = PicSelectWidget(self, self.asset_category, self.picButtonChanged, infocallback)
        if infocallback is not None:
            self.filterview.setPicLayout(self.picwidget.layout)
        self.picwidget.populate(None, None)
        self.changeStatus()
        widget.setLayout(self.picwidget.layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(widget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        layout.addWidget(scrollArea)
        (elem, asset) = self.getSelectedFromRepo()
        self.refreshButtons()
        return(layout)

