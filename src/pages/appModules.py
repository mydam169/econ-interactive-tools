class LinearDSModel:
    def __init__(self, demand_intercept: float, demand_slope: float, supply_intercept: float, supply_slope: float):
        '''initiate a linear supply and demand model
        Demand: P = a + bQ (b < 0)
        Supply: P = c + dQ 
        Q_star = (a - c) / (d - b)
        P_star = a + b * Q_star
        '''
        assert demand_intercept > 0, "The demand intercept must be positive"
        assert demand_slope < 0, "The demand slope must be negative"
        assert supply_intercept >= 0, "The supply intercept must be positive"
        assert demand_intercept >= supply_intercept, "The supply intercept must be smaller than the demand intercept"
        assert supply_slope > 0, "The supply slope must be positive"
        self._a = demand_intercept 
        self._b = demand_slope
        self._c = supply_intercept
        self._d = supply_slope 

    @property
    def q_star(self):
        return (self._a - self._c) / (self._d - self._b)
    
    @property
    def p_star(self):
        return self._a + self._b * self.q_star
    
    @property
    def TS_star(self):
        return (self._a - self._c) * self.q_star * 0.5

    @property
    def demand_intercept(self):
        return self._a
    
    @demand_intercept.setter
    def demand_intercept(self, value):
        if value <= 0:
            raise ValueError("Demand intercept must be positive")
        self._a = value 

    @property
    def demand_slope(self):
        return self._b
    
    @demand_slope.setter
    def demand_slope(self, value):
        if value >= 0:
            raise ValueError("Demand slope must be negative")
        self._b = value
    
    @property
    def supply_intercept(self):
        return self._c 
    
    @supply_intercept.setter 
    def supply_intercept(self, value):
        if value <= 0:
            raise ValueError("Supply intercept must be positive")
        if value >= self._a:
            raise ValueError("Supply intercept must be less than demand intercept")
        self._c = value

    @property
    def supply_slope(self):
        return self._d
    
    @supply_slope.setter
    def supply_slope(self, value):
        if value <= 0:
            raise ValueError("Supply slope must be positive")
        self._d = value

    def get_P_demand(self, quantity):
        return self._a + self._b * quantity
    
    def get_P_supply(self, quantity):
        return self._c + self._d * quantity 
    
    def get_Q_demand(self, price):
        return (price - self._a) / self._b 
    
    def get_Q_supply(self, price):
        return (price - self._c) / self._d
    
    def get_CS(self, quantity_bought, price_paid):
        return 0.5 * (self._a - price_paid) * quantity_bought
    
    def get_PS(self, quantity_sold, price_received):
        return 0.5 * (price_received - self._c) * quantity_sold
    
    

class TaxModel(LinearDSModel):
    def __init__(self, demand_intercept, demand_slope, supply_intercept, supply_slope, tax_size=None):
        super().__init__(demand_intercept, demand_slope, supply_intercept, supply_slope)
        self.tax = tax_size
    
    @property
    def tax_size(self):
        return self.tax
    
    @tax_size.setter 
    def tax_size(self, value):
        # if value >= self._a - self._c:
        #     self.tax = self._a - self._c 
        # else:
        #     self.tax = value
        self.tax = min(value, self._a - self._c)

    @property
    def q_T(self):
        return (self._a - self._c - self.tax) / (self._d - self._b)
    
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
        return (self._a - self.P_d) * self.q_T * 0.5
    
    @property
    def PS_T(self):
        return self.get_PS(self.q_T, self.P_s)
        
class PriceFloor(LinearDSModel):
    def  __init__(self, demand_intercept, demand_slope, supply_intercept, supply_slope, floor=None):
        super().__init__(demand_intercept, demand_slope, supply_intercept, supply_slope)
        # self.p_min = (1 + floor) * self.p_star

    @property
    def price_floor(self):
        return self.p_min
    
    @price_floor.setter
    def price_floor(self, markup):
        # price floor cannot exceed demand intercept
        # self.p_min = min(self._a, (1 + markup) * self.p_star)
        self.p_min = (1 + markup) * self.p_star


    @property 
    def q_floor(self):
        return max(self.get_Q_demand(self.p_min), 0)
    
    @property
    def q_excess(self):
        return self.get_Q_supply(self.p_min) - self.q_floor
    
    @property
    def DWL_floor(self):
        return min(0.5 * (self.p_min - self.get_P_supply(self.q_floor)) * (self.q_star - self.q_floor), 
                   self.TS_star)
    
    @property
    def CS_floor(self):
        return self.get_CS(self.q_floor, self.p_min)
    
    @property
    def PS_floor(self):
        return self.TS_star - self.CS_floor - self.DWL_floor

class PriceCeiling(LinearDSModel):
    def  __init__(self, demand_intercept, demand_slope, supply_intercept, supply_slope, ceiling=None):
        super().__init__(demand_intercept, demand_slope, supply_intercept, supply_slope)
        # self.p_max = ceiling * self.p_star

    @property 
    def price_ceiling(self):
        return self.p_max 
    
    @price_ceiling.setter 
    def price_ceiling(self, ceiling_percent):
        if ceiling_percent > 1:
            raise ValueError("Must be a value between zero and one")
        self.p_max = self.p_star * ceiling_percent


    @property
    def q_ceiling(self):
        return max(self.get_Q_supply(self.p_max), 0)

    @property
    def q_shortage(self):
        return self.get_Q_demand(self.p_max) - self.q_ceiling

    @property
    def DWL_ceiling(self):
        return min(0.5 * (self.get_P_demand(self.q_ceiling) - self.p_max) * (self.q_star - self.q_ceiling), 
                   self.TS_star)

    @property
    def PS_ceiling(self):
        return self.get_PS(self.q_ceiling, self.p_max)

    @property
    def CS_ceiling(self):
        return self.TS_star - self.PS_ceiling - self.DWL_ceiling

    
    
    
    
  



    

