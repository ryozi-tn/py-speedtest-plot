import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib 
import pandas as pd
import json
import glob

def read_lines():
    files = glob.iglob("./logs/*.jsonl")
    for file in files:
        print(file)
        with open(file, "r") as fp:
            for line in fp:
                line = line.strip()
                #print(line)
                if line:
                    yield line

results = [json.loads(line) for line in read_lines()]

# 結果がエラーでないものを抽出
results = [r for r in results if r.get("error") is None]

# server.idによって結果が大きく異なるので、特定のサーバーの結果のみを抽出
SERVER_ID_LIST = [48463, 21569, 14623, 50686]
results = [r for r in results if (r.get("server") or {}).get("id") in SERVER_ID_LIST]

# pandasのDataFrameに変換
df = pd.json_normalize(results, max_level=10)

# timestampをPythonのdatetimeオブジェクトに変換
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='ignore').dt.tz_convert('Asia/Tokyo')
df['download.bandwidth'] *= 8 # Byte/sec -> bit/sec
df['upload.bandwidth'] *= 8 # Byte/sec -> bit/sec

# timestampとdownload.bandwidth, upload.bandwidthの関係をmatplotlibを使ってプロット
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_title('Internet Speed')
ax.set_xlabel('timestamp')
ax.set_ylabel('bandwidth(Mbps)')
ax.set_ylim(0, 10*1000*1000*1000)
ax.set_xlim(df['timestamp'].min(), df['timestamp'].max())
ax.plot(df['timestamp'], df['download.bandwidth'], label='download(Mbps)')
ax.plot(df['timestamp'], df['upload.bandwidth'], label='upload(Mbps)')
ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
ax.xaxis.set_tick_params(which='both', labelsize=8, pad=10, labelrotation=0, width=2, length=10, color='blue', direction='inout', bottom=False, top=False)

ax.grid(which='major', color='gray', linestyle='-', linewidth=1)
ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

ax.legend()

# y軸を1000mbps単位で区切る
ax.yaxis.set_major_locator(ticker.MultipleLocator(1000 * 1000 * 1000))

# y軸の単位をMbpsにする
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x / (1000 * 1000):.0f}'))

# グラフにマウスを乗せると、その時点のtimestampとdownload.bandwidth, upload.bandwidthが表示されるようにする
# https://matplotlib.org/3.1.1/gallery/misc/ftitle.html#sphx-glr-gallery-misc-ftitle-py
def format_coord(x, y):
    x_date = matplotlib.dates.num2date(x)
    return f'{x_date.strftime("%Y-%m-%d %H:%M:%S")}\ndownload: {y / (1000 * 1000):.2f} Mbps'

ax.format_coord = format_coord
ax.format_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
ax.format_ydata = lambda x: f'{x / (1000 * 1000):.2f} Mbps'

# pngで保存
fig.savefig('graph.png')

plt.show()
