"""排序相关算法"""

import typing as _t


@_t.overload
def sequential_search(lst, item, start=0, stop=None, key=None) -> _t.Union[int, None]:
    ...


@_t.overload
def sequential_search(lst, item, start=0, stop=None, key=None, insertion=True) -> int:
    ...


@_t.overload
def binary_search(lst, item, low=0, high=None, key=None) -> _t.Union[int, None]:
    ...


@_t.overload
def binary_search(lst, item, low=0, high=None, key=None, insertion=True) -> int:
    ...


def sequential_search(lst, item, start=0, stop=None, key=None, insertion=False):
    """顺序查找"""
    found = False
    if stop is None:
        stop = len(lst)
    for index in range(start, stop):
        value = lst[index]
        if key:
            value = key(value)
        if item <= value:
            if item == value:
                found = True
            break
    else:
        index = len(lst)
    return index if found or insertion else None


def binary_search(lst, item, low=0, high=None, key=None, insertion=False):
    """二分查找"""
    found = False
    mid = low
    if high is None:
        high = len(lst) - 1
    while low <= high:
        mid = (low + high) // 2
        value = lst[mid]
        if key:
            value = key(value)
        if item > value:
            low = mid = mid + 1
        elif item < value:
            high = mid - 1
        else:
            found = True
            break
    return mid if found or insertion else None


def bubble_sort(lst):
    """冒泡排序"""
    keys = list(lst)
    for i in range(len(keys) - 1, 0, -1):
        for j in range(0, i):
            k = j + 1
            if keys[j] > keys[k]:
                keys[j], keys[k] = keys[k], keys[j]
    return keys


def selection_sort(lst):
    """选择排序"""
    keys = list(lst)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if keys[i] > keys[j]:
                keys[i], keys[j] = keys[j], keys[i]
    return keys


def insertion_sort(lst):
    """插入排序"""
    keys = list(lst)
    for i in range(0, len(keys) - 1):
        j = i + 1
        while keys[i] > keys[j]:
            keys[i], keys[j] = keys[j], keys[i]
            if not i:
                break
            i, j = i - 1, i
    return keys


def quick_sort(lst, left=0, right=None, key=None):
    """快速排序
    非递归 元素交换实现
    """
    if right is None:
        right = len(lst) - 1
    orient = True
    pointer_list = [(left, right)]
    lst = list(lst)
    keys = [key(i) for i in lst] if key else lst
    key = key is not None
    while pointer_list:
        pl, pr = left, right = pointer_list.pop()
        while pl < pr:
            if keys[pl] > keys[pr]:
                keys[pl], keys[pr] = keys[pr], keys[pl]
                if key:
                    lst[pl], lst[pr] = lst[pr], lst[pl]
                orient = not orient
            if orient:
                pr -= 1
            else:
                pl += 1
        pl, pr = pl - 1, pr + 1
        if left < pl:
            pointer_list.append((left, pl))
        if pr < right:
            pointer_list.append((pr, right))
    return lst


def quick_sort2(lst, left=0, right=None):
    """快速排序
    递归实现
    """
    if right is None:
        right = len(lst) - 1
    if right - left > 1:
        border_left, border_right = left, right
        pivot = lst[left]
        while left < right:
            while left < right and lst[right] >= pivot:
                right -= 1
            lst[left] = lst[right]
            while left < right and lst[left] <= pivot:
                left += 1
            lst[right] = lst[left]
        lst[left] = pivot
        quick_sort2(lst, border_left, left - 1)
        quick_sort2(lst, right + 1, border_right)


def quick_sort3(lst, left=0, right=None):
    """快速排序
    非递归元素覆盖实现
    """
    if right is None:
        right = len(lst) - 1
    pointer_list = [(left, right)]
    while pointer_list:
        left, right = border_left, border_right = pointer_list.pop()
        pivot = lst[left]
        while left < right:
            while left < right and lst[right] >= pivot:
                right -= 1
            lst[left] = lst[right]
            while left < right and lst[left] <= pivot:
                left += 1
            lst[right] = lst[left]
        lst[left] = pivot
        left, right = left - 1, right + 1
        if border_left < left:
            pointer_list.append((border_left, left))
        if right < border_right:
            pointer_list.append((right, border_right))


def radix_sort(lst):
    """基数排序."""
    lst = list(lst)
    buckets = [[] for _ in range(10)]
    b1 = 10
    b2 = 1
    for _ in range(len(str(max(lst)))):
        for i in lst:
            buckets[(i%b1 - i%b2) // b2].append(i)
        lst = [j for i in buckets for j in i]
        for i in buckets:
            i.clear()
        b1, b2 = b1 * 10, b1
    return lst


class Sort(object):
    """插入排序，从小到大."""

    def __init__(self, lst=(), key=None):
        self.data = sorted(lst, key=key) if lst else []
        self.key = key

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.data)

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.data)

    def __bool__(self):
        return bool(self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __reversed__(self):
        return reversed(self)

    def __contains__(self, item):
        return item in self.data

    def get_list(self):
        """获取列表."""
        return self.data

    def length(self):
        """长度."""
        return len(self.data)

    def find(self, value, key=None):
        """查找元素."""
        if key:
            for index, i in enumerate(self.data):
                if key(i) == value:
                    return index
            return None
        return binary_search(self.data, value, key=self.key)

    def add(self, value):
        """添加."""
        index = binary_search(self.data, self.key(value) if self.key else value,
                              key=self.key, insertion=True)
        self.data.insert(index, value)
        return index

    def remove(self, value):
        try:
            self.data.remove(value)
        finally:
            pass

    def delete(self, start, stop=None):
        """删除."""
        if stop is None:
            del self.data[start]
        else:
            del self.data[start:stop]

    def clear(self):
        """清空."""
        self.data.clear()
