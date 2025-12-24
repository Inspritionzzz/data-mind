from typing import List


def f1():
    author = 'jason'
    print('legend, {}'.format(author))

    student, teacher = 'Tom', 'Jason'
    student, teacher = teacher, student

    print(student)
    print(locals())
    pass


# 使用类型注解
def remove_element(items: List[int]):
    """删除元素
    :param items: 元素列表
    :return: 返回结果
    """

    pass


if __name__ == '__main__':
    f1()
    #remove_element([1, 2, 3, 4])
