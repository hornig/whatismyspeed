import speedtest
import time
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime
import os
from mastodon import Mastodon
import tweepy


def send_toot(MASTODON_ACCESS_TOKEN, MASTODON_API_BASE_URL, text, filenames):
    try:
        mastodon = Mastodon(
            access_token=MASTODON_ACCESS_TOKEN,
            api_base_url=MASTODON_API_BASE_URL
        )
        #mastodon.toot(text)

        #media1 = mastodon.media_post("space_status.jpg", "image/jpeg", description="jpg")
        #media2 = mastodon.media_post("space_status.png", "image/png", description="png")
        #[media1, media2]

        media = []
        for i in range(len(filenames)):
            media.append(mastodon.media_post(filenames[i], "image/png", description="png"))

        mastodon.status_post(text, media_ids=media)
    except:
        print("not send")



def send_tweet(twitter_api, text, filenames):
    try:

        #filenames = ['space_status.jpg', 'space_status.png']
        media_ids = []
        for filename in filenames:
            res = twitter_api.media_upload(filename)
            media_ids.append(res.media_id)

        # Tweet with multiple images
        twitter_api.update_status(status=text, media_ids=media_ids)
        # same text as before cannot be posted!
    except:
        print("did not tweet")


def update_json(file_configure_path, data_config):
    with open(file_configure_path, 'w') as f:
        json.dump(data_config, f, indent=4)

def load_json(file_configure_path):
    with open(file_configure_path, 'r') as f:
        data_config = json.load(f)

    return data_config

def do_graph(file_data, d, file_graph):


    with open(file_data) as json_file:
        data = json.load(json_file)

    results = data["data"]

    #print("mmmm", len(results))

    timestamp = []
    down_min = []
    down_mean = []
    down_max = []

    up_min = []
    up_mean = []
    up_max = []

    for i in range(len(results)):
        if results[i]["result"] != None:
            result = results[i]["result"]

            down = []
            up = []

            for j in range(len(result)):
                down.append(result[j]["download"])
                up.append(result[j]["upload"])

            #print(down)
            #print(up)

            mean_down = np.mean(down)
            min_down = np.min(down)
            max_down = np.max(down)

            mean_up = np.mean(up)
            min_up = np.min(up)
            max_up = np.max(up)


            down_max.append(max_down)
            down_min.append(min_down)
            down_mean.append(mean_down)

            up_max.append(max_up)
            up_min.append(min_up)
            up_mean.append(mean_up)

            timestamp.append(datetime.datetime.strptime(results[i]["timestamp"][:-6], '%Y-%m-%dT%H:%M:%S.%f'))


    out_down_max = []
    out_down_min = []
    out_down_mean = []
    out_up_max = []
    out_up_min = []
    out_up_mean = []
    out_timestamp = []

    for t in range(len(timestamp)):
        # only seven days before
        if d - datetime.timedelta(7) <= timestamp[t] <= d:
            out_down_max.append(down_max[t])
            out_down_min.append(down_min[t])
            out_down_mean.append(down_mean[t])
            out_up_max.append(up_max[t])
            out_up_min.append(up_min[t])
            out_up_mean.append(up_mean[t])
            out_timestamp.append(timestamp[t])

    #print(timestamp)

    plt.subplots_adjust(bottom=0.2)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)

    out_down_min_str = str(np.round(np.mean(out_down_min) / 1000000, 2))
    out_down_max_str = str(np.round(np.mean(out_down_max) / 1000000, 2))
    out_down_mean_str = str(np.round(np.mean(out_down_mean) / 1000000, 2))
    out_up_min_str = str(np.round(np.mean(out_up_min) / 1000000, 2))
    out_up_max_str = str(np.round(np.mean(out_up_max) / 1000000, 2))
    out_up_mean_str = str(np.round(np.mean(out_up_mean) / 1000000, 2))

    plt.plot(out_timestamp, np.divide(out_down_min, 1000000), "-", label = "down min (~" + out_down_min_str + " Mbit/s)")
    plt.plot(out_timestamp, np.divide(out_down_max, 1000000), "*-", label = "down max (~" + out_down_max_str + " Mbit/s)")
    plt.plot(out_timestamp, np.divide(out_down_mean, 1000000), "--", label = "down mean (~" + out_down_mean_str + " Mbit/s)")
    plt.plot(out_timestamp, np.divide(out_up_min, 1000000), "-", label = "up min (~" + out_up_min_str + " Mbit/s)")
    plt.plot(out_timestamp, np.divide(out_up_max, 1000000), "*-", label = "up max (~" + out_up_max_str + " Mbit/s)")
    plt.plot(out_timestamp, np.divide(out_up_mean, 1000000), "--", label = "up mean (~" + out_up_mean_str + " Mbit/s)")
    plt.legend()
    plt.grid()
    plt.title("MySpeed_Jena0 with Vodafone (Kabel-Internet)")
    plt.ylabel("up/down-links [Mbit/s]")
    plt.savefig(file_graph, dpi=400)
    #plt.show()
    plt.clf()


    return out_down_min_str, out_down_max_str, out_down_mean_str, out_up_min_str, out_up_max_str, out_up_mean_str



