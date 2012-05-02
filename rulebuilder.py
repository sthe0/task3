#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
import math
import random
from heapq import *
from copy import copy


class BoolCmp(object):
    def __init__(self, precision):
        self.precision = precision

    def __call__(self, a, b):
        if a < b - self.precision:
            return -1
        if a > b + self.precision:
            return 1
        return 0


class IntegerType(object):
    def cast(self, item):
        return int(item)

    def __eq__(self, other):
        return isinstance(other, IntegerType)

    def __ne__(self, other):
        return not isinstance(other, IntegerType)


class FloatType(object):
    def cast(self, item):
        return float(item)

    def __eq__(self, other):
        return isinstance(other, FloatType)

    def __ne__(self, other):
        return not isinstance(other, FloatType)


class CategoricalType(object):
    def __init__(self, *categories):
        if len(categories) == 0:
            raise ValueError("No categories specified")
        self.__categories = set(categories)

    def get_categories(self):
        return self.__categories

    def cast(self, item):
        if item not in self.__categories:
            raise TypeError("Wrong item category")
        return item

    def __eq__(self, other):
        return isinstance(other, CategoricalType)

    def __ne__(self, other):
        return not isinstance(other, CategoricalType)


class Domain(object):
    def __init__(self, categories, has_class=True):
        self.__has_class = has_class
        if not has_class:
            self.__item_types = tuple(categories)
            self.__class_type = None
        else:
            self.__item_types = tuple(categories[0:-1])
            self.__class_type = categories[-1]

    def has_class(self):
        return self.__has_class

    def get_class_type(self):
        return self.__class_type

    def get_item_types(self):
        return self.__item_types

    def __eq__(self, other):
        if self.__class_type != other.__class_type:
            return False
        for item1, item2 in zip(self.__item_types, other.__item_types):
            if item1 != item2:
                return False
        return True


class DataEntry(object):
    def __init__(self, domain, data):
        self.__domain = domain
        self.__items = []
        self.__class = None
        if domain.has_class():
            for type_, item in zip(domain.get_item_types(), data[0:-1]):
                self.__items.append(type_.cast(item))
            self.__class = domain.get_class_type().cast(data[len(domain.get_item_types())])
        else:
            self.__items = data

    def get_items(self):
        return self.__items

    def get_class(self):
        return self.__class

    def get_domain(self):
        return self.__domain


class DataSet(object):
    def __init__(self, domain):
        self.__domain = domain
        self.__entries = []

    def append(self, entry):
        if entry.get_domain() != self.__domain:
            raise TypeError("Wrong domain")
        self.__entries.append(entry)

    def append_raw(self, raw_entry):
        entry = DataEntry(self.__domain, raw_entry)
        self.__entries.append(entry)

    def extend(self, entries):
        for entry in entries:
            self.append(entry)

    def extend_raw(self, raw_entries):
        for raw_entry in raw_entries:
            self.append_raw(raw_entry)

    def get_entries(self):
        return self.__entries

    def get_domain(self):
        return self.__domain

    def __getitem__(self, index):
        return self.__entries[index]

    def __setitem__(self, index, entry):
        if entry.get_domain() != self.__domain:
            raise TypeError("Wrong domain")
        self.__entries[index] = entry

    def __delitem__(self, index):
        del self.__entries[index]

    def __len__(self):
        return len(self.__entries)

    def __iter__(self):
        for entry in self.__entries:
            yield entry


class AbstractRule(object):
    def __init__(self, domain):
        self.__domain = domain

    def _apply_customized(self, entry):
        pass

    def apply(self, entry):
        if entry.get_domain() != self.__domain:
            raise TypeError("Wrong domain")
        return self._apply_customized(entry)

    def get_domain(self):
        return self.__domain

    @staticmethod
    def get_type():
        pass


class EquivalenceRule(AbstractRule):
    def __init__(self, domain, index, value):
        super(EquivalenceRule, self).__init__(domain)
        self.__index = index
        self.__value = domain.get_item_types()[index].cast(value)

    def _apply_customized(self, entry):
        return entry.get_items()[self.__index] == self.__value

    @staticmethod
    def is_applicable(item_type):
        return True

    @staticmethod
    def get_type():
        return 1

    def __str__(self):
        return "{0}:{1}:{{{2}}}".format(self.get_type(), self.__index + 1, self.__value)


