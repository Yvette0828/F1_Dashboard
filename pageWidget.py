from PyQt6 import QtWidgets, uic, QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QGraphicsPixmapItem, QGraphicsView, QMessageBox, QGraphicsScene
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QPainter, QImage, QColor, QDesktopServices
from PyQt6.QtCore import QFile, Qt, QUrl
import pyqtgraph as pg
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.offline import plot
from plotly.io import to_image
import plotly.io as pio
import sys
import os
 
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
 
        #Load the UI Page by PyQt6
        uic.loadUi('hw_pageWidget.ui', self)
        self.tabWidget.setCurrentIndex(0)
        self.setWindowTitle('Homework_pageWidges')

        # Signals
        # Tab 1
        self.seasons = pd.read_csv('seasons.csv')
        self.season_year_data = self.seasons['Year'].unique()
        self.season_driver_data = self.seasons['Driver'].unique()
        self.season_comboBox.addItems(self.season_driver_data)
        self.go_button.clicked.connect(self.update_plot)
        self.update_plot()

        # Tab 2
        self.constructors = pd.read_csv('constructors.csv')
        self.constructors_year = ['2019', '2020', '2021']
        self.constructors_name = list(self.constructors['Constructors'].unique())
        self.year_comboBox.addItems(self.constructors_year)
        self.year_comboBox.currentIndexChanged.connect(self.update_pie)
        self.update_pie()

        # Tab 3
        self.file_src = "../images/F1_driver/"
        self.picName = sorted(os.listdir(self.file_src), key=lambda x: os.path.getmtime(os.path.join('../images/F1_driver/', x))) # 按照修改時間排序
        # print(self.picName)
        self.imgageCount = len(self.picName)
        self.driver_comboBox.addItems(self.seasons['Driver'].unique())
        self.driver_comboBox.currentIndexChanged.connect(self.showImg)
        self.current_page = 0
        self.count = 0 # 用來計算 button 被點擊次數
        self.previous_page.clicked.connect(self.go_prev)
        self.next_page.clicked.connect(self.go_next)
        self.first_page.clicked.connect(self.go_first)
        self.last_page.clicked.connect(self.go_last)
        self.url_btn.clicked.connect(self.go_website)

    # Slots
    # Tab 1
    def update_plot(self):
        self.seasonWidget.clear() # clear current plot before plotting
        x = self.season_year_data
        driver_name = self.season_comboBox.currentText()
        print(driver_name)
        y = list(self.seasons.loc[self.seasons['Driver'] == driver_name, 'Points'])
        current_constructor = self.seasons.loc[self.seasons['Driver'] == driver_name, 'Constructor'].unique().tolist()
        current_constructor_str = ", ".join(current_constructor)
        print(y)
        # titlename = str(driver_name) + "'s Points in 2018-2022"
        if driver_name in ['MAX', 'PER']:
            pen = pg.mkPen(color=QColor(42, 90, 186), width=3)
        elif driver_name in ['LEC', 'SAI']:
            pen = pg.mkPen(color=QColor(244, 0, 41), width=3)
        elif driver_name in ['HAM', 'RUS']:
            pen = pg.mkPen(color=QColor(93, 204, 178), width=3)
        elif driver_name in ['RIC']:
            pen = pg.mkPen(color=QColor(239, 107, 26), width=3)
        curve = pg.PlotCurveItem(x, y, pen=pen, name='Driver Points')
        self.seasonWidget.addItem(curve)
        self.current_constructor.setText(current_constructor_str)

        # Add a TextItem for each point on the line
        for i in range(len(x)):
            textItem = pg.TextItem(str(round(y[i], 2)))
            textItem.setParentItem(curve)
            textItem.setPos(x[i], y[i])
            textItem.setColor(pen.color().name())

        self.seasonWidget.setBackground('transparent')
        # self.seasonWidget.setTitle(titlename, color="#AB3B3A", size="16pt")
        styles = {'color':'black', 'font-size':'11px'}
        self.seasonWidget.setLabel('left', 'Points', **styles)
        self.seasonWidget.setLabel('bottom', 'Year', **styles)

    # Tab 2
    def update_pie(self):
        self.constructorsWidget.scene().clear() # clear current plot before plotting
        selected_year = int(self.year_comboBox.currentText())
        selected_df = self.constructors[self.constructors['Year'] == selected_year] # 直接使用 selected_year 轉成整數後進行篩選
        constructors_points = selected_df['Points'].tolist()
        labels = selected_df['Constructors'].tolist()
        fig = px.pie(selected_df, values=constructors_points, names=labels, color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(width=620, height=590)
        pixmap = QPixmap()
        pixmap.loadFromData(fig.to_image(format='svg', scale=5)) # 將 plotly 畫出的圓餅圖存成圖檔
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.constructorsWidget.scene().addItem(pixmap_item)
        scene_rect = self.constructorsWidget.scene().sceneRect()
        scene_width = int(scene_rect.width())
        scene_height = int(scene_rect.height())
        scaled_pixmap = pixmap.scaled(scene_width, scene_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        pixmap_item.setPixmap(scaled_pixmap)
        pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.constructorsWidget.setBackground('transparent') # 設定 GraphicView 背景為透明
        self.constructorsWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # 使用 ScrollBarAlwaysOff 代替 ScrollBarPolicy.ScrollBarAlwaysOff
        self.constructorsWidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # 使用 ScrollBarAlwaysOff 代替 ScrollBarPolicy.ScrollBarAlwaysOff
        self.constructorsWidget.setRenderHint(QPainter.RenderHint.Antialiasing, on=False) # 簡化 setRenderHint 設定
        self.constructorsWidget.setDragMode(QGraphicsView.DragMode.ScrollHandDrag) # 簡化 setDragMode 設定
        self.constructorsWidget.fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio) # 讓圖片保持比例的同時充滿 scene
        self.constructorsWidget.setSceneRect(pixmap_item.boundingRect()) # 設定 scene 範圍為圖片範圍
    
        # 於 tableView 顯示選取年度之資料
        headers = ['Year', 'Constructors', 'Points']
        data = []
        for index, row in self.constructors.sort_values(by='Points', ascending=False).iterrows():
            row_data = dict(zip(headers, row)) # 將row_data轉換為字典
            if row_data['Year'] == selected_year:
                # item1 = QStandardItem(str(row_data['Year']))
                item2 = QStandardItem(str(row_data['Constructors']))
                item3 = QStandardItem(str(row_data['Points']))
                data.append([item2, item3])
        headers = ['Constructors', 'Points']
        model = QStandardItemModel() 
        model.setHorizontalHeaderLabels(headers)
        self.tableView.setModel(model)
        self.tableView.setStyleSheet("background-color: transparent;")
        for row in data:
            model.appendRow(row)
        self.tableView.setColumnWidth(0, 150)

    # Tab 3
    def go_website(self):
        self.current_page = int(self.driver_comboBox.currentIndex())
        if self.current_page == 0:
            url = "https://www.formula1.com/en/drivers/max-verstappen.html"
        if self.current_page == 1:
            url = "https://www.formula1.com/en/drivers/charles-leclerc.html"
        if self.current_page == 2:
            url = "https://www.formula1.com/en/drivers/sergio-perez.html"
        if self.current_page == 3:
            url = "https://www.formula1.com/en/drivers/george-russell.html"
        if self.current_page == 4:
            url = "https://www.formula1.com/en/drivers/carlos-sainz.html"
        if self.current_page == 5:
            url = "https://www.formula1.com/en/drivers/lewis-hamilton.html"
        if self.current_page == 6:
            self.url_btn.setText("RIC is not drive for F1 in 2023 so website not found.")
        # url = "https://www.formula1.com/en/drivers.html"
        QDesktopServices.openUrl(QUrl(url))

    def showImg(self):
        self.current_page = int(self.driver_comboBox.currentIndex())
        self.change_image(self.current_page)

    def go_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.change_image(self.current_page)
        else:
            self.show_warning("This is already the first page.")

    def go_next(self):
        if self.current_page < self.imgageCount - 1:
            self.current_page += 1
            self.change_image(self.current_page)
        else:
            self.show_warning("This is already the last page.")

    def go_first(self):
        if self.current_page == 0:
            self.show_warning("This is already the first page.")
        else:
            self.current_page = 0
            self.count += 1
            self.change_image(self.current_page)
            if self.count > 1:
                self.show_warning("This is already the first page.")
                self.count = 0

    def go_last(self):
        if self.current_page == 6:
            self.show_warning("This is already the last page.")
        else:
            self.current_page = self.imgageCount - 1
            self.count += 1
            self.change_image(self.current_page)
            if self.count > 1:
                self.show_warning("This is already the last page.")
                self.count = 0

    def change_image(self, page):
        self.image_label.setPixmap(QPixmap(u"../images/F1_driver/" + self.picName[page]))
        self.label_cap.setText(self.picName[page][:3]) # set Label text
        self.driver_comboBox.setCurrentText(self.picName[page][:3])

    def show_warning(self, text):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Warning")
        dlg.setGeometry(self.frameGeometry().topLeft().x() + self.frameGeometry().width() / 2 - dlg.width() / 2,
                self.frameGeometry().topLeft().y() + self.frameGeometry().height() / 2 - dlg.height() / 2,
                dlg.width(), dlg.height())
        QMessageBox.warning(dlg, "Warning", text, QMessageBox.StandardButton.Ok)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()