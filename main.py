#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import contextlib
from rulebuilder import *

def main(argv=None):
    if argv is None:
        argv = sys.argv

    domain = Domain((CategoricalType("A11", "A12", "A13", "A14"),
                    IntegerType(),
                    CategoricalType("A30", "A31", "A32", "A33", "A34"),
                    CategoricalType("A40", "A41", "A42", "A43", "A44", "A45", "A46", "A47", "A48", "A49", "A410"),
                    IntegerType(),
                    CategoricalType("A61", "A62", "A63", "A64", "A65"),
                    CategoricalType("A71", "A72", "A73", "A74", "A75"),
                    IntegerType(),
                    CategoricalType("A91", "A92", "A93", "A94", "A95"),
                    CategoricalType("A101", "A102", "A103"),
                    IntegerType(),
                    CategoricalType("A121", "A122", "A123", "A124"),
                    IntegerType(),
                    CategoricalType("A141", "A142", "A143"),
                    CategoricalType("A151", "A152", "A153"),
                    IntegerType(),
                    CategoricalType("A171", "A172", "A173", "A174"),
                    IntegerType(),
                    CategoricalType("A191", "A192"),
                    CategoricalType("A201", "A202"),
                    IntegerType()))
    data_set = DataSet(domain)
    data_set.extend_raw(line.rstrip("\n").split() for line in open("data.txt").readlines())
    rule_builder = RuleBuilder(data_set)
    rules1S = rule_builder.build_rules(class_=1, criterion=StatisticalCriterion(), criterion_min=3, population=10)
    rules2S = rule_builder.build_rules(class_=2, criterion=StatisticalCriterion(), criterion_min=3, population=10)
    rules1E = rule_builder.build_rules(class_=1, criterion=EntropyCriterion(), criterion_min=0.2, population=10)
    rules2E = rule_builder.build_rules(class_=2, criterion=EntropyCriterion(), criterion_min=0.2, population=10)
    rules1S = [(1, key, value) for key, value in rules1S.items()][0:5]
    rules2S = [(2, key, value) for key, value in rules2S.items()][0:5]
    rules1E = [(1, key, value) for key, value in rules1E.items()][0:5]
    rules2E = [(2, key, value) for key, value in rules2E.items()][0:5]
    rulesS = sorted(rules1S + rules2S, key=(lambda x: x[2]))
    rulesE = sorted(rules1E + rules2E, key=(lambda x: x[2]))
    with contextlib.closing(open("RulesS.txt", "w")) as f:
        for item in rulesS:
            f.write("{0};{1};{2}\n".format(item[0], item[1], item[2]))
    with contextlib.closing(open("RulesE.txt", "w")) as f:
        for item in rulesE:
            f.write("{0};{1};{2}\n".format(item[0], item[1], item[2]))

#    with contextlib.closing(open("Rules1S.txt", "w")) as f:
#        for item in rules1S:
#            f.write("{0};{1};{2}\n".format(item[2], item[1], item[0]))
#    with contextlib.closing(open("Rules2S.txt", "w")) as f:
#        for item in rules2S:
#            f.write("{0};{1};{2}\n".format(item[2], item[1], item[0]))
#    with contextlib.closing(open("Rules1E.txt", "w")) as f:
#        for item in rules1E:
#            f.write("{0};{1};{2}\n".format(item[2], item[1], item[0]))
#    with contextlib.closing(open("Rules2E.txt", "w")) as f:
#        for item in rules2E:
#            f.write("{0};{1};{2}\n".format(item[2], item[1], item[0]))

    return 0


if __name__ == "__main__":
    sys.exit(main())
