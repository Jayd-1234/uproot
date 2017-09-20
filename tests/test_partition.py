#!/usr/bin/env python

# Copyright 2017 DIANA-HEP
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import numpy

import uproot
import uproot.partition

class TestPartition(unittest.TestCase):
    def runTest(self):
        pass
    
    files = ["tests/sample-5.23.02-uncompressed.root",
             "tests/sample-5.24.00-uncompressed.root",
             "tests/sample-5.25.02-uncompressed.root",
             "tests/sample-5.26.00-uncompressed.root",
             "tests/sample-5.27.02-uncompressed.root",
             "tests/sample-5.28.00-uncompressed.root",
             "tests/sample-5.29.02-uncompressed.root",
             "tests/sample-5.30.00-uncompressed.root",
             "tests/sample-6.08.04-uncompressed.root",
             "tests/sample-6.10.05-uncompressed.root"]

    check = uproot.partition.PartitionSet(
        "sample",
        {"n": numpy.dtype(">i4"), "i8": numpy.dtype(">i8"), "ai4": numpy.dtype(">i4"), "Ai2": numpy.dtype(">i2")},
        {"Ai2": "n"},
        {"ai4": (3,)},
        7,
        300,
        uproot.partition.Partition(0,
            uproot.partition.Range("tests/sample-5.23.02-uncompressed.root", 0, 30),
            uproot.partition.Range("tests/sample-5.24.00-uncompressed.root", 0, 18)),
        uproot.partition.Partition(1,
            uproot.partition.Range("tests/sample-5.24.00-uncompressed.root", 18, 30),
            uproot.partition.Range("tests/sample-5.25.02-uncompressed.root", 0, 30),
            uproot.partition.Range("tests/sample-5.26.00-uncompressed.root", 0, 6)),
        uproot.partition.Partition(2,
            uproot.partition.Range("tests/sample-5.26.00-uncompressed.root", 6, 30),
            uproot.partition.Range("tests/sample-5.27.02-uncompressed.root", 0, 24)),
        uproot.partition.Partition(3,
            uproot.partition.Range("tests/sample-5.27.02-uncompressed.root", 24, 30),
            uproot.partition.Range("tests/sample-5.28.00-uncompressed.root", 0, 30),
            uproot.partition.Range("tests/sample-5.29.02-uncompressed.root", 0, 12)),
        uproot.partition.Partition(4,
            uproot.partition.Range("tests/sample-5.29.02-uncompressed.root", 12, 30),
            uproot.partition.Range("tests/sample-5.30.00-uncompressed.root", 0, 30)),
        uproot.partition.Partition(5,
            uproot.partition.Range("tests/sample-6.08.04-uncompressed.root", 0, 30),
            uproot.partition.Range("tests/sample-6.10.05-uncompressed.root", 0, 16)),
        uproot.partition.Partition(6,
            uproot.partition.Range("tests/sample-6.10.05-uncompressed.root", 16, 30)))

    def test_make_partitions(self):
        partitionset = uproot.partition.PartitionSet.fill(self.files, "sample", ["n", "i8", "ai4", "Ai2"], under=lambda baskets: sum(x.numbytes for x in baskets) < 600, debug=False)

        self.assertEqual(partitionset, self.check)
        self.assertEqual(hash(partitionset), hash(self.check))
        self.assertEqual(uproot.partition.PartitionSet.fromJson(partitionset.toJson()), partitionset)
        self.assertEqual(uproot.partition.PartitionSet.fromJsonString(partitionset.toJsonString()), partitionset)

    def test_projections(self):
        self.assertEqual(self.check.project(3), self.check.project([3]))
        self.assertEqual(hash(self.check.project(3)), hash(self.check.project([3])))

        self.assertEqual(self.check.project([3, 4]), self.check.project(slice(3, 5)))
        self.assertEqual(hash(self.check.project([3, 4])), hash(self.check.project(slice(3, 5))))

        self.assertEqual(self.check.project(range(1, 4, 2)), self.check.project(slice(1, 4, 2)))
        self.assertEqual(hash(self.check.project(range(1, 4, 2))), hash(self.check.project(slice(1, 4, 2))))

        self.assertEqual(self.check.project([3, 4]), self.check.project(lambda p: 3 <= p.index <= 4))
        self.assertEqual(hash(self.check.project([3, 4])), hash(self.check.project(lambda p: 3 <= p.index <= 4)))

    def test_partitionset_iterator(self):
        firstpass_n = []
        firstpass_i8 = []
        firstpass_ai4 = []
        firstpass_Ai2 = []

        for arrays, partition in zip(uproot.partition.iterator(self.check), self.check.partitions):
            firstpass_n.append(arrays[b"n"])
            firstpass_i8.append(arrays[b"i8"])
            firstpass_ai4.append(arrays[b"ai4"])
            firstpass_Ai2.append(arrays[b"Ai2"])
            self.assertEqual(len(arrays[b"n"]), partition.numentries)
            self.assertEqual(len(arrays[b"i8"]), partition.numentries)
            self.assertEqual(len(arrays[b"ai4"]), partition.numentries)

        firstpass_n = numpy.concatenate(firstpass_n)
        firstpass_i8 = numpy.concatenate(firstpass_i8)
        firstpass_ai4 = numpy.concatenate(firstpass_ai4)
        firstpass_Ai2 = numpy.concatenate(firstpass_Ai2)

        secondpass_n = []
        secondpass_i8 = []
        secondpass_ai4 = []
        secondpass_Ai2 = []

        for entrystart, entryend, (n, i8, ai4, Ai2) in uproot.iterator(17, self.files, "sample", ["n", "i8", "ai4", "Ai2"], outputtype=tuple, reportentries=True):
            secondpass_n.append(n)
            secondpass_i8.append(i8)
            secondpass_ai4.append(ai4)
            secondpass_Ai2.append(Ai2)
            self.assertEqual(len(n), entryend - entrystart)
            self.assertEqual(len(i8), entryend - entrystart)
            self.assertEqual(len(ai4), entryend - entrystart)

        secondpass_n = numpy.concatenate(secondpass_n)
        secondpass_i8 = numpy.concatenate(secondpass_i8)
        secondpass_ai4 = numpy.concatenate(secondpass_ai4)
        secondpass_Ai2 = numpy.concatenate(secondpass_Ai2)
        
        self.assertTrue(numpy.array_equal(firstpass_n, secondpass_n))
        self.assertTrue(numpy.array_equal(firstpass_i8, secondpass_i8))
        self.assertTrue(numpy.array_equal(firstpass_ai4, secondpass_ai4))
        self.assertTrue(numpy.array_equal(firstpass_Ai2, secondpass_Ai2))
