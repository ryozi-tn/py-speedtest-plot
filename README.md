py-speedtest-plot
=================

speedtest-cliの結果をmatplotlibでグラフにするだけ

![描画イメージ](ss.jpg)

準備
-----------------

### speedtest-cliを導入する

https://www.speedtest.net/apps/cli

speedtest-cliの動作確認

```bash
# 近いサーバ一覧を取得
speedtest -L
```

### crontabの設定

```vasg
# 2時間毎に計測
4 */2 * * * speedtest --format=json --progress=no >> /var/log/speedtest/speedtest-$(date +\%Y\%m\%d).jsonl |& logger -t speedtest
```


cronで定期的に実行する際のログを格納するディレクトリを作成（cronを誰で実行するかに応じて所有者や権限をつける）

``` bash
mkdir /var/log/speedtest/
```


`/var/log/speedtest/speedtest*.jsonl` に実行ログが溜まっていくので、これを本プログラムでグラフにする。（1日あたり10KBぐらい）

### 実行

ログは logs に配置する。

``` python
python -m venv venv
. venv/Scripts/activate
pip install -r requirements.txt

python main.py
```

matplotlibのGUIで描画される。また画像は`graph.png`で出力される。
