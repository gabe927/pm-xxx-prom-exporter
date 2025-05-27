from flask import Flask, Response, redirect
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Enum, Counter, Gauge, Info
from waitress import serve
from pm_xxx_parser import PM_Parser
from dotenv import load_dotenv
import threading
import os
import logging
log = logging.getLogger(__name__)

app = Flask(__name__)

### Setup Routes ###

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route("/")
def index():
    return redirect("/metrics")

### Setup Datapoints ###

log.info("Setting up datapoints...")
main_label = ["host"]

gauges = {
    "up":        {"description": "Is meter up?", "gauge": None},
    "l1_volt":   {"description": "Leg 1 Voltage", "gauge": None},
    "l2_volt":   {"description": "Leg 2 Voltage", "gauge": None},
    "l3_volt":   {"description": "Leg 3 Voltage", "gauge": None},
    "l12_volt":  {"description": "Leg 1 to Leg 2 Voltage", "gauge": None},
    "l23_volt":  {"description": "Leg 2 to Leg 3 Voltage", "gauge": None},
    "l31_volt":  {"description": "Leg 3 to Leg 1 Voltage", "gauge": None},
    "l1_amps":   {"description": "Leg 1 Amps", "gauge": None},
    "l2_amps":   {"description": "Leg 2 Amps", "gauge": None},
    "l3_amps":   {"description": "Leg 3 Amps", "gauge": None},
    "n_amps":    {"description": "Neutral Leg Amps", "gauge": None},
    "frequency": {"description": "Input Frequency", "gauge": None},
    "v_avrg":    {"description": "Average leg voltage", "gauge": None},
    "u_avrg":    {"description": "Average leg-to-leg voltage", "gauge": None},
    "i_avrg":    {"description": "Average current", "gauge": None},
    "tot_p":     {"description": "Total Power", "gauge": None},
    "tot_q":     {"description": "Total Reactive Power", "gauge": None},
    "tot_s":     {"description": "Total Apparent Power", "gauge": None},
    "pow_factor": {"description": "Power Factor", "gauge": None},
    "demand_i1": {"description": "Leg 1 Current Demand", "gauge": None},
    "demand_i2": {"description": "Leg 2 Current Demand", "gauge": None},
    "demand_i3": {"description": "Leg 3 Current Demand", "gauge": None},
    "demand_ia": {"description": "Average Current Demand", "gauge": None},
    "demand_p":  {"description": "Power Demand", "gauge": None},
    "demand_q":  {"description": "Reactive Power Demand", "gauge": None},
    "thd_l1":    {"description": "Leg 1 Voltage Total Harmonic Distortion", "gauge": None},
    "thd_l2":    {"description": "Leg 2 Voltage Total Harmonic Distortion", "gauge": None},
    "thd_l3":    {"description": "Leg 3 Voltage Total Harmonic Distortion", "gauge": None},
    "thd_l12":   {"description": "Leg 1 to Leg 2 Voltage Total Harmonic Distortion", "gauge": None},
    "thd_l23":   {"description": "Leg 2 to Leg 3 Voltage Total Harmonic Distortion", "gauge": None},
    "thd_l31":   {"description": "Leg 3 to Leg 1 Voltage Total Harmonic Distortion", "gauge": None},
    "thd_i1":    {"description": "Leg 1 Current Total Harmonic Distortion", "gauge": None},
    "thd_i2":    {"description": "Leg 2 Current Total Harmonic Distortion", "gauge": None},
    "thd_i3":    {"description": "Leg 3 Current Total Harmonic Distortion", "gauge": None},
    "thd_in":    {"description": "Neutral Leg Current Total Harmonic Distortion", "gauge": None},
}

for k, v in gauges.items():
    v["gauge"] = Gauge(k, v["description"], main_label)


log.info("Done setting up datapoints")


### Callbacks ###
def meter_update_callback(meter):
    label = [meter.hostname]
    values = meter.values
    gauges["up"]["gauge"].labels(*label).set(1)
    for k, v in values.items():
        gauges[k]["gauge"].labels(*label).set(v)
    log.debug(f"Gauges for meter ({meter.hostname}) updated")

def meter_down_callback(meter):
    label = [meter.hostname]
    values = meter.values
    gauges["up"]["gauge"].labels(*label).set(0)
    for k, v in values.items():
        gauges[k]["gauge"].remove(*label)
    log.debug(f"Gauges for meter ({meter.hostname}) set to down state")

def meter_removed_callback(meter):
    label = [meter.hostname]
    values = meter.values
    gauges["up"]["gauge"].remove(*label)
    for k, v in values.items():
        gauges[k]["gauge"].remove(*label)
    log.debug(f"Gauges for meter ({meter.hostname}) removed")


if __name__ == "__main__":
    # configure logging
    logging.basicConfig(level=logging.INFO)

    # create parser
    parser = PM_Parser()

    ### load environment
    # load .env file if available
    load_dotenv()
    hostnames_str = os.getenv("METERS")
    if hostnames_str == None:
        log.error("METERS environment variable not defined!")
        exit()
    hostnames = hostnames_str.split(",")
    for m in hostnames:
        parser.register_meter(m)

    # run da threads
    parser_thread = threading.Thread(target=parser.run, args=(meter_update_callback, meter_down_callback, meter_removed_callback), daemon=True)
    parser_thread.start()
    serve(app, host="0.0.0.0", port=9584)