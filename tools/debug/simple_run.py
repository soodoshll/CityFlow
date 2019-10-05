import cityflow
import time
eng = cityflow.Engine(config_file="config/config.json", thread_num=4, render_host="localhost")
for i in range(1000):
    eng.render()
    eng.next_step()
    time.sleep(0.3)