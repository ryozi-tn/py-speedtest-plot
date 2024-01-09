import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib
import matplotlib.dates
import matplotlib.gridspec
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

def load_json(line):
    try:
        return json.loads(line)
    except:
        return None

results = [load_json(line) for line in read_lines() if line is not None]

# 結果がエラーでないものを抽出
results = [r for r in results if r is not None and r.get("error") is None]

# server.idによって結果が大きく異なるので、特定のサーバーの結果のみを抽出
#SERVER_ID_LIST = [48463, 21569, 14623, 50686]
#results = [r for r in results if (r.get("server") or {}).get("id") in SERVER_ID_LIST]

# pandasのDataFrameに変換
df = pd.json_normalize(results, max_level=10)

# timestampをPythonのdatetimeオブジェクトに変換
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='ignore').dt.tz_convert('Asia/Tokyo')
df['download.bandwidth'] *= 8 # Byte/sec -> bit/sec
df['upload.bandwidth'] *= 8 # Byte/sec -> bit/sec


# timestampとdownload.bandwidth, upload.bandwidthの関係をmatplotlibを使ってプロット
fig = plt.figure(figsize=(16, 9))
gs_1 = 4
gs_2 = 1
gs = matplotlib.gridspec.GridSpec(gs_1 + gs_2,1)
ax1 = fig.add_subplot(gs[0:gs_1,0])
ax2 = fig.add_subplot(gs[gs_1,0], sharex=ax1)


ax1.set_ylabel('bandwidth(Mbps)')
ax1.set_ylim(0, 10*1000*1000*1000)
ax1.set_xlim(df['timestamp'].min(), df['timestamp'].max())
ax1.plot(df['timestamp'], df['download.bandwidth'], label='download(Mbps)', linewidth=0.75)
ax1.plot(df['timestamp'], df['upload.bandwidth'], label='upload(Mbps)', linewidth=0.75)
ax1.tick_params(labelbottom=False)

ax1.grid(which='major', color='gray', linestyle='-', linewidth=0.5)
ax1.grid(which='minor', color='gray', linestyle='-', linewidth=0.25)

ax2.set_ylabel('latency(ms)')
ax2.set_ylim(0, df['ping.latency'].quantile(0.99))
ax2.set_xlim(df['timestamp'].min(), df['timestamp'].max())
ax2.plot(df['timestamp'], df['ping.latency'], color='red', linewidth=0.5)
ax2.tick_params(labelbottom=True)

ax2.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax2.xaxis.set_minor_locator(ticker.MultipleLocator(1))
ax2.xaxis.set_tick_params(which='both', labelsize=8, pad=10, labelrotation=0, width=2, length=10, color='blue', direction='inout', bottom=False, top=False)

# timestampに日付(m/d)が被らないようにするが、年を跨ぐときだけ日付(y/m/d)を表示する
def create_format_date():
    prev = None
    def format_date(x, pos=None):
        nonlocal prev
        x_date = matplotlib.dates.num2date(x)
        is_over_year = prev is None or x_date.year != prev.year
        prev = x_date
        return x_date.strftime("%Y\n%m/%d") if is_over_year else x_date.strftime("\n%m/%d")
    return format_date
        
ax2.xaxis.set_major_formatter(ticker.FuncFormatter(create_format_date()))

ax2.grid(which='major', color='gray', linestyle='-', linewidth=0.5)

# ax,ax2の凡例をまとめて表示する
ax_handles, ax_labels = ax1.get_legend_handles_labels()
ax2_handles, ax2_labels = ax2.get_legend_handles_labels()
ax1.legend(ax_handles + ax2_handles, ax_labels + ax2_labels, loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=3)

# y軸を1000mbps単位で区切る
ax1.yaxis.set_major_locator(ticker.MultipleLocator(1000 * 1000 * 1000))

# y軸の単位をMbpsにする
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x / (1000 * 1000):.0f}'))

# グラフにマウスを乗せると、その時点のtimestampとdownload.bandwidth, upload.bandwidthが表示されるようにする
# https://matplotlib.org/3.1.1/gallery/misc/ftitle.html#sphx-glr-gallery-misc-ftitle-py
def ax1_format_coord(x, y):
    x_date = matplotlib.dates.num2date(x)
    return f'{x_date.strftime("%Y-%m-%d %H:%M:%S")} | {y / (1000 * 1000):.2f} Mbps'
ax1.format_coord = ax1_format_coord

def ax2_format_coord(x, y):
    x_date = matplotlib.dates.num2date(x)
    return f'{x_date.strftime("%Y-%m-%d %H:%M:%S")} | {y:.2f} ms'
ax2.format_coord = ax2_format_coord


# pngで保存
fig.savefig('graph.png')

plt.show()
