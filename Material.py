class Material(object):
    def __init__(self, PK, name, quantity, vendor, unitCost):
        self.PK = PK
        self.name = name
        #This quantity should be how many of these Materials exist for
        #   a single one of the Products it belongs to. So it should be set once
        #   and not changed from that point on.
        #TotalMaterialQuantity = Product.quantity*Material.quantity
        self.quantity = quantity
        self.vendor = vendor
        #The cost of these materials for a single Product in total equals
        #   self.quantity*self.unitCost
        #And if there is more than one product the total equals
        #   Product.quantity*Material.quantity*Material.unitCost
        self.unitCost = unitCost