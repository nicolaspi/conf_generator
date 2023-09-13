import unittest
import copy
from conf_generator import ConfGenerator


class TestConfGenerator(unittest.TestCase):

    def _get_confs(self, config, prefix='$'):
        exp = ConfGenerator(config, varying_param_prefix=prefix)
        confs = []
        summaries = []
        for conf, summary in exp.generate():
            print(conf)
            confs.append(copy.deepcopy(conf))
            summaries.append(copy.deepcopy(summary))
        return confs, summaries

    def test_simple(self):
        confs, summaries = self._get_confs(config={'alpha': [1, 2]})
        assert (len(confs) == 1)

    def test_simple1(self):
        confs, summaries = self._get_confs(config = {'$alpha': [1, 2]})
        assert(len(confs) == 2)
        assert({'alpha': 2} in confs)
        assert ({'alpha': 1} in confs)

    def test_simple8(self):
        confs, summaries = self._get_confs(config = {'$alpha': [{'a': 'a'}, {'b': 'b'}]})
        assert(len(confs) == 2)
        assert({'alpha': {'a': 'a'}} in confs)
        assert ({'alpha': {'b': 'b'}} in confs)

    def test_simple9(self):
        confs, summaries = self._get_confs(config = {'$alpha': [{'a': {'$beta' : [1, 2]}}, {'b': 'b'}]})
        assert(len(confs) == 3)
        assert({'alpha': {'a': {'beta': 1}}} in confs)
        assert ({'alpha': {'a': {'beta': 2}}} in confs)
        assert ({'alpha': {'b': 'b'}} in confs)

    def test_simple2(self):
        config = {'$alpha': {'a': 1, 'b': 2}, '$beta': {'a': 1, 'b': 2}}
        confs, summaries = self._get_confs(config)
        assert(len(confs) == 2)
        assert({'alpha': 2, 'beta': 2} in confs)
        assert ({'alpha': 1, 'beta': 1} in confs)

    def test_simple3(self):
        config = {'$alpha': {'a': 1, 'b': 2}, '$beta': {'a': 1, 'b': 2}, '$gamma': {'e': 'e', 'f': 'f'}}
        confs, summaries = self._get_confs(config)
        assert(len(confs) == 4)
        assert({'alpha': 2, 'beta': 2, 'gamma': 'e'} in confs)
        assert ({'alpha': 2, 'beta': 2, 'gamma': 'f'} in confs)
        assert ({'alpha': 1, 'beta': 1, 'gamma': 'e'} in confs)
        assert ({'alpha': 1, 'beta': 1, 'gamma': 'f'} in confs)

    def test_simple4(self):
        config = {'$alpha': {'a': 1, 'b': 2, 'c': 3, 'd': 4}, '$beta': {'a|c': 1, 'b|d': 2}}
        confs, summaries = self._get_confs(config)
        assert(len(confs) == 4)
        assert({'alpha': 1, 'beta': 1} in confs)
        assert ({'alpha': 2, 'beta': 2} in confs)
        assert ({'alpha': 3, 'beta': 1} in confs)
        assert ({'alpha': 4, 'beta': 2} in confs)

    def test_simple6(self):
        config = {'$alpha': {'a': 'a', 'b': 'b'}, '$beta': {'a': 'a', 'b': 'b'}, '$gamma': {'a': 'a', 'b': 'b'}}
        confs, summaries = self._get_confs(config)
        assert(len(confs) == 2)
        assert({'alpha': 'a', 'beta': 'a', 'gamma': 'a'} in confs)
        assert ({'alpha': 'b', 'beta': 'b', 'gamma': 'b'} in confs)

    def test_simple7(self):
        config = {'$alpha': {'a': 'a', 'b': 'b'}, '$beta': {'a': {'e': 'ae', 'f': 'af'}, 'b': {'e': 'be', 'f': 'bf'}}, '$gamma': {'e': 'e', 'f': 'f'}}
        confs, summaries = self._get_confs(config)
        assert(len(confs) == 4)
        assert({'alpha': 'a', 'beta': {'e': 'ae', 'f': 'af'}, 'gamma': 'f'} in confs)
        assert ({'alpha': 'a', 'beta': {'e': 'ae', 'f': 'af'}, 'gamma': 'e'} in confs)
        assert ({'alpha': 'b', 'beta': {'e': 'be', 'f': 'bf'}, 'gamma': 'f'} in confs)
        assert ({'alpha': 'b', 'beta': {'e': 'be', 'f': 'bf'}, 'gamma': 'e'} in confs)

    def test_simple5(self):
        config = {'$alpha': {'a': 'a', 'b': 'b'}, '$$beta': {'a': {'e': 'ae', 'f': 'af'}, 'b': {'e': 'be', 'f': 'bf'}}, '$gamma': {'e': 'e', 'f': 'f'}}
        confs, summaries = self._get_confs(config)
        assert(len(confs) == 4)
        assert({'alpha': 'a', 'beta': 'af', 'gamma': 'f'} in confs)
        assert ({'alpha': 'a', 'beta': 'ae', 'gamma': 'e'} in confs)
        assert ({'alpha': 'b', 'beta': 'bf', 'gamma': 'f'} in confs)
        assert ({'alpha': 'b', 'beta': 'be', 'gamma': 'e'} in confs)

    def test_simple12(self):
        config = {'$alpha': {'a': 'a', 'b': 'b'}, 'beta': {'$alpha': [0,1]}}
        confs, summaries = self._get_confs(config)
        assert(len(summaries) == 4)
        assert({'alpha': 'b', 'alpha$1': 0} in summaries)
        assert ({'alpha': 'b', 'alpha$1': 1} in summaries)
        assert ({'alpha': 'a', 'alpha$1': 0} in summaries)
        assert ({'alpha': 'a', 'alpha$1': 1} in summaries)

    def test_simple13(self):
        config = {'$alpha': [0], 'beta': {'$alpha': [0], '$alpha_': [0]}}
        confs, summaries = self._get_confs(config)
        assert(len(summaries) == 1)
        assert({'alpha': 0, 'alpha$1': 0, 'alpha_': 0} in summaries)

    def test_simple14(self):
        config = {'$alpha': [0], '$$beta': [[{'$alpha': [0], '$alpha_': [0]}]]}
        confs, summaries = self._get_confs(config)
        assert(len(summaries) == 1)
        assert({'alpha': 0, 'alpha$1': 0, 'alpha_': 0, 'beta': {'$alpha': [0], '$alpha_':[0]}} in summaries)

    def test_simple15(self):
        config = {'1#alpha': [0], '1#1#beta': [[{'1#alpha': [0], '1#alpha_': [0]}]]}
        confs, summaries = self._get_confs(config, prefix='1#')
        assert(len(summaries) == 1)
        assert({'alpha': 0, 'alpha$1': 0, 'alpha_': 0, 'beta': {'1#alpha': [0], '1#alpha_':[0]}} in summaries)

    def test_simple16(self):
        config = {'$$beta': {'non_alpha': [16, 8, 1], 'alpha': [1]}, '$$alpha': {'non_alpha': [0.0], 'alpha': [0.001, 0.01, 0.1]}}
        confs, summaries = self._get_confs(config)
        assert (len(summaries) == 6)
        assert ({'beta': 16, 'alpha': 0.0} in summaries)
        assert ({'beta': 8, 'alpha': 0.0} in summaries)
        assert ({'beta': 1, 'alpha': 0.0} in summaries)
        assert ({'beta': 1, 'alpha': 0.001} in summaries)
        assert ({'beta': 1, 'alpha': 0.01} in summaries)
        assert ({'beta': 1, 'alpha': 0.1} in summaries)

    def test_simple10(self):
        config = {'prediction_builder_shape': [4, 4]}
        confs, summaries = self._get_confs(config)
        assert (len(confs) == 1)
        assert ({'prediction_builder_shape': [4, 4]} in confs)

    def test_simple11(self):
        config = {"alpha": [{"beta": 'value'}]}
        confs, summaries = self._get_confs(config)
        assert (len(confs) == 1)
        assert ({'alpha': [{'beta': 'value'}]} in confs)

    def test_simpleConf(self):
        file = "resources/conf.yml"
        confs, summaries = self._get_confs(file)
        assert(len(confs) == 40)

    def test_simpleConf3(self):
        file = "resources/conf3.yml"
        confs, summaries = self._get_confs(file)
        assert (len(confs) == 1)

    def test_simpleConf4(self):
        file = "resources/conf4.yml"
        confs, summaries = self._get_confs(file)
        assert (len(confs) == 1)

    def test_simpleConf2(self):
        file = "resources/conf2.yml"
        confs, summaries = self._get_confs(file)
        assert (len(confs) == 4)
        assert ({'training_epochs': 10, 'learning_rate': 0.01} in summaries)
        assert ({'training_epochs': 10, 'learning_rate': 0.05} in summaries)
        assert ({'training_epochs': 20, 'learning_rate': 0.001} in summaries)
        assert ({'training_epochs': 20, 'learning_rate': 0.005} in summaries)