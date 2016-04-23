from Material import Material
import random

class Product(object):
    def __init__(self, quantity):
        self.quantity   = quantity
        
        self.columnInfo = {}
        
        self.PK = ""
        
        #A list of material objects.
        #These are the materials for a single product
        self.materials  = []
        
    def AddColumns(self, columnNames, columnValues):
        """
        This takes in a list of column names and column values. Then it maps those
        two lists together and saves the results to self.columnInfo
        @param columnNames A list of columnNames for the Product_T table.
        @param columnValues A list of columnValues for this specific product in Product_T.
        @return A boolean telling whether this was a success or not.
        """
        success = False
        
        if (len(columnNames) == len(columnValues)):
            success = True
            self.PK = columnValues[0]
            for i in range(len(columnNames)):
                self.columnInfo[columnNames[i]] = columnValues[i]
                
        #Remove this when Controller.AddProduct() is finished
        #self.AddMaterial(str(random.randint(0,1000)), "test", 5, "Albertsons", 5.0)
        #self.AddMaterial("5", "test", 5, "Albertsons", 500000)
        
        return success
        
    def GetMaterial(self, PK):
        material = None
        for mat in self.materials:
            if (str(mat.PK) == str(PK)):
                material = mat
                break
                
        return material
                
    def AddMaterial(self, PK, name, quantity, vendor, unitCost):
        """
        This will add a material to this Product's list of materials. If the material already exists,
        then its quantity will be added to the first material object.
        @param PK           The primary key (string) for the material in the database.
        @param name         A string representing the name of the material.
        @param quantity     An integer representing the amount of <some material> needed for a single one of this product.
                                The material's quantity will be static and won't be changed along with the Product's quantity!
        @param vendor       A string representing the name of the vendor that supplies this material.
        @param unitCost     The cost for a single one of this material. A float or integer is assumed.
        """
        material = self.GetMaterial(PK)
        if (material == None):
            self.materials.append(Material(PK, name, quantity, vendor, unitCost))
        else:
            material.quantity += quantity