class SetRule(AbstractRule):
    def __init__(self, domain, index, iterable):
        super(SetRule, self).__init__(domain)
        self.__index = index
        self.__set = set()
        for item in iterable:
            self.__set.add(domain.get_item_types()[index].cast(item))

    def _apply_customized(self, entry):
        return entry.get_items()[self.__index] in self.__set

    @staticmethod
    def is_applicable(item_type):
        return True

    @staticmethod
    def get_type():
        return 2

    def __str__(self):
        return "{0}:{1}:{{{2}}}".format(self.get_type(), self.__index + 1, ",".join(self.__set))


class LERule(AbstractRule):
    def __init__(self, domain, index, threshold):
        super(LERule, self).__init__(domain)
        self.__index = index
        self.__threshold = threshold

    def _apply_customized(self, entry):
        return entry.get_items()[self.__index] <= self.__threshold

    @staticmethod
    def is_applicable(item_type):
        return issubclass(item_type, IntegerType) or issubclass(item_type, FloatType)

    @staticmethod
    def get_type():
        return 3

    def __str__(self):
        return "{0}:{1}:{{{2}}}".format(self.get_type(), self.__index + 1, self.__threshold)


class GERule(AbstractRule):
    def __init__(self, domain, index, threshold):
        super(GERule, self).__init__(domain)
        self.__index = index
        self.__threshold = threshold

    def _apply_customized(self, entry):
        return entry.get_items()[self.__index] >= self.__threshold

    @staticmethod
    def is_applicable(item_type):
        return issubclass(item_type, IntegerType) or issubclass(item_type, FloatType)

    @staticmethod
    def get_type():
        return 4

    def __str__(self):
        return "{0}:{1}:{{{2}}}".format(self.get_type(), self.__index + 1, self.__threshold)


class RangeRule(AbstractRule):
    def __init__(self, domain, index, left, right):
        super(RangeRule, self).__init__(domain)
        self.__index = index
        self.__left = left
        self.__right = right

    def _apply_customized(self, entry):
        return entry.get_items()[self.__index] >= self.__left and entry.get_items()[self.__index] <= self.__right

    @staticmethod
    def is_applicable(item_type):
        return issubclass(item_type, IntegerType) or issubclass(item_type, FloatType)

    @staticmethod
    def get_type():
        return 5

    def __str__(self):
        return "{0}:{1}:{{{2},{3}}}".format(self.get_type(), self.__index + 1, self.__left, self.__right)


class Conjunction(AbstractRule):
    def __init__(self, domain, rules = ()):
        super(Conjunction, self).__init__(domain)
        self.__rules = set()
        self.extend(rules)

    def add(self, rule):
        self.__rules.add(rule)

    def extend(self, rules):
        self.__rules.update(rules)

    def apply(self, item):
        return reduce(operator.and_, (x.apply(item) for x in self.__rules))

    def remove(self, rule):
        self.__rules.remove(rule)

    def clear(self):
        self.__rules.clear()

    def copy(self):
        result = Conjunction(self.get_domain())
        result.__rules = copy(self.__rules)
        return result

    def __iter__(self):
        for rule in self.__rules:
            yield rule

    def __contains__(self, rule):
        return rule in self.__rules

    def __hash__(self):
        return reduce(operator.xor, map(id, self.__rules))

    def __eq__(self, other):
        if not isinstance(other, Conjunction):
            return False
        return self.__rules.issubset(other.__rules) and self.__rules.issuperset(other.__rules)

    def __ne__(self, other):
        if not isinstance(other, Conjunction):
            return True
        return not self.__rules.issubset(other.__rules) or not self.__rules.issuperset(other.__rules)

    def __len__(self):
        return len(self.__rules)

    @staticmethod
    def get_type():
        return 6

    def __str__(self):
        return ";".join(map(str, self.__rules))


class BinomialCoefficientLogarithmComputer(object):
    def __init__(self):
        self.__computed = {}
    def __logarithm_of_factorial(self, n):
        if n == 0:
            return 0
        if n not in self.__computed:
            self.__computed[n] = self.__logarithm_of_factorial(n - 1) + math.log(n)
        return self.__computed[n]

    def compute(self, n, k):
        return self.__logarithm_of_factorial(n) - self.__logarithm_of_factorial(k) - self.__logarithm_of_factorial(n - k)


class AbstractInformativityCriterion(object):
    def _compute_customized(self, N, P, n, p):
        pass

    def compute(self, rule, data_set, class_):
        if not data_set.get_domain().has_class():
            raise ValueError("Entry doesn't contain class column")

        N, P, n, p = 0, 0, 0, 0
        for entry in data_set:
            result = rule.apply(entry)
            if entry.get_class() == class_:
                P += 1
                if result:
                    p += 1
            else:
                N += 1
                if result:
                    n += 1

        return self._compute_customized(N, P, n, p)


