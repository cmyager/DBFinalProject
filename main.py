from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter import ttk
from Controller import Controller


#Because multiple functions can be wrapped in single function and this is needed for the scrollbar.
def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func
    
def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))
        
def updateTableHeader(table, header, colWidths):
    """
    This just updates the names of the headers for the given table.
    @param table A TreeView object for the table that we're updating.
    @param header A list of strings for the header names of each column.
    @param colWidths A list of numbers that identify the current width of each column.
    """
    for i in range(len(header)):
        table.heading(header[i], text=header[i].title(), command=lambda c=header[i]: sortby(table, c, 0))
        table.column(header[i], width=tkFont.Font().measure(header[i].title()))
        colWidths[i] = tkFont.Font().measure(header[i].title())
        
def AdjustColumnWidths(table, header, colWidths, newItem):
    """
    This looks at an item that is being added to a table and if the new item is too large for
    the current column width, the columns will be adjusted.
    @param table A TreeView object for the table that we're updating.
    @param header A list of strings for the header names of each column.
    @param colWidths A list of numbers that identify the current width of each column.
    @param newItem  The item that's being added to the table.
    """
    for ix, val in enumerate(newItem):
        col_w = tkFont.Font().measure(val)
        if (colWidths[ix] < col_w):
            table.column(header[ix], width=col_w)
            colWidths[ix] = col_w
        

