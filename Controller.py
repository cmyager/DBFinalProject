from __future__ import print_function
import pymysql
import sys

from Product import Product

class Controller(object):
    """
    The middleman inbetween the database connection engine and the GUI.
    """
    
    cnx = 0
    cursor = 0
    pendingProducts = []
    
    @classmethod
    def Setup(cls):
        cls.cnx = pymysql.connect(user='CS', host='isoptera.lcsc.edu', password = "cs445", database='cs445')
        print("Databse Connected")
        cls.cursor = cls.cnx.cursor()
        
    @classmethod
    def TearDown(cls):
        cls.cursor.close()
        cls.cnx.commit()
        cls.cnx.close()
        print("DONE")

    @classmethod
    def GetPossibleProducts(cls):
        """
        Fetches a list of the Products that this company is able to sell.
        @return
            A list of primary keys for the products and a list of names for the products. 
            (Maybe a dictionary would have been better to use... whatever.)
        """
        cls.cursor.execute("SELECT * FROM Product_T")
        
        productIds      = []
        productNames    = []
        
        for row in cls.cursor:
            if (row[0] != None and row[2] != None and row[3] != None):
                if (len(productIds) == 0):
                    productIds.append(row[0])
                    productNames.append("%s-%s"%(row[2], row[3]))
                else:
                    for i in range(len(productIds)):
                        productName = "%s-%s"%(row[2], row[3])
                        if (productName < productNames[i]):
                            productIds.insert(i, row[0])
                            productNames.insert(i, productName)
                            break
                        elif (i == len(productIds)-1):
                            productIds.append(row[0])
                            productNames.append(productName)
                            break
            
        return productIds, productNames
        
    @classmethod
    def GetProduct(cls, productPK):
        product = None
        for i in range(len(cls.pendingProducts)):
            if (str(cls.pendingProducts[i].PK) == str(productPK)):
                product = cls.pendingProducts[i]
                break
                
        return product
        
    @classmethod
    def RemoveProduct(cls, productPK, amountToRemove):
        """
        This subtracts from a product's quantity until the quantity is zero. Then
        the product is removed entirely.
        """
        for i in range(len(cls.pendingProducts)):
            if (cls.pendingProducts[i].PK == int(productPK)):
                if (cls.pendingProducts[i].quantity - amountToRemove <= 0):
                    del cls.pendingProducts[i]
                    break
                else:
                    cls.pendingProducts[i].quantity -= amountToRemove
                    break
        
    @classmethod
    def AddProduct(cls, productPK, quantity):
        """
        This adds to the self.pendingProducts list with Product objects that
        have been built using data from the database.
        @param productPK    The primary key of the product that is to be add.
        @param quantity     The amount of products that is being added.
        
        @return Returns the Product object that was just created or added to.
        """
        cls.cursor.execute("SELECT * FROM Product_T WHERE ProductID='%s'"%(productPK))
        
        product = cls.GetProduct(productPK)
        messages = []
        
        if (product == None):
            product = Product(quantity)
            
            columnNames = []
            
            for column in cls.cursor.description:
                columnNames.append(column[0])
                
            #Add those columns to the Product object!
            if (not product.AddColumns(columnNames, list(cls.cursor)[0])):
                print("AddColumns failed within Controller.AddProduct!")
            
            #Query vendors and materials and add that info to the product.
            cls.cursor.execute("SELECT * FROM Uses_T WHERE ProductID='%s'"%(productPK))
            
            materialsNeeded = list(cls.cursor)
            
            #Sometimes there are products that don't even have listed materials. So we'll
            #   just skip over those ones.
            if (materialsNeeded != []):
                for material in materialsNeeded:
                    cls.cursor.execute("SELECT * FROM RawMaterial_T WHERE MaterialID='%s'"%(material[0]))
                    materialResults = list(cls.cursor)
                    
                    if (materialResults != []):
                        #There should be a single tuple within this list.
                        materialResults = materialResults[0]
                        
                        #Now we query the vendorID and his/her price for this material.
                        cls.cursor.execute("SELECT * FROM Supplies_T WHERE MaterialID='%s'"%(material[0]))
                        
                        suppliesResults = list(cls.cursor)
                    
                        if (suppliesResults != []):
                            #There should be a single tuple within this list.
                            suppliesResults = suppliesResults[0]
                            
                            #Now we query the name of the vendor
                            cls.cursor.execute("SELECT * FROM Vendor_T WHERE VendorID=%d"%(int(suppliesResults[0])))
                        
                            vendorResults = list(cls.cursor)
                        
                            if (vendorResults != []):
                                #There should be a single tuple within this list.
                                vendorResults = vendorResults[0]
                            
                                product.AddMaterial(materialResults[0], materialResults[1], material[2], vendorResults[1], float(suppliesResults[2]))
                            else:
                                #The standard price for the material in the Product_T is used for the UnitCost if a Vendor isn't found.
                                product.AddMaterial(materialResults[0], materialResults[1], material[2], "Unknown", float(materialResults[6]))
                                messages.append("VendorID, %d, doesn't exist within the Vendor_T table!"%(int(suppliesResults[0])))
                                
                        else:
                            #The standard price for the material in the Product_T is used for the UnitCost if a Vendor isn't found.
                            product.AddMaterial(materialResults[0], materialResults[1], material[2], "Unknown", float(materialResults[6]))
                            messages.append("MaterialID, %s, doesn't exist within the Supplies_T table!"%(material[0]))
                        
                    else:
                        messages.append("MaterialID, %s, doesn't exist within the RawMaterial_T table!"%(material[0]))
                        
                if (product.materials != []):
                    cls.pendingProducts.append(product)
                else:
                    messages.append("There were no materials found for product: %s-%s!"%(product.columnInfo["ProductDescription"], product.columnInfo["ProductFinish"]))
                    product = None
            else:
                messages.append("There were no materials found for product: %s-%s!"%(product.columnInfo["ProductDescription"], product.columnInfo["ProductFinish"]))
                product = None
        else:
            product.quantity += quantity
        
        return product, messages
        
    @classmethod
    def SubmitProducts(cls):
        """
        This submits the pending products that have been selected by the user. This means that
        the ProductsOnHand in the database within the Product_T table will be updated with the
        amount of products that have been selected.
        """
        success = True
        exception = None
        try:
            for product in cls.pendingProducts:
                print("Adding %d to ProductID %s"%(product.quantity, product.PK))
                cls.cursor.execute("UPDATE Product_T SET ProductOnHand=ProductOnHand+%d WHERE ProductID='%s'"%(product.quantity, product.PK))
                
            cls.cnx.commit()
        except:
            success = False
            exception = str(sys.exc_info()[0])
        
        return success, exception
        