class StatisticalCriterion(AbstractInformativityCriterion):
    def __init__(self):
        super(StatisticalCriterion, self).__init__()
        self.__bclc = BinomialCoefficientLogarithmComputer()

    def _compute_customized(self, N, P, n, p):
        return -(self.__bclc.compute(P, p) + self.__bclc.compute(N, n) - self.__bclc.compute(P + N, p + n))


class EntropyCriterion(AbstractInformativityCriterion):
    def __compute_entropy(self, P, N):
        if P == 0 or N == 0:
            return 0
        p1 = 1.0 * P / (P + N)
        p2 = 1.0 * N / (P + N)
        return -p1 * math.log(p1, 2) - p2 * math.log(p2, 2)

    def _compute_customized(self, N, P, n, p):
        new_entropy = 1.0 * (p + n) / (P + N) * self.__compute_entropy(p, n) + \
                      1.0 * (P + N - p - n) / (P + N) * self.__compute_entropy(P - p, N - n)
        return self.__compute_entropy(P, N) - new_entropy


class RuleHeap(object):
    def __init__(self, max_size=10):
        self.__set = set()
        self.__items = []
        self.__smallest = None
        self.__smallest_count = 0
        self.__max_size = max(max_size, 1)
        self.__cmp = BoolCmp(1e-9)

    def __count_smallest(self):
        self.__smallest_count = 0
        self.__smallest = self.top()[0]
        tmp = []
        while self.__items:
            tmp.append(heappop(self.__items))
            if self.__cmp(tmp[-1][0], self.__smallest) != 0:
                break
            self.__smallest_count += 1

        for item in tmp:
            heappush(self.__items, item)

    def push(self, informativity, rule):
        if self.__smallest_count == 0:
            self.__smallest = informativity
        if self.__cmp(self.__smallest, informativity) == 0:
            self.__smallest_count += 1
        if self.__cmp(self.__smallest, informativity) > 0:
            self.__smallest = informativity
            self.__smallest_count = 1

        if rule in self.__set:
            return
        heappush(self.__items, (informativity, rule))
        self.__set.add(rule)

        if len(self.__items) - self.__smallest_count >= self.__max_size:
            while self.__cmp(self.top()[0], self.__smallest) == 0:
                informativity, rule = heappop(self.__items)
                self.__set.remove(rule)
            self.__count_smallest()

    def pop(self):
        informativity, rule = heappop(self.__items)
        self.__smallest_count -= 1
        if self.__smallest_count == 0 and len(self.__items) > 0:
            self.__count_smallest()
        self.__set.remove(rule)
        return informativity, rule

    def top(self):
        return self.__items[0]

    def __len__(self):
        return len(self.__items)

    def __iter__(self):
        for item in copy(self.__items):
            yield item

    def __contains__(self, rule):
        return rule in self.__set


