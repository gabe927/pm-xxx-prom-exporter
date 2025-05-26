import requests
import logging
log = logging.getLogger(__name__)

class PM_Meter:
    meters = []

    hostname = None
    values = {
        'l1_volt'     : None,
        'l2_volt'     : None,
        'l3_volt'     : None,
        'l12_volt'    : None,
        'l23_volt'    : None,
        'l31_volt'    : None,
        'l1_amps'     : None,
        'l2_amps'     : None,
        'l3_amps'     : None,
        'n_amps'      : None,
        'frequency'   : None,
        'v_avrg'      : None,
        'u_avrg'      : None,
        'i_avrg'      : None,
        'tot_p'       : None,
        'tot_q'       : None,
        'tot_s'       : None,
        'pow_factor'  : None,
        'demand_i1'   : None,
        'demand_i2'   : None,
        'demand_i3'   : None,
        'demand_ia'   : None,
        'demand_p'    : None,
        'demand_q'    : None,
        'thd_l1'      : None,
        'thd_l2'      : None,
        'thd_l3'      : None,
        'thd_l12'     : None,
        'thd_l23'     : None,
        'thd_l31'     : None,
        'thd_i1'      : None,
        'thd_i2'      : None,
        'thd_i3'      : None,
        'thd_in'      : None
    }

    def __init__(self, hostname):
        self.hostname = hostname
        self.meters.append(self)
        log.info(f"New meter ({hostname}) created")

    def __str__(self):
        return self.hostname
    
    def get_hostname(self):
        return self.hostname
    
    def set_hostname(self, hostname):
        log.info(f"Setting meter ({self.hostname}) to new hostname ({hostname})")
        self.hostname = str(hostname)
    
    def get_values(self):
        return self.values
    
    @classmethod
    def get_meter_from_hostname(self, hostname):
        for meter in self.meters:
            if meter.hostname == hostname:
                return meter
        return None
    
    @classmethod
    def get_meters(self):
        return self.meters
    
    @classmethod
    def new_meter(self, hostname):
        return PM_Meter(hostname)
    
    @classmethod
    def del_meter(self, hostname):
        meter = self.get_meter_from_hostname(hostname)
        if meter:
            self.meters.remove(meter)
            log.info(f"Meter ({hostname}) removed")
            return True
        else:
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)