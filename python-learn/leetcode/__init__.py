class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        # 遍历列表
        for i in range(len(nums)):
            # 计算需要找到的下一个目标数字
            res = target-nums[i]
                # 遍历剩下的元素，查找是否存在该数字
            if res in nums[i+1:]:
                # 若存在，返回答案。这里由于是两数之和，可采用.index()方法
                # 获得目标元素在nums[i+1:]这个子数组中的索引后，还需加上i+1才是该元素在nums中的索引
                return [i, nums[i+1:].index(res)+i+1]

if __name__ == '__main__':

    pass