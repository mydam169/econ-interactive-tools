class LinearDSModel:
    def __init__(self, demand_intercept, demand_slope, supply_intercept, supply_slope):
        '''initiate a linear supply and demand model
        Demand: P = a + bQ (b < 0)
        Supply: P = c + dQ 
        Q_star = (a - c) / (d - b)
        P_star = a + b * Q_star
        '''
        assert demand_intercept > 0, "The demand intercept must be positive"
        assert demand_slope < 0, "The demand slope must be negative"
        assert supply_intercept > 0, "The supply intercept must be positive"
        assert demand_intercept > supply_intercept, "The supply intercept must be smaller than the demand intercept"
        assert supply_slope > 0, "The supply slope must be positive"
        self.a = demand_intercept 
        self.b = demand_slope
        self.c = supply_intercept
        self.d = supply_slope 

    @property
    def q_star(self):
        return (self.a - self.c) / (self.d - self.b)
    
    @property
    def p_star(self):
        return self.a + self.b * self.q_star
    
    @property
    def TS_star(self):
        return (self.a - self.c) * self.q_star * 0.5

    def get_demand_intercept(self):
        return self.a

    def get_supply_intercept(self):
        return self.c 

    def get_demand_slope(self):
        return self.b

    def get_supply_slope(self):
        return self.d
    
    def set_demand_intercept(self, demand_intercept):
        self.a = demand_intercept 

    def set_supply_intercept(self, supply_intercept):
        self.c = supply_intercept 

    def set_demand_slope(self, demand_slope):
        self.b = demand_slope

    def set_supply_slope(self, supply_slope):
        self.d = supply_slope

    def get_P_demand(self, quantity):
        return self.a + self.b * quantity
    
    def get_P_supply(self, quantity):
        return self.c + self.d * quantity 
    
    def get_Q_demand(self, price):
        return (price - self.a) / self.b 
    
    def get_Q_supply(self, price):
        return (price - self.c) / self.d
    
    def get_CS(self, quantity_bought, price_paid):
        return 0.5 * (self.a - price_paid) * quantity_bought
    
    def get_PS(self, quantity_sold, price_received):
        return 0.5 * (price_received - self.c) * quantity_sold
    

class TaxModel(LinearDSModel):
    def __init__(self, demand_intercept, demand_slope, supply_intercept, supply_slope, tax_size):
        super().__init__(demand_intercept, demand_slope, supply_intercept, supply_slope)
        self.tax = tax_size

    def get_tax_size(self):
        return self.tax 
    
    def set_tax_size(self, new_tax):
        self.tax = new_tax

    @property
    def q_T(self):
        return (self.a - self.c - self.tax) / (self.d - self.b)
    
    @property
    def P_d(self):
        return self.get_P_demand(self.q_T)
    
    @property 
    def P_s(self):
        return self.get_P_supply(self.q_T)
    
    @property
    def DWL_T(self):
        return 0.5 * (self.q_star - self.q_T) * self.tax
    
    @property 
    def tax_rev(self):
        return self.q_T * self.tax
    
    @property
    def CS_T(self):
        return (self.a - self.P_d) * self.q_T * 0.5
        # return self.get_CS(self.q_T, self.P_d)
    
    @property
    def PS_T(self):
        return self.get_PS(self.q_T, self.P_s)
        
class PriceFloor(LinearDSModel):
    def  __init__(self, demand_intercept, demand_slope, supply_intercept, supply_slope, floor):
        super().__init__(demand_intercept, demand_slope, supply_intercept, supply_slope)
        self.p_min = (1 + floor) * self.p_star

    def get_price_floor(self):
        return self.p_min
    
    def set_price_foor(self, price_floor):
        self.p_min = price_floor

    @property 
    def q_floor(self):
        return self.get_Q_demand(self.p_min)
    
    @property
    def q_excess(self):
        return self.get_Q_supply(self.p_min) - self.q_floor
    
    @property
    def DWL_floor(self):
        return 0.5 * (self.p_min - self.get_P_supply(self.q_floor)) * (self.q_star - self.q_floor)
    
    @property
    def CS_floor(self):
        return self.get_CS(self.q_floor, self.p_min)
    
    @property
    def PS_floor(self):
        return self.TS_star - self.CS_floor - self.DWL_floor

class PriceCeiling(LinearDSModel):
    def  __init__(self, demand_intercept, demand_slope, supply_intercept, supply_slope, ceiling):
        super().__init__(demand_intercept, demand_slope, supply_intercept, supply_slope)
        self.p_max = ceiling * self.p_star

    def get_price_ceiling(self):
        return self.p_max
    
    def set_price_ceiling(self, price_ceiling):
        self.p_max = price_ceiling

    @property
    def q_ceiling(self):
        return self.get_Q_supply(self.p_max)

    @property
    def q_shortage(self):
        return self.get_Q_demand(self.p_max) - self.q_ceiling

    @property
    def DWL_ceiling(self):
        return 0.5 * (self.get_P_demand(self.q_ceiling) - self.p_max) * (self.q_star - self.q_ceiling)

    @property
    def PS_ceiling(self):
        return self.get_PS(self.q_ceiling, self.p_max)

    @property
    def CS_ceiling(self):
        return self.TS_star - self.PS_ceiling - self.DWL_ceiling

    
    
    
    
  



    

