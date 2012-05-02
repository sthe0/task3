#!/usr/bin/env python
# -*- coding: utf-8 -*-
class ListNode(object):
    def __init__(self, value, prev=None, next=None):
        self.value = value
        self._next = next
        self._prev = prev


class LinkedList(object):
    def __init__(self):
        self._fake_node = ListNode(None)
        self._fake_node._next = self._fake_node
        self._fake_node._prev = self._fake_node
        self.__size = 0

    def push_back(self, value):
        self.insert_before(self._fake_node, value)

    def push_front(self, value):
        self.insert_after(self._fake_node, value)

    def pop_back(self):
        if self.back() is None:
            raise ValueError("List is empty")
        value = self.back().value
        self.remove(self.back())
        return value

    def pop_front(self):
        if self.front() is None:
            raise ValueError("List is empty")
        value = self.front().value
        self.remove(self.front())
        return value

    def next(self, node=None):
        if node is None:
            node = self._fake_node
        if node._next == self._fake_node:
            return None
        return node._next

    def prev(self, node=None):
        if node is None:
            node = self._fake_node
        if node._prev == self._fake_node:
            return None
        return node._prev

    def back(self):
        return self.prev()

    def front(self):
        return self.next()

    def insert_after(self, node, value):
        new_node = ListNode(value, node, node._next)
        new_node._next._prev = new_node
        new_node._prev._next = new_node
        self.__size += 1

    def insert_before(self, node, value):
        new_node = ListNode(value, node._prev, node)
        new_node._next._prev = new_node
        new_node._prev._next = new_node
        self.__size += 1

    def remove(self, node):
        node._next._prev = node._prev
        node._prev._next = node._next
        self.__size -= 1

    def clear(self):
        while self:
            self.pop_back()

    def __iter__(self):
        cur = self._fake_node._next
        while cur != self._fake_node:
            yield cur
            cur = cur._next

    def __len__(self):
        return self.__size

