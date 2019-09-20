import cityflow
eng = cityflow.Engine(config_file="config/config.json", thread_num=4)
for i in range(1000):
    eng.render()
    eng.next_step()