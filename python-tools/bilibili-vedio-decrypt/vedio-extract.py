
import os
import shutil


def extract_files_from_folders(folder_path, destination_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_path, file)

            if file_path != destination_file_path:
                # 获取源文件的文件名和扩展名
                file_name, file_extension = os.path.splitext(file)

                # # 筛选视频文件
                # if file_extension != ".mp4":
                #     continue

                # 构建目标文件路径
                count = 1
                while True:
                    new_file_path = os.path.join(destination_path, f"{file_name}_{count}{file_extension}")
                    if not os.path.exists(new_file_path):
                        break
                    count += 1

                # 复制文件到目标路径
                shutil.copy(file_path, new_file_path)
    print('finish')

# 指定文件夹路径和目标路径

folder_path = r"D:\\Users\\jason\\Desktop\\记录\\学习-技术文档_书籍\\bilibili\\58666880"
destination_path = r"D:\\Users\\jason\\Desktop\\记录\\学习-技术文档_书籍\\bilibili\\select"
# destination_path = r"D:\\Users\\jason\\Desktop\\github\\awesome-python\\python-learn\\bilibili-vedio-decrypt"



# 调用函数提取并存储文件
extract_files_from_folders(folder_path, destination_path)



# def get_video_files(folder_path):
#     video_files = glob.glob(os.path.join(folder_path, '*.mp4'))
#     return video_files
#
#
# if __name__ == '__main__':
#     folder_path = 'D:\\Users\\jason\\Desktop\\记录\\学习-技术文档_书籍'
#     video_files = get_video_files(folder_path)
#
#     for video_file in video_files:
#         print(os.path.basename(video_file))
