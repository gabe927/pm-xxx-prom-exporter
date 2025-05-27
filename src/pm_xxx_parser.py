import requests
import time
import re
import logging
log = logging.getLogger(__name__)

class PM_Meter:
    meters = []

    hostname = None
    is_up = False
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
    
class PM_Parser:
    cache_ttl = 1 #time to live in seconds for the cache before a new data must be pulled
    _cache_time = -1
    request_timeout = 2
    meter_update_callback = None
    meter_down_callback = None
    meter_removed_callback = None

    def register_meter(self, hostname):
        # check that meter isn't already registered
        meter = PM_Meter.get_meter_from_hostname(hostname)
        if meter != None:
            return meter
        # register new meter
        return PM_Meter(hostname)

    def unregister_meter(self, hostname):
        meter = PM_Meter.get_meter_from_hostname(hostname)
        if meter:
            if self.meter_removed_callback:
                self.meter_removed_callback(meter)
            PM_Meter.del_meter(hostname)

    def set_cache_ttl_seconds(self, cache_ttl):
        self.cache_ttl = cache_ttl
        log.info(f"Parser cache TTL set to {cache_ttl} seconds")

    def set_request_timeout_seconds(self, request_timeout):
        self.request_timeout = request_timeout
        log.info(f"Parser request timeout set to {request_timeout} seconds")

    def pull_data(self):
        # check cache ttl
        currTime = time.time()
        if (currTime < self._cache_time + self.cache_ttl):
            # return cache if ttl not met
            log.debug(f"get_data returning cache | cache time:{self._cache_time} | currTime:{currTime}")
            return PM_Meter.meters
        
        # get data for each meter, parse and update the class data
        for m in PM_Meter.meters:
            try:
                response = requests.get(f"http://{m.hostname}/scd.xml", timeout=self.request_timeout)
            except Exception as e:
                log.warning(f"Meter ({m.hostname}) request error: {e}")
                m.is_up = False
                if self.meter_down_callback:
                    self.meter_down_callback(m)
                continue
            if response.status_code != 200:
                log.warning(f"Meter ({m.hostname}) returned status code ")
                m.is_up = False
                if self.meter_down_callback:
                    self.meter_down_callback(m)
                continue
            
            str_values = re.findall(r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", response.text)
            values = [float(i) for i in str_values]
            value_keys = list(m.values)
            for i in range(len(m.values)):
                m.values[value_keys[i]] = values[i]
            logging.debug(f"Parsed values:{m.values}")
            m.is_up = True
            if self.meter_update_callback:
                self.meter_update_callback(m)

        # update cache time
        self._cache_time = currTime
        log.debug(f"cache time updated:{currTime}")

    def run(self):
        try:
            while True:
                self.pull_data()
                sleep_time = (self._cache_time + self.cache_ttl) - time.time()
                log.debug(f"sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            log.info("Keyboard Interrupt detected. Exiting...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # test with local scd.xml test file via Live Server
    parser = PM_Parser()
    parser.register_meter("127.0.0.1:5500/example%20files")
    parser.run()