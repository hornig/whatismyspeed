import speedtest
import time
import datetime
import json
import os

file_data = 'inetspeed_data.json'
file_config = 'inetspeed_config.json'
with open(file_config) as json_file:
    config = json.load(json_file)


delay_time = config["config"]["delay_time"]
time_analysis =  config["config"]["time_analysis"]
time_period = config["config"]["time_period"]

results = []

if os.path.exists(file_data) == True:
    with open(file_data) as json_file:
        data = json.load(json_file)

    results = data["data"]


servers = []
# If you want to test against a specific server
# servers = [1234]

threads = None
# If you want to use a single threaded test
# threads = 1

test = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
print(test)

while True:

    time_run = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    results_run = []

    try:

        for i in range(8):
            print("speedtest", i)
            s = speedtest.Speedtest()
            s.get_servers(servers)
            s.get_best_server()
            s.download(threads=threads)
            s.upload(threads=threads)
            s.results.share()

            results_dict = s.results.dict()

            results_run.append(results_dict)


        results.append({'timestamp': time_run, "run" : True, "result" : results_run})

    except:
        results.append({'timestamp': time_run, "run": False, "result": None})


    data = {"data" : results}
    #print(data)

    with open(file_data, 'w') as outfile:
        json.dump(data, outfile, indent=2)

    time_now = time.time()

    if time_analysis + time_period < time_now:
        print("hammer time for analysis")
        time_analysis = time_now

        config["config"]["time_analysis"] = time_analysis

        with open(file_config, 'w') as outfile:
            json.dump(config, outfile, indent=2)

    print(time_run, "waiting...")
    time.sleep(delay_time)
