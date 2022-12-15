import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
import random
import time
import logging

main_ui = uic.loadUiType('wakark.ui')[0]

class Thread1(QThread):
    #parent = MainWidget을 상속 받음.
    def __init__(self, parent, main_, arg, opt):
        super().__init__(parent)
        self.main_ = main_
        self.arg = arg
        self.opt = opt

    def run(self):
        self.main_(self.arg, self.opt)
        self.parent.nextBtn.show()

class LogStringHandler(logging.Handler):

    def __init__(self, logText, progrssLabel, progressBar, totalProgressBar, resultText):
        super(LogStringHandler, self).__init__()
        self.logText = logText
        self.progressLabel = progrssLabel
        self.progressBar = progressBar
        self.totalProgressBar = totalProgressBar
        self.resultText = resultText

    def emit(self, record):
        if '진행 중' in record.getMessage():
            self.progressLabel.setText(record.getMessage())
        if '클립 다운로드 완료' in record.getMessage():
            self.progressBar.setValue(int(record.getMessage()[-3:]))
        if '전체 진행도' in record.getMessage():
            self.totalProgressBar.setValue(int(record.getMessage()[-3:]))
        if record.levelname == 'INFO':
            self.logText.append(record.getMessage())
        if record.levelname == 'WARNING':
            self.logText.append(record.getMessage())
            self.resultText.append(record.getMessage())
        if record.levelname == 'ERROR':
            self.resultText.append(record.getMessage())

class makeLog():
    def test(self, argument, option):
        if option == 'option1':
            logging.info(argument[option]['addressList'])
        else: 
            if option == 'option2':
                logging.info(argument[option]['board'])
            else :
                logging.info(argument[option]['streamer'])
            logging.info(argument[option]['user'])
            logging.info(argument[option]['startDate'])
            logging.info(argument[option]['endDate'])

        for k in range(10):
            logging.info('%d 단계 진행 중' % k)
            for i in range(51):
                logging.info('클립 다운로드 완료 %3d' % (i / 50 * 100))
                time.sleep(random.random()/100)
                if random.random() > 0.8:
                    logging.error('에러 %3d' % i)
            logging.info('전체 진행도 %3d' % ((k + 1) / 10 * 100))

