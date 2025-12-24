import os
import zipfile

def batch_compress_files(source_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 最大压缩文件大小，单位为字节
    max_size = 999 * 1024
    current_size = 0
    zip_index = 1
    zip_file = zipfile.ZipFile(os.path.join(output_dir, f'compressed_{zip_index}.zip'), 'w')

    # 遍历源目录下的所有文件
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)

            # 检查加入当前文件是否会超过最大大小
            if current_size + file_size > max_size:
                zip_file.close()
                zip_index += 1
                zip_file = zipfile.ZipFile(os.path.join(output_dir, f'compressed_{zip_index}.zip'), 'w')
                current_size = 0

            # 将文件添加到压缩文件中
            zip_file.write(file_path)
            current_size += file_size

    # 关闭最后一个压缩文件
    zip_file.close()

if __name__ == "__main__":
    # 更改路径
    source_directory = 'your_source_directory'
    output_directory = 'your_output_directory'
    batch_compress_files(source_directory, output_directory)