class Application(Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master, padding=(5, 0, 100, 5))
        
        self.master = master
        
        self.master.title("DB Stuff")
        self.master.geometry('900x760')
        
        Controller.Setup()
        
        #Set up the grid for the Widgets
        self.grid(column=0, row=0, sticky=(N,W,E,S))
        self.master.grid_columnconfigure(0,weight=1)
        self.master.grid_rowconfigure(0,weight=1)
        
        
        #Vars for the product table
        self.productTable = None
        self.productHeader = ["name", "finish", "quantity"]
        self.productColWidth = [0, 0, 0]
        
        #The primary keys and product names that will be used with the dropdown box.
        self.possibleProductIds, self.possibleProductNames = Controller.GetPossibleProducts()
        
        #Vars for the material table
        self.materialTable = None
        self.materialHeader = ["name", "vendor", "unit cost", "quantity"]
        self.materialColWidth = [0, 0, 0, 0]
        
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        """
        This creates all of the widgets for the gui and places them in the correct spots.
        """
        #Create all of the widgets that we will be using.
        
        
        #These widgets are for the product table.
        productLbl = ttk.Label(self, text="Products")
        
        self.productTable = ttk.Treeview(self, columns=self.productHeader, show="headings")
        prodvsb = ttk.Scrollbar(self, orient="vertical", command=self.productTable.yview)
        prodhsb = ttk.Scrollbar(self, orient="horizontal", command=self.productTable.xview)
        self.productTable.configure(yscrollcommand=prodvsb.set, xscrollcommand=prodhsb.set)
        
        
        #This will display the total cost of all the materials selected.
        totalCostHdrLbl = ttk.Label(self, text="Total Cost of Materials")
        totalCostLbl = ttk.Label(self, text="$0.00")
        
        #This variable defines how much Products will be added/removed.
        productNumber = IntVar()
        productNumber.set(1)
        
        def updateTotalCost():
            """
            This is used to update the total cost of the materials that are currently in 
            the materials table and show that number to the user.
            """
            totalCost = 0.0
            for prodiid in self.productTable.get_children():
                product = Controller.GetProduct(prodiid)
                    
                for material in product.materials:
                    totalCost += material.unitCost*material.quantity*product.quantity
                
            totalCostLbl["text"] = "$%0.2f"%(totalCost)
        
        def removeProduct(*args):
            """
            This will remove all of the products that are selected in the product table.
            """
            selitems = self.productTable.selection()
            
            #This is how many of each product we'll be removing!
            amountToRemove = productNumber.get()
            
            for prodiid in selitems:
                if (self.productTable.exists(prodiid)):
                    product = Controller.GetProduct(prodiid)
                    
                    for material in product.materials:
                        if (product.quantity-amountToRemove > 0):
                            newMat = (material.name, material.vendor, "$%0.2f"%material.unitCost, (product.quantity-amountToRemove)*material.quantity)
                            self.materialTable.item(material.PK, values=newMat)
                        else:
                            self.materialTable.delete(material.PK)

                    #We should only be subtracting the product by 1 until there are no more. Then
                    #   we'll delete the row.
                    if (product.quantity-amountToRemove > 0):
                        newProd = (product.columnInfo["ProductDescription"], product.columnInfo["ProductFinish"], product.quantity-amountToRemove)
                        self.productTable.item(prodiid, values=newProd)
                    else:
                        self.productTable.delete(prodiid)
                        
                    #This just subtracts from the quantity if more than 1 exists.
                    #Then it deletes the product obj for good if the quantity reaches 0.
                    Controller.RemoveProduct(prodiid, productNumber.get())
            
            updateTotalCost()
        def removeAllProducts(*args):
            for i in range(len(self.productTable.get_children())-1,-1,-1):
                self.productTable.delete(self.productTable.get_children()[i])
                
            for i in range(len(self.materialTable.get_children())-1,-1,-1):
                self.materialTable.delete(self.materialTable.get_children()[i])
                
            updateTotalCost()
        
        #These buttons are used to remove selected products in the product table
        removeProductBtn = ttk.Button(self, text="Remove Product", command=removeProduct)
        removeAllProductsBtn = ttk.Button(self, text="Remove All Products", command=removeAllProducts)
        
        #The material table's widgets.
        materialLbl = ttk.Label(self, text="Materials")
        self.materialTable = ttk.Treeview(self, columns=self.materialHeader, show="headings", selectmode="none")
        matvsb = ttk.Scrollbar(self, orient="vertical", command=self.materialTable.yview)
        mathsb = ttk.Scrollbar(self, orient="horizontal", command=self.materialTable.xview)
        self.materialTable.configure(yscrollcommand=matvsb.set, xscrollcommand=mathsb.set)
        
        quitBtn = ttk.Button(self, text="QUIT", command=self.master.destroy)
        
        
        dropdownLbl = ttk.Label(self, text="Select a Product to Add!")
        
        selectedProductVar = StringVar(self.master)
        dropdown = ttk.OptionMenu(self, selectedProductVar, "<Product>", *self.possibleProductNames)
        
        
        productNumberHeaderLbl = ttk.Label(self, text="Change the Number of Products to Add/Remove!")
        
        def intOnly(*args):
            """
            This makes sure the slider only is setting productNumber to an integer value.
            """
            productNumber.set(round(productNumber.get()))
        
        productNumberSlider = ttk.Scale(self, orient=HORIZONTAL, length=300, from_=1.0, to=50.0, variable=productNumber, command=intOnly)
        
        productNumberLbl = ttk.Label(self, textvariable=productNumber)
        productNumberLbl["text"] = 1
        
        def addProduct(*args):
            """
            This adds the currently selected product using information from a database that is fetched by the Controller class
            and then stored in Product and Material objects.
            """
            if (selectedProductVar.get() != "<Product>"):
                indx = self.possibleProductNames.index(selectedProductVar.get())
                product, messages = Controller.AddProduct(self.possibleProductIds[indx], productNumber.get())
                
                #There are several possible messages we might get back after trying to add a product. Let's display those to the user first.
                for msg in messages:
                    messagebox.showwarning("Possible Problem", msg)
                
                if (product != None):
                    newProd = (product.columnInfo["ProductDescription"], product.columnInfo["ProductFinish"], product.quantity)
                    
                    #First check to see if the product and its materials exist already!
                    #There should only be 1 instance of each product and material in the tables.
                    if (self.productTable.exists(product.PK)):
                        self.productTable.item(product.PK, values=newProd)
                    else:
                        self.productTable.insert("", "end", iid=product.PK, values=newProd)
                    
                    AdjustColumnWidths(self.productTable, self.productHeader, self.productColWidth, newProd)
                    
                    for mat in product.materials:
                        newMat = (mat.name, mat.vendor, "$%0.2f"%mat.unitCost, product.quantity*mat.quantity)
                        if (self.materialTable.exists(mat.PK)):
                            self.materialTable.item(mat.PK, values=newMat)
                        else:
                            self.materialTable.insert("", "end", iid=mat.PK, values=newMat)
                        
                        AdjustColumnWidths(self.materialTable, self.materialHeader, self.materialColWidth, newMat)
                        
                    
                    sortby(self.productTable, self.productHeader[0], False)
                    sortby(self.materialTable, self.materialHeader[0], False)
            
            updateTotalCost()
            
        addProductBtn = ttk.Button(self, text="Add Product", command=addProduct)
        
        def submitOrder(*args):
            success, exception = Controller.SubmitProducts()
            if (success):
                messagebox.showinfo("Completion", "The order for your products has been submitted!")
            else:
                messagebox.showwarning("Possible Problem", "The order was unable to be submitted!\n" + exception)
        
        submitionBtn = ttk.Button(self, text="Submit Order", command=submitOrder)
        
        #Set up the widget's location in the GUI
        productLbl.grid(column=0, row=0, pady=10)
        self.productTable.grid(column=0, row=1, columnspan=4, stick=(N,S,E,W))
        prodvsb.grid(column=4, row=1, sticky="ns")
        prodhsb.grid(column=0, row=2, columnspan=4, sticky="ew")
        
        removeProductBtn.grid(column=0, row=3, pady=10)
        removeAllProductsBtn.grid(column=0, row=4)
        
        dropdownLbl.grid(column=3, row=3, pady=10)
        dropdown.grid(column=3, row=4)
        addProductBtn.grid(column=3, row=5)
        
        productNumberHeaderLbl.grid(column=1, row=3, columnspan=2, pady=10)
        productNumberSlider.grid(column=1, row=4, pady=10, padx=50, columnspan=2)
        productNumberLbl.grid(column=1,row=5, columnspan=2)
        
        materialLbl.grid(column=0, row=6, pady=10)
        self.materialTable.grid(column=0, row=7, columnspan=4, stick=(N,S,E,W))
        matvsb.grid(column=4, row=7, sticky="ns")
        mathsb.grid(column=0, row=8, columnspan=4, sticky="ew")
        
        quitBtn.grid(column=0, row=10)
        
        totalCostHdrLbl.grid(column=1, row=9, pady=10)
        totalCostLbl.grid(column=1, row=10)
        
        submitionBtn.grid(column=3, row=10)
        
        self.columnconfigure(0, minsize=120)
        self.columnconfigure(1, minsize=120)
        self.columnconfigure(2, minsize=120)
        self.columnconfigure(3, minsize=220)
        
        updateTableHeader(self.productTable, self.productHeader, self.productColWidth)
        updateTableHeader(self.materialTable, self.materialHeader, self.materialColWidth)
        
def main():
    root = Tk()
    app = Application(master=root)
    app.mainloop()
    Controller.TearDown()
    
main()