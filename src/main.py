from flask import Flask, Response, redirect
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Enum, Counter, Gauge, Info
from waitress import serve
import threading
import requests
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

l1_volt     = Gauge("l1_volt", "Leg 1 Voltage", main_label)
l2_volt     = Gauge("l2_volt", "Leg 2 Voltage", main_label)
l3_volt     = Gauge("l3_volt", "Leg 3 Voltage", main_label)
l12_volt    = Gauge("l12_volt", "Leg 1 to Leg 2 Voltage", main_label)
l23_volt    = Gauge("l23_volt", "Leg 2 to Leg 3 Voltage", main_label)
l31_volt    = Gauge("l31_volt", "Leg 3 to Leg 1 Voltage", main_label)
l1_amps     = Gauge("l1_amps", "Leg 1 Amps", main_label)
l2_amps     = Gauge("l2_amps", "Leg 2 Amps", main_label)
l3_amps     = Gauge("l3_amps", "Leg 3 Amps", main_label)
n_amps      = Gauge("n_amps", "Neutral Leg Amps", main_label)
frequency   = Gauge("frequency", "Input Frequency", main_label)
v_avrg      = Gauge("v_avrg", "Average leg voltage", main_label)
u_avrg      = Gauge("u_avrg", "Average leg-to-leg voltage", main_label)
i_avrg      = Gauge("i_avrg", "Average current", main_label)
tot_p       = Gauge("tot_p", "Total Power", main_label)
tot_q       = Gauge("tot_q", "Total Reactive Power", main_label)
tot_s       = Gauge("tot_s", "Total Apparent Power", main_label)
pow_factor  = Gauge("pow_factor", "Power Factor", main_label)
demand_i1   = Gauge("demand_i1", "Leg 1 Current Demand", main_label)
demand_i2   = Gauge("demand_i2", "Leg 2 Current Demand", main_label)
demand_i3   = Gauge("demand_i3", "Leg 3 Current Demand", main_label)
demand_ia   = Gauge("demand_ia", "Average Current Demand", main_label)
demand_p    = Gauge("demand_p", "Power Demand", main_label)
demand_q    = Gauge("demand_1", "Reactive Power Demand", main_label)
thd_l1      = Gauge("thd_l1", "Leg 1 Voltage Total Harmonic Distortion", main_label)
thd_l2      = Gauge("thd_l2", "Leg 2 Voltage Total Harmonic Distortion", main_label)
thd_l3      = Gauge("thd_l3", "Leg 3 Voltage Total Harmonic Distortion", main_label)
thd_l12     = Gauge("thd_l12", "Leg 1 to Leg 2 Voltage Total Harmonic Distortion", main_label)
thd_l23     = Gauge("thd_l23", "Leg 2 to Leg 3 Voltage Total Harmonic Distortion", main_label)
thd_l31     = Gauge("thd_l31", "Leg 3 to Leg 1 Voltage Total Harmonic Distortion", main_label)
thd_i1      = Gauge("thd_i1", "Leg 1 Current Total Harmonic Distortion", main_label)
thd_i2      = Gauge("thd_i2", "Leg 2 Current Total Harmonic Distortion", main_label)
thd_i3      = Gauge("thd_i3", "Leg 3 Current Total Harmonic Distortion", main_label)
thd_in      = Gauge("thd_in", "Neutral Leg Current Total Harmonic Distortion", main_label)

log.info("Done setting up datapoints")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    serve(app, host="0.0.0.0", port=9584)