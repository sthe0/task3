#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from linkedlist import LinkedList
from rulebuilder import *

class TestLinkedList(unittest.TestCase):
    def test_empty_list(self):
        llist = LinkedList()
        self.assertEqual(len(llist), 0)
        self.assertIsNone(llist.next())
        self.assertIsNone(llist.prev())
        self.assertEqual(llist.prev(), llist.back())
        self.assertEqual(llist.next(), llist.front())
        self.assertEqual(llist.back(), llist.front())
        self.assertFalse(bool(llist))

    def test_non_empty_list(self):
        llist = LinkedList()
        llist.push_back(1)
        self.assertIsNotNone(llist.next())
        self.assertIsNotNone(llist.prev())
        self.assertEqual(llist.prev(), llist.back())
        self.assertEqual(llist.next(), llist.front())
        self.assertEqual(llist.back(), llist.front())
        self.assertTrue(bool(llist))

    def test_push_back(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_back(i)
        for i, node in enumerate(llist):
            self.assertEqual(node.value, i)

    def test_push_front(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_front(i)
        for i, node in enumerate(llist):
            self.assertEqual(node.value, 9 - i)

    def test_pop_back(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_back(i)
        i = 9
        while llist:
            item = llist.pop_back()
            self.assertEqual(item, i)
            i -= 1

    def test_pop_front(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_front(i)
        i = 9
        while llist:
            item = llist.pop_front()
            self.assertEqual(item, i)
            i -= 1

    def test_remove(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_back(i)
        for item in llist:
            if item.value % 2 == 0:
                llist.remove(item)
        self.assertEqual([node.value for node in llist], range(1,10,2))

        for i in xrange(5):
            llist.remove(llist.back())
        self.assertFalse(bool(llist))

    def test_insert_after(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_back(i)
        for item in llist:
            if item.value % 2 == 0:
                llist.insert_after(item, item.value - 1)
        self.assertEqual([0,-1,1,2,1,3,4,3,5,6,5,7,8,7,9], [node.value for node in llist])

    def test_insert_before(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_back(i)
        for item in llist:
            if item.value % 2 == 0:
                llist.insert_before(item, item.value)
        self.assertEqual([0,0,1,2,2,3,4,4,5,6,6,7,8,8,9], [node.value for node in llist])

    def test_clear(self):
        llist = LinkedList()
        for i in xrange(10):
            llist.push_back(i)
        llist.clear()
        self.assertFalse(bool(llist))
        self.assertIsNone(llist.back())


class TestRuleList(unittest.TestCase):
    def test_empty_list(self):
        rlist = RuleList()
        self.assertFalse(bool(rlist))
        for item in rlist:
            self.assertTrue(False)

    def test_insert(self):
        rlist = RuleList(5)
        for i in range(10):
            rlist.insert(i, i * 100)
        self.assertEqual(len(rlist), 5)
        test_list = [(9,900), (8, 800), (7, 700), (6, 600), (5, 500)]
        self.assertEqual(list(rlist), test_list)

        rlist.insert(5, 500)
        for i in range(10, 15):
            rlist.insert(5, i * 100)
        test_list += [(5, 1000), (5, 1100), (5, 1200), (5, 1300), (5, 1400)]
        self.assertEqual(len(rlist), 10)
        self.assertEqual(list(rlist), test_list)

        rlist.insert(7, 1500)
        self.assertEqual(len(rlist), 5)
        test_list = [(9,900), (8, 800), (7, 700), (7, 1500), (6, 600)]
        self.assertEqual(test_list, list(rlist))

        rlist.insert(5, 500)
        self.assertEqual(len(rlist), 5)
        self.assertEqual(test_list, list(rlist))

        rlist.insert(7, 500)
        self.assertEqual(len(rlist), 5)
        test_list[-1] = (7, 500)
        self.assertEqual(test_list, list(rlist))

        rlist.insert(8.5, 88)
        self.assertEqual(len(rlist), 6)
        test_list = [(9,900), (8.5, 88), (8, 800), (7, 700), (7, 1500), (7, 500)]
        self.assertEqual(test_list, list(rlist))

        rlist.insert(8.5, 888)
        self.assertEqual(len(rlist), 7)
        test_list = [(9,900), (8.5, 88), (8.5, 888), (8, 800), (7, 700), (7, 1500), (7, 500)]
        self.assertEqual(test_list, list(rlist))

        rlist.insert(8.5, 8888)
        self.assertEqual(len(rlist), 5)
        test_list = [(9,900), (8.5, 88), (8.5, 888), (8.5, 8888), (8, 800)]
        self.assertEqual(test_list, list(rlist))

    def test_clear(self):
        rlist = RuleList(5)
        for i in range(10):
            rlist.insert(i, i * 10)
        rlist.clear()
        self.assertFalse(bool(rlist))
        self.assertEqual(len(rlist), 0)
        for _ in rlist:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
