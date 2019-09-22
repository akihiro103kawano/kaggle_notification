<参考URL>
https://github.com/reo11/Kaggle-notify/blob/master/kaggle_notify.py

<注意！>
subprocess.run時に以下のerrorが発生

UnicodeDecodeError: 'utf-8' codec can't decode byte 0xaa in position 6567: invalid start byte

⇒「errors='ignore'」を追加することでエラーが回避できた。
⇒参考：https://qiita.com/mitazet/items/adcbcc2da5b78056f256
