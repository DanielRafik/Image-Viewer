from PyQt5.QtWidgets import*

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure

    
class MplWidget(QWidget):
    
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.set_facecolor('#242424')
        self.canvas.figure.set_facecolor("#242424")
        self.canvas.axes.spines['left'].set_color('white')        
        self.canvas.axes.spines['bottom'].set_color('white')  
        self.canvas.axes.tick_params(axis='x', colors='white')    #setting up X-axis tick color to red
        self.canvas.axes.tick_params(axis='y', colors='white')  #setting up Y-axis tick color to black 
        self.canvas.axes.xaxis.label.set_color('white')        #setting up X-axis label color to yellow
        self.canvas.axes.yaxis.label.set_color('white')          #setting up Y-axis label color to blue      
        self.setLayout(vertical_layout)