# coding: utf-8
#
# Copyright 2019 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for linter_utils.py."""
from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import collections

from core.tests import test_utils
import python_utils

from . import linter_utils


class MemoizeTest(test_utils.GenericTestBase):
    """Tests for the memoize function."""

    def test_memoize_with_args(self):
        call_counter = collections.Counter()

        @linter_utils.memoize
        def count_calls(arg):
            """Counts calls made with given arg."""
            call_counter[arg] += 1

        unique_objs = (python_utils.OBJECT(), python_utils.OBJECT())
        self.assertEqual(call_counter[unique_objs[0]], 0)
        self.assertEqual(call_counter[unique_objs[1]], 0)

        count_calls(unique_objs[0])
        self.assertEqual(call_counter[unique_objs[0]], 1)
        self.assertEqual(call_counter[unique_objs[1]], 0)

        count_calls(unique_objs[0])
        count_calls(unique_objs[1])
        self.assertEqual(call_counter[unique_objs[0]], 1)
        self.assertEqual(call_counter[unique_objs[1]], 1)

    def test_memoize_with_kwargs(self):
        call_counter = collections.Counter()

        @linter_utils.memoize
        def count_calls(**kwargs):
            """Counts calls made with given kwargs."""
            hashable_kwargs = tuple(sorted(kwargs.items()))
            call_counter[hashable_kwargs] += 1

        empty_kwargs = ()
        nonempty_kwargs = (('kwarg', 0),)
        self.assertEqual(call_counter[empty_kwargs], 0)
        self.assertEqual(call_counter[nonempty_kwargs], 0)

        count_calls()
        self.assertEqual(call_counter[empty_kwargs], 1)
        self.assertEqual(call_counter[nonempty_kwargs], 0)

        count_calls()
        count_calls(kwarg=0)
        self.assertEqual(call_counter[empty_kwargs], 1)
        self.assertEqual(call_counter[nonempty_kwargs], 1)

    def test_memoize_with_kwargs_using_default_values(self):
        call_counter = collections.Counter()

        @linter_utils.memoize
        def count_calls(kwarg=0):
            """Counts calls made with given kwargs."""
            call_counter[kwarg] += 1

        self.assertEqual(call_counter[0], 0)
        count_calls()
        self.assertEqual(call_counter[0], 1)
        count_calls(kwarg=0)
        self.assertEqual(call_counter[0], 1)

    def test_memoize_with_methods(self):
        class CallCounter(python_utils.OBJECT):
            """Counts calls made to an instance."""
            def __init__(self):
                self.count = 0

            @linter_utils.memoize
            def __call__(self):
                self.count += 1

        call_counter_a, call_counter_b = CallCounter(), CallCounter()
        self.assertEqual(call_counter_a.count, 0)
        self.assertEqual(call_counter_b.count, 0)

        call_counter_a()
        self.assertEqual(call_counter_a.count, 1)
        self.assertEqual(call_counter_b.count, 0)

        call_counter_a()
        call_counter_b()
        self.assertEqual(call_counter_a.count, 1)
        self.assertEqual(call_counter_b.count, 1)

    def test_memoize_with_classmethods(self):
        class GoodCallCounter(python_utils.OBJECT):
            """Counts calls made to the class."""
            count = 0

            @classmethod
            @linter_utils.memoize
            def method_decorated_by_memoize_before_classmethod(cls):
                """memoize is called first so this def will work properly."""
                cls.count += 1

        call_counter_a, call_counter_b = GoodCallCounter(), GoodCallCounter()
        self.assertEqual(GoodCallCounter.count, 0)

        call_counter_a.method_decorated_by_memoize_before_classmethod()
        self.assertEqual(GoodCallCounter.count, 1)

        call_counter_a.method_decorated_by_memoize_before_classmethod()
        call_counter_b.method_decorated_by_memoize_before_classmethod()
        self.assertEqual(GoodCallCounter.count, 1)

        with self.assertRaisesRegexp(TypeError, 'not a Python function'):
            class BadCallCounter(python_utils.OBJECT):  # pylint: disable=unused-variable
                """Counts calls made to the class."""
                count = 0

                @linter_utils.memoize
                @classmethod
                def method_decorated_by_classmethod_before_memoize(cls):
                    """classmethods are not real functions so trying to memoize
                    them will raise a TypeError.
                    """

    def test_memoize_with_argument_values_in_different_orders(self):
        call_counter = collections.Counter()

        @linter_utils.memoize
        def count_calls(a, b, c=0, d=1):
            """Counts calls made with the given arguments."""
            key = (a, b, c, d)
            call_counter[key] += 1

        self.assertEqual(call_counter[(5, 6, 0, 1)], 0)
        self.assertEqual(call_counter[(6, 5, 0, 1)], 0)
        count_calls(5, 6)
        count_calls(6, 5)
        self.assertEqual(call_counter[(5, 6, 0, 1)], 1)
        self.assertEqual(call_counter[(6, 5, 0, 1)], 1)
        count_calls(5, 6, c=0, d=1)
        count_calls(6, 5, c=0, d=1)
        self.assertEqual(call_counter[(5, 6, 0, 1)], 1)
        self.assertEqual(call_counter[(6, 5, 0, 1)], 1)

        self.assertEqual(call_counter[(5, 6, 2, 3)], 0)
        count_calls(5, 6, c=2, d=3)
        self.assertEqual(call_counter[(5, 6, 2, 3)], 1)
        count_calls(5, 6, d=3, c=2)
        self.assertEqual(call_counter[(5, 6, 3, 2)], 0)
        self.assertEqual(call_counter[(5, 6, 2, 3)], 1)
