import subprocess
import requests

# あらかじめ決めること
comp = "XXXXXX"
line_sheet = "XXXXXX"
json_file = "XXXXXX.json"
LINE_TOKEN = "XXXXXX"

def line(message):
    '''
    input: Message, line notify api token
    '''
    line_notify_api = 'https://notify-api.line.me/api/notify'
    payload = {'message': '\n' + message}
    headers = {'Authorization': 'Bearer ' + LINE_TOKEN}
    line_notify = requests.post(line_notify_api, data=payload, headers=headers)
	
#cat-in-the-dat
page = "kaggle kernels list --competition {} --sort-by dateCreated".format(comp)
#proc = subprocess.run(page, shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE)
s = subprocess.run(page, shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE).stdout.decode("utf-8",errors='ignore')

kernels = []
rows = s.split("\n")

# スペース2つでlist化、先頭/末尾のスペースを削除
for i in range(len(rows )):
    row = rows[i].split("  ")
    row = [x.strip(" ") for x in row if x]
    kernels.append(row)
    
# ヘッダとフッタを除外
kernels = kernels[2:-1]

# 使用するパラメータ
use_params = ["url", "title"]

# 古い順にする
kernels = kernels[::-1]

# dictに変える
tmp = [{} for i in range(len(kernels))]
for i, kernel in enumerate(kernels):
    for j, param in enumerate(use_params):
        tmp[i][param] = "https://kaggle.com/" + kernel[j] if param == "url" else kernel[j]
        
kernels = tmp


import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
gc = gspread.authorize(credentials)
wks = gc.open(line_sheet).sheet1

wks_values = wks.get_all_values()

if len(wks_values) == 0:
    update_list = wks.range('A2:{}{}'.format(chr(ord("A") + len(use_params) - 1), 1+len(kernels)))
    value_list = []
    for kernel in kernels:
        for param in use_params:
            value_list.append(kernel[param])
    for i, (cell, value) in enumerate(zip(update_list, value_list)):
        cell.value = value
    for i, param in enumerate(use_params):
        column = chr(ord("A") + i)
        wks.update_acell('{}1'.format(column), param)
    wks.update_cells(update_list)

    message = "スプレッドシートに新しいデータを追加しました\nhttps://docs.google.com/spreadsheets/d/{}".format(gc.open(line_sheet).id)
    line(message)
    
# 投稿が追加されているか確認
elif wks_values[-1][1] != kernels[-1]["title"]:# wks_values[-1][1] -> 最も新しいコンペ名
    index = 0
    for i, kernel in enumerate(kernels):
        if wks_values[-1][1] == kernel["title"]:
            index = i
    new_kernels = kernels[index+1:]

    for kernel in new_kernels:
        message = "新しいカーネルが公開されました\n{}\n{}".format(kernel["title"], kernel["url"])
        line(message)

    value_list = []
    for kernel in new_kernels:
        for param in use_params:
            value_list.append(kernel[param])

    start = len(wks_values) + 1
    end = start + len(new_kernels) - 1
    update_list = wks.range('A{}:{}{}'.format(start, chr(ord("A") + len(use_params) - 1), end))

    for i, (cell, value) in enumerate(zip(update_list, value_list)):
        cell.value = value
    wks.update_cells(update_list)
else:
    pass