path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

# starting by configuring the bot
file_configure_path = dir_path + os.sep + "inetspeed_config.json"
data_config = load_json(file_configure_path)

path_graph = dir_path + os.sep + data_config["config"]["analysis"]["storage_path"]
analysis_locked = data_config["config"]["analysis"]["locked"]
analysis_weekday = data_config["config"]["analysis"]["weekday"]
analysis_hour = data_config["config"]["analysis"]["hour"]


if not os.path.exists(path_graph):
    os.makedirs(path_graph)


file_data = dir_path + os.sep + 'inetspeed_data.json'
delay_time = data_config["config"]["delay_time"]
time_analysis =  data_config["config"]["time_analysis"]
time_period = data_config["config"]["time_period"]

results = []

if os.path.exists(file_data) == True:
    with open(file_data) as json_file:
        data = json.load(json_file)

    results = data["data"]

#print(results)

servers = []
# If you want to test against a specific server
# servers = [1234]

threads = None
# If you want to use a single threaded test
# threads = 1

test = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
#print(test)

while True:

    data_config = load_json(file_configure_path)

    path_graph = dir_path + os.sep + data_config["config"]["analysis"]["storage_path"]
    analysis_locked = data_config["config"]["analysis"]["locked"]
    analysis_weekday = data_config["config"]["analysis"]["weekday"]
    analysis_hour = data_config["config"]["analysis"]["hour"]

    file_data = dir_path + os.sep + 'inetspeed_data.json'
    delay_time = data_config["config"]["delay_time"]
    time_analysis = data_config["config"]["time_analysis"]
    time_period = data_config["config"]["time_period"]

    out_down = []
    out_up = []

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

        if len(results_run) > 0:
            results.append({'timestamp': time_run, "run" : True, "result" : results_run})

            down = []
            up = []
            for k in range(len(results_run)):
                down.append(results_run[k]["download"])
                up.append(results_run[k]["upload"])

            out_down = [np.min(down), np.max(down), np.mean(down)]
            out_up = [np.min(up), np.max(up), np.mean(up)]

        else:
            results.append({'timestamp': time_run, "run": False, "result": None})

    except:
        results.append({'timestamp': time_run, "run": False, "result": None})


    data = {"data" : results}
    #print("ggg")
    #print(data)
    #print("ggg")

    with open(file_data, 'w') as outfile:
        json.dump(data, outfile, indent=2)

    time_now = time.time()


    d = datetime.datetime.now()
    file_graph = path_graph + os.sep + "T".join(("-".join(str(d).split(".")[0].split(":"))).split(" "))+".png"

    #print(file_graph)
    #print(file_data)
    #print(analysis_weekday, analysis_hour)

    # print(d.isoweekday() in range(1, 6))
    if d.isoweekday() in analysis_weekday and d.hour in analysis_hour and analysis_locked == 0:
        out_down_min_str, out_down_max_str, out_down_mean_str, out_up_min_str, out_up_max_str, out_up_mean_str = \
            do_graph(file_data, d, file_graph)

        text = "#MySpeed weekly #Breitbandmessung @ " + str(d) + \
               " is download ~" + out_down_mean_str + " and upload ~" + out_up_mean_str + " Mbit/s on @Raspberry_Pi w/ @Speedtest. What's yours?"

        filenames = [file_graph]
        #print(filenames)


        ##################
        MASTODON_ACCESS_TOKEN = data_config["config"]["social"]["mastodon"]["access_token"]
        MASTODON_API_BASE_URL = data_config["config"]["social"]["mastodon"]["api_base_url"]

        #send_toot(MASTODON_ACCESS_TOKEN, MASTODON_API_BASE_URL, text, filenames)



        ###################
        TWITTER_CONSUMER_KEY = data_config["config"]["social"]["twitter"]["consumer_key"]
        TWITTER_CONSUMER_SECRET = data_config["config"]["social"]["twitter"]["consumer_secret"]
        TWITTER_ACCESS_KEY = data_config["config"]["social"]["twitter"]["token"]
        TWITTER_ACCESS_SECRET = data_config["config"]["social"]["twitter"]["token_secret"]

        twitter_auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        twitter_auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
        twitter_api = tweepy.API(twitter_auth)

        send_tweet(twitter_api, text, filenames)


        analysis_locked = 1
        data_config["config"]["analysis"]["locked"] = analysis_locked
        print(out_down_min_str, out_down_max_str, out_down_mean_str, out_up_min_str, out_up_max_str, out_up_mean_str)

    if (d.isoweekday() in analysis_weekday and d.hour in analysis_hour) is False:
        analysis_locked = 0
        data_config["config"]["analysis"]["locked"] = analysis_locked


    data_config["config"]["time_analysis"] = time.time()
    update_json(file_configure_path, data_config)

    data_config = load_json(file_configure_path)

    analysis_weekday = data_config["config"]["analysis"]["weekday"]
    analysis_hour = data_config["config"]["analysis"]["hour"]
    print(time_run, "waiting... until", analysis_weekday, analysis_hour, np.divide(out_down, 1000000), np.divide(out_up, 1000000))
    time.sleep(delay_time)
