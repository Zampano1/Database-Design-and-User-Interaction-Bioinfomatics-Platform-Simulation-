#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apr 2019

@author: Li McCarthy, Pengcheng Wu
"""


import MySQLdb
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib import pyplot as plt
from PyQt5.QtCore import QSize

"""Just for the time being, store the acceptable username and password.
#It would be interesting to store the encrypted username and password, but it is not a priority (out of the data domain)."""

host = "localhost"
database = "cmap_project"
admin_username = "admin"
admin_password = "password"

     
class MainWindow(QMainWindow): 
    def __init__(self):
        super(MainWindow, self).__init__()
        self.left = 300
        self.top = 200
        self.width = 800
        self.height = 600
        self.title = "Perturbation Comprendium"
        self.login_state =  -1
        self.username = None
        self.password  = None
        self.start_ui()
        self.literature_import_widgets= []
        self.perturbation_show_widgets = []
        self.perturbation_all_widgets = []
        self.disease_all_widgets = []
        self.gene_all_widgets = []
        self.cell_line_all_widgets = []
        self.delete_record_all_widgets = []
        self.alter_record_all_widgets = []
        self.gene_info_all_widgets = []
        self.output = None

        self.choices = None

    #Set up login
    def start_ui(self):
        self.back_button = None
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #Set central widget and layout.
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setObjectName("main")

        self.main_widget.setStyleSheet("QWidget#main {background-image: url(resources/pexels-photo-256262.jpg)}")

        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_widget.setLayout(self.layout)
        self.launch_screen()

    #Launch screen directly from open
    def launch_screen(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None

        #Define the buttons.
        self.login_pw = QtWidgets.QPushButton("Log in with account", self)
        self.login_pw.setMaximumWidth(200)
        self.login_guest = QtWidgets.QPushButton("Use as guest", self)
        self.login_guest.setMaximumWidth(200)

        #Hook up the buttons.
        self.login_pw.setCheckable(True)
        self.login_guest.setCheckable(True)

        self.layout.addWidget(self.login_pw)
        self.layout.addWidget(self.login_guest)

        self.login_pw.clicked.connect(self.login_screen_state)
        self.login_guest.clicked.connect(self.read_only_state)

        self.show()

    def login_to_launch(self):
        self.hide_all()
        self.enter_login_un.deleteLater()
        self.enter_login_password.deleteLater()
        self.login_submit.deleteLater()
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.launch_screen()

    def guest_to_launch(self):
        self.hide_all()
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.launch_screen()

    def login_screen_state(self):
        self.hide_all()
        if self.login_pw != None:
            self.login_pw.deleteLater()
            self.login_guest.deleteLater()
            self.login_pw = None
            self.login_guest = None
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None

        self.enter_login_un = QtWidgets.QLineEdit(self)
        self.enter_login_un.setPlaceholderText("Enter username")
        self.enter_login_password = QtWidgets.QLineEdit(self)
        self.enter_login_password.setPlaceholderText("Enter password")

        self.enter_login_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_submit = QtWidgets.QPushButton("Submit")
        self.login_submit.setCheckable(True)

        self.layout.addWidget(self.enter_login_un, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.enter_login_password, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.login_submit, QtCore.Qt.AlignTop)

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        self.back_button.clicked.connect(self.login_to_launch)
        self.layout.addWidget(self.back_button)

        #Check username and password.

        self.login_submit.clicked.connect(self.submit_password)


    def submit_password(self):
        un = self.enter_login_un.text()
        pw = self.enter_login_password.text()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Please re-enter username and password")

        if un == admin_username and pw == admin_password:
            self.login_state = 1
            self.read_write_state()
        else:
            self.login_submit.toggle()
            ret = msg.exec_()


    def read_only_state(self):
        self.hide_all()
        if self.login_pw != None:
            self.login_pw.deleteLater()
            self.login_guest.deleteLater()
            self.login_pw = None
            self.login_guest = None
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.setWindowTitle("Perturbation Comprendium - Read only")
        self.login_state = 0
        self.row_index = 0

        self.hide_all()
        self.connect_database()
        self.choices = QComboBox()
        self.choices.addItem("Choose option")
        self.choices.addItem("Find a perturbation")
        self.choices.addItem("Plot perturbation frequency")
        self.choices.addItem("Get all information on a perturbation")
        self.choices.addItem("Get all information on a gene")
        self.choices.addItem("Get all information on a disease")
        self.choices.addItem("Get all information on a cell line")
        self.choices.addItem("Get all information connected to a gene")
        self.layout.addWidget(self.choices)
        self.perturbation_show_widgets = []

        self.connect_database()

        

        self.choices.currentTextChanged.connect(self.control_combobox)

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        self.back_button.clicked.connect(self.guest_to_launch)
        self.layout.addWidget(self.back_button)




    def read_write_to_launch(self):

        if self.choices != None:
            self.choices.deleteLater()
            self.choices = None

        self.disconnect_database()
        self.login_screen_state()

      
        
    def read_write_state(self):
        self.hide_all()

        self.setWindowTitle("Perturbation Comprendium - Read/Write")
        self.login_state = 1
        self.row_index = 0
        self.hide_all()

        #Control what’s present on the screen.
        if self.enter_login_un != None:
            self.enter_login_un.deleteLater()
            self.enter_login_un = None
            self.enter_login_password.deleteLater()
            self.enter_login_password = None
            self.login_submit.deleteLater()
            self.login_submit = None
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        if self.choices != None:
            self.choices.deleteLater()
            self.choices = None
        if self.literature_import_widgets != None:
            for widget in self.literature_import_widgets:
                widget.deleteLater()
            self.literature_import_widgets = None

        self.connect_database()
        self.choices = QComboBox()
        self.choices.addItem("Choose option")
        self.choices.addItem("Add a publication")
        self.choices.addItem("Find a perturbation")
        self.choices.addItem("Plot perturbation frequency")
        self.choices.addItem("Get all information on a perturbation")
        self.choices.addItem("Get all information on a gene")
        self.choices.addItem("Get all information on a disease")
        self.choices.addItem("Get all information on a cell line")
        self.choices.addItem("Get all information connected to a gene")
        self.choices.addItem("Delete a record")
        self.choices.addItem("Alter a record")
        self.layout.addWidget(self.choices)

        #Widgets for showing perturbation
        self.perturbation_show_widgets = []
        self.literature_import_widgets = []
        #Here’s everything that’s necessary for the literature input.
        title = QLineEdit(self)
        title.setPlaceholderText("Title (Required)")
        self.literature_import_widgets.append(title)
        author = QLineEdit(self)
        author.setPlaceholderText("Author (Required)")
        self.literature_import_widgets.append(author)
        journal = QLineEdit(self)
        journal.setPlaceholderText("Journal (Required)")
        self.literature_import_widgets.append(journal)
        perturbation = QLineEdit(self)
        perturbation.setPlaceholderText("Perturbation")
        self.literature_import_widgets.append(perturbation)
        gene = QLineEdit(self)
        gene.setPlaceholderText("Gene")
        self.literature_import_widgets.append(gene)
        disease = QLineEdit(self)
        disease.setPlaceholderText("Disease")
        self.literature_import_widgets.append(disease)
        cell_line = QLineEdit(self)
        cell_line.setPlaceholderText("Cell line")
        self.literature_import_widgets.append(cell_line)
        self.literature_import_widgets.append(QPushButton("Commit changes", self))

        #Add in the widgets for literature import option.  
        for widget in self.literature_import_widgets:
            self.layout.addWidget(widget)
            widget.hide()


        query_p_field = QLineEdit(self)
        query_p_field.setPlaceholderText("Enter perturbation name")
        self.perturbation_show_widgets.append(query_p_field)
        self.perturbation_show_widgets.append(QPushButton("Query Perturbation", self))
        self.perturbation_show_widgets.append(QTableWidget(100,3, self))

        header = QTableWidgetItem("Queried perturbation")
        self.perturbation_show_widgets[2].setHorizontalHeaderItem(0, header)
        header2 = QTableWidgetItem("Query result")
        self.perturbation_show_widgets[2].setHorizontalHeaderItem(1, header2)
        header3 = QTableWidgetItem("Details")
        self.perturbation_show_widgets[2].setHorizontalHeaderItem(2, header3)

        display =   self.perturbation_show_widgets[2].horizontalHeader()
        display.setSectionResizeMode(QHeaderView.Stretch)

        for widget in self.perturbation_show_widgets:
            self.layout.addWidget(widget)
            widget.hide()

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        self.back_button.clicked.connect(self.read_write_to_launch)
        self.layout.addWidget(self.back_button)


        self.literature_import_widgets[7].setCheckable(True)
        self.literature_import_widgets[7].clicked.connect(self.add_literature)

        self.choices.currentTextChanged.connect(self.control_combobox)

    def handle_nulls(self, title):
        if title == "":
            title = "null"
        else:
            title = "\"" + title + "\""
        return title

    def add_literature(self):
        #Get fields from literature_import_widget.
        title = self.literature_import_widgets[0].text()
        title = self.handle_nulls(title)
        author = self.literature_import_widgets[1].text()
        author = self.handle_nulls(author)
        journal = self.literature_import_widgets[2].text()
        journal = self.handle_nulls(journal)
        perturbation = self.literature_import_widgets[3].text()
        perturbation = self.handle_nulls(perturbation)
        gene = self.literature_import_widgets[4].text()
        gene = self.handle_nulls(gene)
        disease = self.literature_import_widgets[5].text()
        disease = self.handle_nulls(disease)
        cell_line = self.literature_import_widgets[6].text()
        cell_line = self.handle_nulls(cell_line)

        if title == "" or author == "" or journal == "":
            msg = QMessageBox()
            msg.setWindowTitle("Entry error")
            msg.setText("At least title, quthor, and journal are required")
            ret = msg.exec_()
            self.read_write_state()

        else:
            try:
                cursor = self.db.cursor()
                lit_query = ("CALL insert_literature(" + title + "," + author + "," + journal+ ","+ disease+ ","+ cell_line+","+ gene+ ","+ perturbation+ ");")
                cursor.execute(lit_query)
                cursor.close() 
                self.db.commit()
            except:
                msg = QMessageBox()
                msg.setWindowTitle("Entry error")
                msg.setText("Duplicate entry")
                ret = msg.exec_()
                self.literature_import_widgets[0].clear()
                self.literature_import_widgets[1].clear()
                self.literature_import_widgets[2].clear()
                self.literature_import_widgets[3].clear()
                self.literature_import_widgets[4].clear()
                self.literature_import_widgets[5].clear()
                self.literature_import_widgets[6].clear()

                self.read_write_state()

        self.literature_import_widgets[0].clear()
        self.literature_import_widgets[1].clear()
        self.literature_import_widgets[2].clear()
        self.literature_import_widgets[3].clear()
        self.literature_import_widgets[4].clear()
        self.literature_import_widgets[5].clear()
        self.literature_import_widgets[6].clear()

    def express_perturbation_info(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None

        query_p_field = QLineEdit(self)
        query_p_field.setPlaceholderText("Enter perturbation name")
        self.perturbation_show_widgets.append(query_p_field)
        self.perturbation_show_widgets.append(QPushButton("Query Perturbation", self))
        self.perturbation_show_widgets.append(QTableWidget(100,3, self))

        header = QTableWidgetItem("Queried perturbation")
        self.perturbation_show_widgets[2].setHorizontalHeaderItem(0, header)
        header2 = QTableWidgetItem("Query result")
        self.perturbation_show_widgets[2].setHorizontalHeaderItem(1, header2)
        header3 = QTableWidgetItem("Details")
        self.perturbation_show_widgets[2].setHorizontalHeaderItem(2, header3)

        display =   self.perturbation_show_widgets[2].horizontalHeader()
        display.setSectionResizeMode(QHeaderView.Stretch)

        for widget in self.perturbation_show_widgets:
            self.layout.addWidget(widget)

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        self.back_button.clicked.connect(self.guest_to_launch)
        self.layout.addWidget(self.back_button)

        for widget in self.perturbation_show_widgets:
            widget.show()

        self.perturbation_show_widgets[1].clicked.connect(self.query_perturbation)


    def query_perturbation(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None

        cursor = self.db.cursor()
        query = self.perturbation_show_widgets[0].text()
        if query != "":
            query_text = "CALL whether_small_molecule(\"" + query +"\"," + "@out" + ");"
            cursor.execute(query_text)
            ret = cursor.fetchall()
            identity = ret[0][0]
            if identity == 0:
                label = "Perturbation is not in database"
            elif identity == 1:
                label = "Perturbation is in the database, not a small molecule compound"
            elif identity == 2:
                label = "Perturbation is a small molecule compound, details are in small molecule table"
                query_2 = "CALL fetch_chemical_formula(\"" + query +"\");"
                cursor.execute(query_2)
                ret = cursor.fetchall()
                self.perturbation_show_widgets[2].setItem(self.row_index, 2, QTableWidgetItem("Chemical formula: " + ret[0][0]))
            else:
                label = "Perturbation is a small molecule, but we do not have its details"


            self.perturbation_show_widgets[2].setItem(self.row_index, 0, QTableWidgetItem(query))
            self.perturbation_show_widgets[2].setItem(self.row_index, 1, QTableWidgetItem(label))
        
            self.row_index += 1

            cursor.close()
            self.db.commit()

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        if self.login_state == 0:
            self.back_button.clicked.connect(self.read_only_state)
        else:
            self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button)  


  
    def plot_pert_freq(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None

        self.output = None

        cursor = self.db.cursor()
        query_text = "CALL pert_type_plot();"
        cursor.execute(query_text)
        ret = cursor.fetchall()
        cursor.close()
        labels = []
        numbers = []


        total = 0
        for index in ret:
            if index[0] != "":
                    labels.append(str(index[0]))
                    numbers.append(index[1])
                    total += index[1]

        final_labels = []
        final_numbers = []

        for l in range(0, len(labels)):
            if numbers[l]/total >= .01:
                final_labels.append(labels[l])
                final_numbers.append(numbers[l])
            
        fig1, ax1 = plt.subplots()
        ax1.pie(final_numbers, labels=final_labels, textprops={'size': 'smaller'}, autopct='%3.0f%%',pctdistance=0.85)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()

        plt.show()

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        if self.login_state == 0:
            self.back_button.clicked.connect(self.read_only_state)
        else:
            self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button)  
        
    def print_pert_info_2(self):
        cursor = self.db.cursor()
        name = self.perturbation_all_widgets[0].currentText()
        if name != "":
            query_text = "CALL "+ "search_pert(\""+ name +  "\");"
            cursor.execute(query_text)
            ret = cursor.fetchall()
            output = ""
            for index in ret:
                output += "ID: " + index[0] + "\n"
                output += "Name: " + index[1] + "\n"
                output += "Type: " + index[2] + "\n\n"

            self.perturbation_all_widgets[2].insertPlainText(output)

        cursor.close()
        self.db.commit()



    def print_pert_info(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        #draw a text box, combo box.
        self.perturbation_all_widgets = []

        #Combo box that pre-loads all perturbations.
        perturbation_box = QComboBox()
        cursor = self.db.cursor()
        query_text = "SELECT pert_iname FROM perturbation;"
        cursor.execute(query_text)
        ret = cursor.fetchall()
        cursor.close()
        for index in ret:
            if index[0] != "":
                perturbation_box.addItem(index[0])

        pert_go_button = QtWidgets.QPushButton("Search")

        self.perturbation_all_widgets.append(perturbation_box)
        self.perturbation_all_widgets.append(pert_go_button)
        self.perturbation_all_widgets.append(QtWidgets.QTextEdit())

        self.perturbation_all_widgets[1].setCheckable(True)
        self.perturbation_all_widgets[1].clicked.connect(self.print_pert_info_2)


        for widget in self.perturbation_all_widgets:
            self.layout.addWidget(widget)

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        if self.login_state == 0:
            self.back_button.clicked.connect(self.read_only_state)
        else:
            self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button)  
        
    def print_disease_info_2(self):
        cursor = self.db.cursor()
        name = self.disease_all_widgets[0].currentText()
        query_text = "CALL "+ "search_disease(\""+ name +  "\");"
        cursor.execute(query_text)
        ret = cursor.fetchall()
        output = ""
        for index in ret:
            output += "Name: " + index[0] + "\n"
            output += "Description: " + index[1] + "\n\n"

        self.disease_all_widgets[2].insertPlainText(output)

        cursor.close()
        self.db.commit()


    def print_disease_info(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.disease_all_widgets = []
        
        disease_box = QComboBox()
        cursor = self.db.cursor()
        query_text = "SELECT disease_name FROM disease"
        cursor.execute(query_text)
        ret = cursor.fetchall()
        cursor.close()
        for index in ret:
            if index[0] != "":
                disease_box.addItem(index[0])

        dis_go_button = QtWidgets.QPushButton("Search")

        self.disease_all_widgets.append(disease_box)
        self.disease_all_widgets.append(dis_go_button)
        self.disease_all_widgets.append(QtWidgets.QTextEdit())

        self.disease_all_widgets[1].setCheckable(True)
        self.disease_all_widgets[1].clicked.connect(self.print_disease_info_2)

        for widget in self.disease_all_widgets:
            self.layout.addWidget(widget)


        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        if self.login_state == 0:
            self.back_button.clicked.connect(self.read_only_state)
        else:
            self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button) 

    def print_gene_info_2(self):
        cursor = self.db.cursor()
        name = self.gene_all_widgets[0].currentText()
        query_text = "SELECT * FROM gene WHERE gene_symbol =" + "\"" + name + "\";"

        cursor.execute(query_text)
        ret = cursor.fetchall()
        output = ""
        for index in ret:
            output += "Gene ID: " + str(index[0]) + "\n"
            output += "Gene Symbol: " + str(index[1]) + "\n"
            output += "Gene Title: " + str(index[2]) + "\n"
            output += "is lm: " + str(index[3]) + "\n"
            output += "is bing: " + str(index[4]) + "\n\n"

        self.gene_all_widgets[2].insertPlainText(output)

        cursor.close()
        self.db.commit()

    def print_gene_info(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.gene_all_widgets = []
        
        gene_box = QComboBox()
        cursor = self.db.cursor()
        query_text = "SELECT gene_symbol FROM gene"
        cursor.execute(query_text)
        ret = cursor.fetchall()
        cursor.close()
        for index in ret:
            if index[0] != "":
                gene_box.addItem(str(index[0]))

        gene_go_button = QtWidgets.QPushButton("Search")

        self.gene_all_widgets.append(gene_box)
        self.gene_all_widgets.append(gene_go_button)
        self.gene_all_widgets.append(QtWidgets.QTextEdit())

        self.gene_all_widgets[1].setCheckable(True)
        self.gene_all_widgets[1].clicked.connect(self.print_gene_info_2)

        for widget in self.gene_all_widgets:
            self.layout.addWidget(widget)


        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        if self.login_state == 0:
            self.back_button.clicked.connect(self.read_only_state)
        else:
            self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button) 

    def all_gene_info_2(self):
        cursor = self.db.cursor()
        name = self.gene_info_all_widgets[0].text()
        query_text = "CALL retrieve_info_by_gene(\"" + name + "\");"

        cursor.execute(query_text)
        ret = cursor.fetchall()
        output = ""
        for index in ret:
            output += "Gene Name: " + str(index[0]) + "\n"
            output += "Disease name: " + str(index[1]) + "\n"
            output += "Perturbation: " + str(index[2]) + "\n"
            output += "Cell line: " + str(index[3]) + "\n"
            output += "Literature: " + str(index[4]) + "\n\n"

        self.gene_info_all_widgets[2].insertPlainText(output)

        cursor.close()
        self.db.commit()


    def all_gene_info(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.gene_info_all_widgets = []
        gene_name = QLineEdit(self)
        gene_name.setPlaceholderText("Enter gene symbol")

        gene_info_go_button = QtWidgets.QPushButton("Search")

        self.gene_info_all_widgets.append(gene_name)
        self.gene_info_all_widgets.append(gene_info_go_button)
        self.gene_info_all_widgets.append(QtWidgets.QTextEdit())

        self.gene_info_all_widgets[1].setCheckable(True)
        self.gene_info_all_widgets[1].clicked.connect(self.all_gene_info_2)

        for widget in self.gene_info_all_widgets:
            self.layout.addWidget(widget)


        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        if self.login_state == 0:
            self.back_button.clicked.connect(self.read_only_state)
        else:
            self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button) 




    def print_cell_line_info_2(self):
        cursor = self.db.cursor()
        name = self.cell_line_all_widgets[0].currentText()
        query_text = "CALL search_cell_line(" + "\"" + name + "\");"

        cursor.execute(query_text)
        ret = cursor.fetchall()
        output = ""
        for index in ret:
            output += "Cell id: " + str(index[0]) + "\n"
            output += "Cell type: " + str(index[1]) + "\n"
            output += "Base Cell ID: " + str(index[2]) + "\n"
            output += "Precursor Cell ID: " + str(index[3]) + "\n"
            output += "Modification: " + str(index[4]) + "\n"
            output += "Sample type: " + str(index[5]) + "\n"
            output += "Primary site: " + str(index[6]) + "\n"
            output += "Subtype: " + str(index[7]) + "\n"
            output += "Original growth pattern: " + str(index[8]) + "\n"
            output += "Provider catalog id: " + str(index[9]) + "\n"
            output += "Original source vendor: " + str(index[10]) + "\n"
            output += "Donor age: " + str(index[11]) + "\n"
            output += "Donor sex: " + str(index[12]) + "\n"
            output += "Donor ethnicity: " + str(index[13]) + "\n\n"

        self.cell_line_all_widgets[2].insertPlainText(output)

        cursor.close()
        self.db.commit()

    def print_cell_line_info(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.cell_line_all_widgets = []
        
        cell_line_box = QComboBox()
        cursor = self.db.cursor()
        query_text = "SELECT cell_id FROM cell_line"
        cursor.execute(query_text)
        ret = cursor.fetchall()
        cursor.close()
        for index in ret:
            if index[0] != "":
                cell_line_box.addItem(str(index[0]))

        cell_line_go_button = QtWidgets.QPushButton("Search")

        self.cell_line_all_widgets.append(cell_line_box)
        self.cell_line_all_widgets.append(cell_line_go_button)
        self.cell_line_all_widgets.append(QtWidgets.QTextEdit())

        self.cell_line_all_widgets[1].setCheckable(True)
        self.cell_line_all_widgets[1].clicked.connect(self.print_cell_line_info_2)

        for widget in self.cell_line_all_widgets:
            self.layout.addWidget(widget)


        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        if self.login_state == 0:
            self.back_button.clicked.connect(self.read_only_state)
        else:
            self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button) 
        

    def do_delete(self):
        cursor = self.db.cursor()
        table_name = self.delete_record_all_widgets[0].text()
        column_name = self.delete_record_all_widgets[1].text()
        record_name = self.delete_record_all_widgets[2].text()


        cursor = self.db.cursor()

        query_text = "DELETE FROM " + table_name + " WHERE " + column_name + " = " + "\""+record_name  +"\";"
        print(query_text)


        try:
            cursor.execute(query_text)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Unable to delete record, may be cross-referenced.")
            ret = msg.exec_()

        cursor.close()
        self.db.commit()


    def delete_record(self):
        self.delete_record_all_widgets = []
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None

        enter_table_name = QtWidgets.QLineEdit(self)
        enter_table_name.setPlaceholderText("Enter table name")
        enter_column_name = QtWidgets.QLineEdit(self)
        enter_column_name.setPlaceholderText("Enter column to delete from")
        enter_record_name = QtWidgets.QLineEdit(self)
        enter_record_name.setPlaceholderText("Enter value to decide which records will be deleted")
        delete_go_button = QtWidgets.QPushButton("go")
        
        delete_go_button.setCheckable(True)
        delete_go_button.clicked.connect(self.do_delete)

        self.delete_record_all_widgets.append(enter_table_name)
        self.delete_record_all_widgets.append(enter_column_name)
        self.delete_record_all_widgets.append(enter_record_name)
        self.delete_record_all_widgets.append(delete_go_button)
        
        for widget in self.delete_record_all_widgets:
            self.layout.addWidget(widget)

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button) 


    def alter_state(self):
        cursor = self.db.cursor()
        table_name = self.alter_record_all_widgets[0].text()
        field_name = self.alter_record_all_widgets[1].text()
        pk = self.alter_record_all_widgets[2].text()
        actual_name = self.alter_record_all_widgets[3].text()
        new_value = self.alter_record_all_widgets[4].text()

        cursor = self.db.cursor()
        query_text = "UPDATE " + table_name + " SET " + field_name + "= \"" + new_value +"\"" + " WHERE " +  pk + "= " + "\"" + actual_name + "\";"
        print(query_text)

        try:
            cursor.execute(query_text)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Unable to alter record, it may be cross-referenced or not exist.")
            ret = msg.exec_()

        cursor.close()
        self.db.commit()

    def alter_record(self):
        if self.back_button != None:
            self.back_button.deleteLater()
            self.back_button = None
        self.alter_record_all_widgets = []

        enter_table_name = QtWidgets.QLineEdit(self)
        enter_table_name.setPlaceholderText("Enter table name")
        enter_field_name = QtWidgets.QLineEdit(self)
        enter_field_name.setPlaceholderText("Enter column to make edit")
        enter_pk = QtWidgets.QLineEdit(self)
        enter_pk.setPlaceholderText("Enter column criteria to select on")
        enter_actual_name = QtWidgets.QLineEdit(self)
        enter_actual_name.setPlaceholderText("Enter field to select on")

        enter_new_value = QtWidgets.QLineEdit(self)
        enter_new_value.setPlaceholderText("Enter new value")
        alter_go_button = QtWidgets.QPushButton("go")
        alter_go_button.setCheckable(True)
        alter_go_button.clicked.connect(self.alter_state)

        self.alter_record_all_widgets.append(enter_table_name)
        self.alter_record_all_widgets.append(enter_field_name)
        self.alter_record_all_widgets.append(enter_pk)
        self.alter_record_all_widgets.append(enter_actual_name)
        self.alter_record_all_widgets.append(enter_new_value)
        self.alter_record_all_widgets.append(alter_go_button)

        for widget in self.alter_record_all_widgets:
            self.layout.addWidget(widget)

        self.back_button = QtWidgets.QPushButton("Go back")
        self.back_button.setCheckable(True)
        self.back_button.clicked.connect(self.read_write_state)
        self.layout.addWidget(self.back_button) 

    def control_combobox(self):
        self.hide_all()
        if self.choices.currentText() == "Add a publication":
            for widget in self.literature_import_widgets:
                widget.show()

        elif self.choices.currentText() == "Find a perturbation":
            self.express_perturbation_info()

        elif self.choices.currentText() == "Plot perturbation frequency":
            self.plot_pert_freq()

        elif self.choices.currentText() == "Get all information on a perturbation":
            self.print_pert_info()

        elif self.choices.currentText() == "Get all information on a cell line":
            self.print_cell_line_info()

        elif self.choices.currentText() == "Get all information on a disease":
            self.print_disease_info()

        elif self.choices.currentText() == "Get all information on a gene":
            self.print_gene_info()

        elif self.choices.currentText() == "Delete a record":
            self.delete_record()

        elif self.choices.currentText() == "Alter a record":
            self.alter_record()

        elif self.choices.currentText() == "Get all information connected to a gene":
            self.all_gene_info()



        else:
            self.hide_all()

    def hide_all(self):
        for widget in self.literature_import_widgets:
            widget.hide()
        for widget in self.perturbation_show_widgets:
             widget.hide()
        for widget in self.perturbation_all_widgets:
            widget.hide()
        for widget in self.disease_all_widgets:
            widget.hide()
        for widget in self.gene_all_widgets:
            widget.hide()
        for widget in self.cell_line_all_widgets:
            widget.hide()
        for widget in self.alter_record_all_widgets:
            widget.hide()
        for widget in self.delete_record_all_widgets:
            widget.hide()
        for widget in self.gene_info_all_widgets:
            widget.hide()
        if self.choices != None:
            self.choices.hide()
        if self.output != None:
            self.output.hide()




    def connect_database(self):
        self.db = MySQLdb.connect(host,admin_username,admin_password,database)
        
    def disconnect_database(self):
        self.db.close()



if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")

        dark_palette = QPalette()

        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        app.setPalette(dark_palette)




        mainWin = MainWindow()
        app.exec_()


    run_app()