class RuleBuilder(object):
    def __init__(self, train_set, folds=5, test_fraction=0.25):
        random.seed()
        self.__folds = folds
        self.__test_fraction = test_fraction
        self.__train_set, self.__test_set = self.__separate(train_set)
        self.__simple_rules = self.__create_simple_rules()
        self.__criterion = None
        self.__max_error = None
        self.__class = None
        self.__max_rank = None

    def __separate(self, data_set):
        classes = {}
        test_set = DataSet(data_set.get_domain())
        train_set = DataSet(data_set.get_domain())
        for entry in data_set:
            class_ = entry.get_class()
            classes[class_] = classes.setdefault(class_, []) + [entry]
        for k, v in classes.items():
            train_number = int(len(v) * self.__test_fraction)
            if train_number == 0 and len(v) > 1:
                train_number = 1
            for i in range(train_number):
                rnd = random.randint(i + 1, len(v) - 1)
                v[i], v[rnd] = v[rnd], v[i]
            test_set.extend(v[0:train_number])
            train_set.extend(v[train_number:])
        return train_set, test_set

    def __create_simple_rules(self):
        rules = []
        domain = self.__train_set.get_domain()
        for index, item_type in enumerate(self.__train_set.get_domain().get_item_types()):
            if isinstance(item_type, CategoricalType):
                categories = item_type.get_categories()
                rules.append(SetRule(domain, index, categories))
                for category in item_type.get_categories():
                    rules.append(EquivalenceRule(domain, index, category))
                    if len(categories) > 2:
                        categories.remove(category)
                        rules.append(SetRule(domain, index, categories))
                        categories.add(category)

            if isinstance(item_type, IntegerType) or isinstance(item_type, FloatType):
                feature_column = sorted(set(entry.get_items()[index] for entry in self.__train_set))

                step = (len(feature_column) + self.__folds * self.__folds - 1) / (self.__folds * self.__folds)
                for i in xrange(0, len(feature_column) - 1, step):
                    threshold = (feature_column[i] + feature_column[i + 1]) / 2.0
                    rules.append(LERule(domain, index, threshold))
                    rules.append(GERule(domain, index, threshold))

                step = (len(feature_column) + self.__folds - 1) / self.__folds
                for i in xrange(0, len(feature_column) - 1, step):
                    for j in xrange(i + step, len(feature_column) - 1, step):
                        rules.append(RangeRule(domain, index, feature_column[i], feature_column[j - 1]))
                    rules.append(RangeRule(domain, index, feature_column[i], feature_column[-1]))
        return rules

    def __compute_error(self, rule, data_set):
        n, p = 0, 0
        for entry in data_set:
            if rule.apply(entry):
                if entry.get_class() == self.__class:
                    p += 1
                else:
                    n += 1
        if n == 0 and p == 0:
            return 1.0
        return 1.0 * n / (n + p)

    def __stabilize(self, conjunction):
        informativity = self.__criterion.compute(conjunction, self.__train_set, self.__class)
        new_conjunction = conjunction.copy()
        for rule1 in conjunction:
            best_rule = rule1
            for rule2 in self.__simple_rules:
                if rule2 not in conjunction:
                    new_conjunction.remove(best_rule)
                    new_conjunction.add(rule2)
                    new_informativity = self.__criterion.compute(new_conjunction, self.__train_set, self.__class)
                    error = self.__compute_error(new_conjunction, self.__train_set)
                    if new_informativity < informativity or error >= self.__max_error:
                        new_conjunction.remove(rule2)
                        new_conjunction.add(best_rule)
                    else:
                        informativity = new_informativity
                        best_rule = rule2
        conjunction = new_conjunction
        new_conjunction = conjunction.copy()
        for rule in conjunction:
            if len(new_conjunction) == 1:
                break
            new_conjunction.remove(rule)
            new_informativity = self.__criterion.compute(new_conjunction, self.__train_set, self.__class)
            error = self.__compute_error(new_conjunction, self.__train_set)
            if new_informativity < informativity or error >= self.__max_error:
                new_conjunction.add(rule)
            else:
                informativity = new_informativity
        return informativity, new_conjunction


    def __reduce(self, conjunction):
        informativity = self.__criterion.compute(conjunction, self.__test_set, self.__class)
        new_conjunction = conjunction.copy()
        for rule in conjunction:
            if len(new_conjunction) == 1:
                break
            new_conjunction.remove(rule)
            new_informativity = self.__criterion.compute(new_conjunction, self.__test_set, self.__class)
            error = self.__compute_error(new_conjunction, self.__test_set)
            if new_informativity < informativity or error >= self.__max_error:
                new_conjunction.add(rule)
            else:
                informativity = new_informativity
        error = self.__compute_error(new_conjunction, self.__train_set)
        #if error >= self.__max_error:
        #    informativity = 0.0
        #    new_conjunction = None
        return informativity, new_conjunction

    def build_rules(self,
                    class_,
                    population=10,
                    criterion=StatisticalCriterion(),
                    criterion_min=3,
                    max_error=0.4,
                    max_rank=3):

        self.__max_rank = max_rank
        self.__criterion = criterion
        self.__max_error = max_error
        self.__class = class_

        rule_heap = RuleHeap(population)
        for rule in self.__simple_rules:
            conjunction = Conjunction(self.__train_set.get_domain(), [rule])
            rule_heap.push(criterion.compute(conjunction, self.__train_set, class_), conjunction)

        for rank in range(2, self.__max_rank + 1):
            rule_improved = False
            for informativity, conjunction in rule_heap:
                if len(conjunction) == rank - 1:
                    new_conjunction = conjunction.copy()
                    for rule in self.__simple_rules:
                        if rule not in new_conjunction:
                            new_conjunction.add(rule)
                            if new_conjunction not in rule_heap:
                                new_informativity = criterion.compute(new_conjunction, self.__train_set, class_)
                                error = self.__compute_error(new_conjunction, self.__train_set)
                                if new_informativity > criterion_min and error < max_error:
                                    rule_improved = True
                                    rule_heap.push(new_informativity, new_conjunction.copy())
                            else:
                                x = 2 #debug branch
                            new_conjunction.remove(rule)
            if not rule_improved:
                break
        result = []
        while rule_heap:
            informativity, conjunction = rule_heap.pop()
            informativity, conjunction = self.__stabilize(conjunction)
            informativity, conjunction = self.__reduce(conjunction)
            if conjunction is not None:
                heappush(result, (informativity, conjunction, class_))
        return result