class WindowClass(QMainWindow, main_ui) :

    def __init__(self, logger, main_, isFileExist) :
        super(WindowClass,self).__init__()

        # init UI
        self.setupUi(self)
        self.setFixedSize(800,600)
        self.setWindowTitle('WakArk')
        self.setWindowIcon(QIcon('./assets/icon.png'))

        self.stackedWidget.widget(0).setStyleSheet('QWidget#page {border-image: url(./assets/대문.png)}')
        self.stackedWidget.widget(1).setStyleSheet('QWidget#page_2 {border-image: url(./assets/background.png)}')

        # argument
        self.argument = {
            'option1': {'addressList' : []}, 
            'option2': {'board': '', 'user': '', 'startDate': '', 'endDate': ''}, 
            'option3': {'streamer': '', 'user': '', 'startDate': '', 'endDate': ''}
            }

        # prev/next Button
        self.prevBtn.clicked.connect(self.prevPage)
        self.nextBtn.clicked.connect(self.nextPage)
        
        # select option Button
        self.option1.clicked.connect(lambda: self.selectOption(0))
        self.option2.clicked.connect(lambda: self.selectOption(1))
        self.option3.clicked.connect(lambda: self.selectOption(2))

        # address setting
        self.addressLayout = self.verticalLayout_2        
        self.address.textChanged.connect(self.checkAddresses)
        self.removeBtn.clicked.connect(lambda: self.removeLine(self.horizontalLayout))
        self.addBtn.clicked.connect(lambda: self.addLine(self.addressLayout.count() - 1))


        # addItems for ComboBox
        self.board.addItems(['이세돌 엄마', '이세돌 | 핫클립', '고멤 | 핫클립', '우왁굳 | 핫클립', '이세돌 | 자유게시판', '이세돌 | 팬영상', '이세돌 | NEWS', '아 오늘 방송 못봤는데', '이세돌 오늘의 유튭각', '이세돌 컨텐츠용 게시판'])
        self.streamer.addItems(['우왁굳','아이네','징버거','릴파','주르르','고세구','비챤'])

        # set main_func
        self.main_ = main_

        # set logger
        self.logger = logger#logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(LogStringHandler(self.logText, self.progressLabel, self.progressBar, self.totalProgressBar, self.resultText))

        # set page flow
        self.pageList = [0,1,2,5,6]
        self.selectOption(0)

        # start page
        if isFileExist:
            QMessageBox.about(self,'안내','저장된 파일에서 클립을 불러옵니다.')
            f = open('wakark.cf','r',encoding='utf-8')
            a = f.read()
            self.pageList[2] = 1 + int(a[0])
            self.argument['option1']['YTMake'] = (a[1] == '1')
            self.argument['option1']['YTUpload'] = (a[2] == '1')
            self.argument['option2']['YTMake'] = (a[1] == '1')
            self.argument['option2']['YTUpload'] = (a[2] == '1')
            self.argument['option3']['YTMake'] = (a[1] == '1')
            self.argument['option3']['YTUpload'] = (a[2] == '1')
            self.argument['option1']['isVPN'] = (a[3] == '1')
            self.argument['option2']['isVPN'] = (a[3] == '1')
            self.argument['option3']['isVPN'] = (a[3] == '1')
            if not self.argument['option1']['YTMake']:
                self.YTMakecheckBox_2.toggle()
            if not self.argument['option1']['YTUpload']:
                self.YTUploadcheckBox_2.toggle()
            if not self.argument['option2']['YTMake']:
                self.YTMakecheckBox.toggle()
            if not self.argument['option2']['YTUpload']:
                self.YTUploadcheckBox.toggle()
            if not self.argument['option1']['isVPN']:
                self.isVPNcheckBox.toggle()
            if not self.argument['option2']['isVPN']:
                self.isVPNcheckBox_2.toggle()
            if not self.argument['option3']['isVPN']:
                self.isVPNcheckBox_3.toggle()
            f.close()

        self.stackedWidget.setCurrentIndex(5 if isFileExist else 0)
        self.stackedWidget.currentChanged.connect(self.pageUpdated)
        self.show()
        self.pageUpdated()





    def prevPage(self):
        currentIndex = self.pageList.index(self.stackedWidget.currentIndex())

        if currentIndex > 0: 
            prevIndex = self.pageList[currentIndex - 1]
            self.stackedWidget.setCurrentIndex(prevIndex)

    def nextPage(self):
        currentIndex = self.pageList.index(self.stackedWidget.currentIndex())

        if currentIndex < 4:
            if currentIndex == 2:
                if not self.isValid(): return
                
            nextIndex = self.pageList[currentIndex + 1]
            self.stackedWidget.setCurrentIndex(nextIndex)

        elif currentIndex == 4:
            self.close()

    def pageUpdated(self):
        index = self.stackedWidget.currentIndex()

        # show/hide button
        if index == 0 or index == 6:
            self.prevBtn.hide()
            self.nextBtn.show()
        
        elif index == 5:
            self.prevBtn.hide()
            self.nextBtn.hide()
            
        else :
            self.prevBtn.show()
            self.nextBtn.show()

        # set button Text
        if 2 <= index <= 4:
            self.nextBtn.setText('완료')
        
        elif index == 6:
            self.nextBtn.setText('종료')
        
        else :
            self.nextBtn.setText('다음')

        # start loading
        if index == 5:
            self.startLoad()

    def selectOption(self, index):
        self.pageList[2] = index + 2

        #Main_image = self.stackedWidget.widget(0).findChildren(QLabel)[0]

        #pixmap = QPixmap('./assets/title.png')
        #Main_image.setPixmap(pixmap.scaledToWidth(640))


        for i in range(3):
            optionBtn = self.stackedWidget.widget(1).findChildren(QPushButton)[i]
            if i == index:
                optionBtn.setStyleSheet('border: 1px solid #00b4d8; background-image: url(./assets/option%d.png)' % (i + 1))
            else:
                optionBtn.setStyleSheet('border: 1px solid #d9d9d9; background-image: url(./assets/option%d.png)' % (i + 1))

        

    def addLine(self, index, text = ''):
        line = QHBoxLayout()

        lineEdit = QLineEdit(text)
        lineEdit.setPlaceholderText('게시글 주소')
        lineEdit.textChanged.connect(self.checkAddresses)

        pushButton = QPushButton('삭제')
        pushButton.clicked.connect(lambda: self.removeLine(line))

        line.addWidget(lineEdit)
        line.addWidget(pushButton)

        self.addressLayout.insertLayout(index, line)

    def removeLine(self, line):
        lineEdit = line.itemAt(0).widget()
        pushButton = line.itemAt(1).widget()
        lineEdit.deleteLater()
        pushButton.deleteLater()
        self.addressLayout.removeItem(line)

    def checkAddresses(self):
        for i in range(self.addressLayout.count() - 1):
            line = self.addressLayout.itemAt(i)
            lineEdit = line.itemAt(0).widget()
            addressList = lineEdit.text().split('\n')
            passList = []
            
            for address in addressList:
                if len(address) < 38:
                    continue
                if address[:38] != 'https://cafe.naver.com/steamindiegame/' and address[:37] != 'http://cafe.naver.com/steamindiegame/': 
                    continue
                passList.append(address)
            
            for j in range(len(passList)):
                if j == 0:
                    lineEdit.setText(passList[j])
                else:
                    self.addLine(self.addressLayout.indexOf(line) + j, passList[j])

    def isValid(self):
        # option1
        if self.pageList[2] == 2:
            lineEditList = self.stackedWidget.widget(2).findChildren(QLineEdit)
            for lineEdit in lineEditList:
                if lineEdit.text()[:38] != 'https://cafe.naver.com/steamindiegame/' and lineEdit.text()[:37] != 'http://cafe.naver.com/steamindiegame/':
                    QMessageBox.about(self,'경고','올바른 주소를 입력해주세요.')
                    return False

        # option2
        if self.pageList[2] == 3:
            if self.userName.text() == '':
                QMessageBox.about(self,'경고','글 작성자를 입력해주세요.')
                return False
            if self.startDate.date() > self.endDate.date():
                QMessageBox.about(self,'경고','시작 날짜가 끝 날짜보다 앞서야 합니다.')
                return False

        # option3
        elif self.pageList[2] == 4:
            if self.userName_2.text() == '':
                QMessageBox.about(self,'경고','트위치 닉네임을 입력해주세요.')
                return False
            if self.startDate_2.date() > self.endDate_2.date():
                QMessageBox.about(self,'경고','시작 날짜가 끝 날짜보다 앞서야 합니다.')
                return False

        return True

    def makeArgument(self):
        # option1
        if self.pageList[2] == 2:
            self.argument['option1']['addressList'] = [lineEdit.text() for lineEdit in self.stackedWidget.widget(2).findChildren(QLineEdit)]
            self.argument['option1']['YTMake'] = self.YTMakecheckBox_2.isChecked()
            self.argument['option1']['YTUpload'] = self.YTUploadcheckBox_2.isChecked()
            self.argument['option1']['isVPN'] = self.isVPNcheckBox.isChecked()

        # option2
        elif self.pageList[2] == 3:
            self.argument['option2']['board'] = self.board.currentText()
            self.argument['option2']['user'] = self.userName.text()
            self.argument['option2']['startDate'] = self.startDate.text()
            self.argument['option2']['endDate'] = self.endDate.text()
            self.argument['option2']['YTMake'] = self.YTMakecheckBox.isChecked()
            self.argument['option2']['YTUpload'] = self.YTUploadcheckBox.isChecked()
            self.argument['option2']['isVPN'] = self.isVPNcheckBox_2.isChecked()

        # option3
        else :
            self.argument['option3']['streamer'] = self.streamer.currentText()
            self.argument['option3']['user'] = self.userName_2.text()
            self.argument['option3']['startDate'] = self.startDate_2.text()
            self.argument['option3']['endDate'] = self.endDate_2.text()
            self.argument['option3']['YTMake'] = False
            self.argument['option3']['YTUpload'] = False
            self.argument['option3']['isVPN'] = self.isVPNcheckBox_3.isChecked()

    def startLoad(self):
        self.makeArgument()

        #makeLog().test(self.argument,'option%d' % (self.pageList[2] - 1))
        self.main_(self.argument,'option%d' % (self.pageList[2] - 1))
        self.nextBtn.show()
        #x = Thread1(self, self.main_, self.argument,'option%d' % (self.pageList[2] - 1))
        #x.start()
        

        

if __name__ == "__main__" :
    app = QApplication(sys.argv)

    myWindow = WindowClass(logging.getLogger(),'',False)
    myWindow.main_ = makeLog().test
    #myWindow.show()

    app.exec_()