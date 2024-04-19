import os
import re
from tkinter import Tk, Button, Label, Listbox, Scrollbar, filedialog
from Pinyin2Hanzi import DefaultDagParams, DefaultHmmParams, dag, viterbi
import opencc

selected_files = []

def split_file_name(file_name):
    # 先將檔名根據括弧內外與"-"符號前後部分進行切割
    parts = re.split(r'(\(.*?\))|(-)', file_name)
    # 移除 None
    parts = [part for part in parts if part]
    # 根據標點符號分割各個數組
    split_parts = []
    for part in parts:
        split_parts.extend(re.split(r'(?=[^\w\s])|(?<=[^\w\s])', part))
    return split_parts

def convert_to_chinese(parts):
    # 將檔案名稱中包含英文字母的部分轉換成繁體中文，其他部分維持原樣
    dag_params = DefaultDagParams()
    hmm_params = DefaultHmmParams()
    chinese_parts = []
    converter = opencc.OpenCC('s2twp.json')  # 從簡體中文轉換為台灣正體繁體中文
    for part in parts:
        if re.search(r'[a-zA-Z]', part):
            # 如果部分包含英文字母，则根据空格分割成单词
            # 移除空格和标点符号
            cleaned_part = re.sub(r'[^\w\s]|(_)|(\s)', '', part)
            # 根据大写字母分割成列表，并将大写字母转换为小写字母
            uppercase_words = re.findall(r'[A-Z][^A-Z]*', cleaned_part)
            lowercase_words = [word.lower() for word in uppercase_words]
            part_list = lowercase_words
            # 尝试将部分转换成中文
            #print(part_list)
            
            if not part_list:
                chinese_parts.append(part)
                continue

            #检查 part_list 中的每个拼音字符串是否在字典中
            valid_part_list = []
            for pinyin in part_list:
                if len(pinyin) <= 6:
                    if pinyin in hmm_params.py2hz_dict:
                        valid_part_list.append(pinyin)
                        #print(part_list)
                    else:
                        result = dag(dag_params, valid_part_list, path_num=1, log=True)
                        #result = viterbi(hmm_params, valid_part_list, path_num=1, log=True)
                        valid_part_list.clear()
                        
                        # 如果转换成功，则添加转换后的中文，否则保持原样
                        if result:
                            chinese_part = ''.join([re.sub(r'[\s]', '', word) for word in result[0].path])
                            #print(chinese_part)
                            # 将簡體中文轉換為繁體中文
                            chinese_part = converter.convert(chinese_part)
                            chinese_parts.append(chinese_part)
                        else:
                            chinese_parts.append(pinyin)
                        
            result = dag(dag_params, valid_part_list, path_num=1, log=True)
            #result = viterbi(hmm_params, valid_part_list, path_num=1, log=True)
            # 如果转换成功，则添加转换后的中文，否则保持原样
            if result:
                chinese_part = ''.join([re.sub(r'[\s]', '', word) for word in result[0].path])
                #print(chinese_part)
                # 将簡體中文轉換為繁體中文
                chinese_part = converter.convert(chinese_part)
                chinese_parts.append(chinese_part)
            else:
                chinese_parts.append(part)
                        
        else:
            # 如果部分不包含英文字母，则直接添加到结果列表中
            chinese_parts.append(part)
    return chinese_parts

def batch_convert():
    global selected_files
    directory_path = directory_label.cget("text")
    #converted_listbox.delete(0, "end")  # 清空轉換後的檔案列表
    for file_name in selected_files:
        old_path = os.path.join(directory_path, file_name)
        if os.path.isfile(old_path):
            parts = split_file_name(file_name)
            chinese_parts = convert_to_chinese(parts)
            # 确保所有元素都是字符串类型
            chinese_parts = [str(part) for part in chinese_parts]
            new_name = ''.join(chinese_parts)
            new_path = os.path.join(directory_path, new_name)
            # 检查目标文件是否已存在，如果存在，则修改目标文件名
            num = 0
            base_name, ext = os.path.splitext(new_name)
            while os.path.exists(new_path):
                num = num + 1      
                new_name = base_name + "_" + str(num) + ext
                new_path = os.path.join(directory_path, new_name)
            os.rename(old_path, new_path)
            # 在檔案重命名後，將轉換後的檔案名稱添加到 converted_listbox 中
            #converted_listbox.insert("end", f"檔案 '{file_name}' 名稱已修改為 '{new_name}'")
        #else:
            #converted_listbox.insert("end", f"'{file_name}' 不是檔案，跳過處理")
    selected_files = []

def choose_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        directory_label.config(text=directory_path)
        update_file_list(directory_path)

def update_file_list(directory_path):
    file_listbox.delete(0, "end")
    files = os.listdir(directory_path)
    for file_name in files:
        file_listbox.insert("end", file_name)

def on_select(event):
    global selected_files
    widget = event.widget
    selected_files = [widget.get(idx) for idx in widget.curselection()]

# 建立 Tkinter 視窗
root = Tk()
root.title("拼音轉換成中文")

# 選擇目錄按鈕
choose_button = Button(root, text="選擇目錄", command=choose_directory)
choose_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")

# 顯示已選擇的目錄
directory_label = Label(root, text="")
directory_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")

# 檔案列表
file_listbox = Listbox(root, selectmode="multiple", width=50, height=10)
file_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
file_scrollbar = Scrollbar(root, orient="vertical")
file_scrollbar.config(command=file_listbox.yview)
file_scrollbar.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="ns")
file_listbox.config(yscrollcommand=file_scrollbar.set)
file_listbox.bind("<<ListboxSelect>>", on_select)

# 批次轉換按鈕
convert_button = Button(root, text="批次轉換", command=batch_convert)
convert_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# 轉換後的檔案列表
#converted_listbox = Listbox(root, width=50, height=10)
#converted_listbox.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")
#converted_scrollbar_y = Scrollbar(root, orient="vertical")
#converted_scrollbar_y.config(command=converted_listbox.yview)
#converted_scrollbar_y.grid(row=1, column=3, padx=(0, 10), pady=5, sticky="ns")
#converted_scrollbar_x = Scrollbar(root, orient="horizontal")
#converted_scrollbar_x.config(command=converted_listbox.xview)
#converted_scrollbar_x.grid(row=2, column=2, padx=10, pady=(0, 5), sticky="ew")
#converted_listbox.config(yscrollcommand=converted_scrollbar_y.set, xscrollcommand=converted_scrollbar_x.set)


# 配置列和行使得控件可以拉伸
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(2, weight=1)

# 啟動主迴圈
root.mainloop()
