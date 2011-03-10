
import os,sys

from PyQt4 import QtGui,QtCore
from rename_ui import Ui_mainWidget
import rename_rc

class RenameWidget(QtGui.QWidget):
    'Rename Main Widget'
    def __init__(self,parent=None):
        super(RenameWidget,self).__init__(parent)
        self.ui = Ui_mainWidget()
        self.ui.setupUi(self)
        self.myDirView = self.ui.dirView
        self.myFileListWidget = self.ui.fileListWidget
        self.myExtCombo = self.ui.extCombo

        self.model = QtGui.QDirModel()
        self.model.setReadOnly(True)
        self.model.setSorting(QtCore.QDir.DirsFirst or QtCore.QDir.IgnoreCase or QtCore.QDir.Name)
        self.ui.dirView.setModel(self.model)
        header = self.ui.dirView.header()
        header.setStretchLastSection(True)
        header.setClickable(True)

        ind = self.model.index(QtCore.QDir.currentPath())
        self.showFileList(ind)
        self.myDirView.scrollTo(ind)
        self.myDirView.resizeColumnToContents(0)
        self.myDirView.hideColumn(1)
        self.myDirView.hideColumn(2)
        self.myDirView.hideColumn(3)
        self.myDirView.setAnimated(True)

        self.ui.startCombo.setEditText('1')

        self.myDirView.expanded.connect(self.showFileList)
        self.myExtCombo.activated.connect(self.filterExt)
        self.ui.aboutBtn.clicked.connect(self.about)
        self.ui.closeBtn.clicked.connect(self.close)
        self.ui.renameBtn.clicked.connect(self.act)
        self.ui.letterRadio.toggled.connect(self.letterToggled)

    def showFileList(self,index):
        'Show file names in TableWidget'
        self.myDir = index.data().toString().toUtf8()
        par = index.parent()
        while par.data().toString() != '':
            self.myDir = par.data().toString() + os.sep + self.myDir
            par = par.parent()
        dirList = os.listdir(unicode(self.myDir,'utf8','ignore'))
        self.noFilterFileList = []
        self.renameMap = {}
        self.myExtCombo.clear()
        for fileName in dirList:
            if os.path.isdir(unicode(self.myDir,'utf8','ignore') + os.sep + fileName):
                continue
            self.noFilterFileList.append(fileName)
            self.renameMap[fileName] = fileName
        self.myExtCombo.addItem(unicode('All Files','utf8','ignore'))
        for fileName in self.noFilterFileList:
            ext = os.path.splitext(fileName)[1]
            if self.myExtCombo.findText(ext) == -1:
                self.myExtCombo.addItem(ext)
        self.myExtCombo.setCurrentIndex(0)

        self.refreshFileList()


    def refreshFileList(self):
        self.myFileListWidget.clearContents()
        self.myFileListWidget.setRowCount(len(self.renameMap))
        if len(self.renameMap) != 0:
            for row in range(len(self.renameMap)):
                item1 = QtGui.QTableWidgetItem(sorted(self.renameMap.keys())[row])
                self.myFileListWidget.setItem(row,0,item1)
                item2 = QtGui.QTableWidgetItem(sorted(self.renameMap.values())[row])
                item2.setTextColor(QtGui.QColor(0,0,200))
                self.myFileListWidget.setItem(row,1,item2)


    def filterExt(self):
        'Filter file ext'

        curExt = unicode(self.myExtCombo.currentText().toUtf8(),'utf8','ignore')
        if curExt != u'All Files':
            self.renameMap.clear()
            for fileName in self.noFilterFileList:
                if os.path.splitext(fileName)[1] == curExt:
                    self.renameMap[fileName] = fileName
        else:
            for fileName in self.noFilterFileList:
                self.renameMap[fileName] = fileName

        self.refreshFileList()


    def about(self):
        'About Dialog'
        QtGui.QMessageBox.about(self,'About Renamer',
                          '<font color="blue">Renamer v1.0</font><br> \
                          A useful toolkit for rename many files at one time!<br> \
                          Author:<font color="blue">PinkyJie</font><br> \
                          Powered by <font color="blue">Python+PyQt</font><br> \
                          Need more infomation? Visit <a href="http://pinkyway.info">PinkyWay.info</a>')


    def act(self):
        'Rename Action'
        prefix = unicode(self.ui.prefixEdit.text().toUtf8(),'utf8','ignore')
        postfix = unicode(self.ui.postfixEdit.text().toUtf8(),'utf8','ignore')
        count = str(self.ui.countSpin.text())
        letter_flag = self.ui.letterRadio.isChecked()
        num_flag = self.ui.numRadio.isChecked()
        start = str(self.ui.startCombo.currentText())

        if num_flag:
            try:
                assert start.isdigit()
            except AssertionError:
                QtGui.QMessageBox.warning(None,'Error','Since you selected "Number",<br> \
                "Start with" option must be a number too!<br>Input again!')
                self.ui.startCombo.setFocus()
                return
            asc = int(start)

        if letter_flag:
            asc = ord(start)
            if start.islower():
                origin = ord('a')
                limit = ord('z')
            else:
                origin = ord('A')
                limit = ord('Z')
        self.newNameList = []
        tmpList = []
        for fileName in sorted(self.renameMap.keys()):
            ext = os.path.splitext(fileName)[1]
            tmpName = os.path.splitext(fileName)[0]+u'_1'+ext
            os.rename(unicode(self.myDir,'utf8','ignore') + os.sep + fileName, \
                      unicode(self.myDir,'utf8','ignore') + os.sep + tmpName)
            tmpList.append(tmpName)
        for fileName in tmpList:
            ext = os.path.splitext(fileName)[1]
            if letter_flag:
                newName = prefix + str(chr(asc))*int(count) + postfix + ext
            if num_flag:
                newName = prefix + str(asc).zfill(int(count)) + postfix + ext
            os.rename(unicode(self.myDir,'utf8','ignore') + os.sep + fileName, \
                      unicode(self.myDir,'utf8','ignore') + os.sep + newName)
            origin_index = os.path.splitext(fileName)[0].rpartition('_1')[0] + ext
            self.renameMap[origin_index] = newName
            asc += 1
            if letter_flag and asc > limit:
                asc = origin

        QtGui.QMessageBox.information(None,'Success','%d files renaming done!' % len(self.renameMap))

        self.model.refresh()
        self.refreshFileList()

        newNameList = self.renameMap.values()
        self.renameMap.clear()
        for fileName in newNameList:
            self.renameMap[fileName] = fileName


    def letterToggled(self,flag):
        'Using Letter'
        self.ui.startCombo.clear()
        if flag:
            self.ui.startCombo.setEditable(False)
            for letter in range(ord('a'),ord('z')+1):
                self.ui.startCombo.addItem(chr(letter))
            for letter in range(ord('A'),ord('Z')+1):
                self.ui.startCombo.addItem(chr(letter))
        else:
            self.ui.startCombo.setEditable(True)




if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    myRename = RenameWidget()
    myRename.setFixedSize(myRename.size())
    myRename.setWindowIcon(QtGui.QIcon(':/xigua.png'))
    myRename.show()
    sys.exit(app.exec_())
