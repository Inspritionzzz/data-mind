from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba  # 导入jieba模块

# 读取文本数据（替换为你的文本内容或文件路径）
text = """
包含东方财富、朝阳永续私募、同花顺数据，数据用于加工基金相关指标...
（此处省略你的原始文本，建议直接复制所有内容到这里）
"""

# 中文分词（关键：使用jieba.cut()，而非jieba()）
cut_text = jieba.cut(text)  # 正确调用分词函数
result = " ".join(cut_text)  # 用空格连接分词结果（词云默认按空格分割）

# 创建词云对象（确保字体路径正确，若无simhei.ttf可替换为系统中存在的中文字体）
wordcloud = WordCloud(
    background_color="white",
    font_path="simhei.ttf",  # 例如：Windows系统可替换为 "C:/Windows/Fonts/simhei.ttf"
    width=2400,
    height=1600,
    max_words=100000
).generate(result)

# 显示词云
plt.figure(figsize=(15, 6))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")  # 隐藏坐标轴
plt.show()

# 保存词云图
wordcloud.to_file("wordcloud_result.png")