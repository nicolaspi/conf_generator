import yaml
import abc
import itertools
import copy


class ParamsSet(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, context, params):
        self._params = params
        self.context = context if context else {''}

    @abc.abstractmethod
    def generator(self):
        raise NotImplementedError()

    def context_generator(self):
        for c in sorted(self.context):
            yield c

    def is_matching_context(self, context):
        if context.intersection(self.context):
            return True
        return False


class ListElement(list):

    def __init__(self, seq=()):
        super(ListElement, self).__init__(seq)


class AtomicParam(ParamsSet):

    def __init__(self, context, params):
        super(AtomicParam, self).__init__(context, params)

    def generator(self):
        yield self._params


class VaryingParam(ParamsSet):

    def __init__(self, context, params):
        super(VaryingParam, self).__init__(context, params)

    def generator(self):
        if isinstance(self._params, dict):
            generators = []
            keys = []
            for k, v in sorted(self._params.items()):
                generators.append(v.generator())
                keys.append(k)
            value = {}
            for e in itertools.product(*generators):
                for k, v in zip(keys, e):
                    value[k] = v
                yield value
        elif isinstance(self._params, ParamsSet):
            for v in self._params.generator():
                yield v
        elif isinstance(self._params, list):
            for v in self._params:
                yield v
        else:
            raise ValueError("invalid params")


class ConfGenerator(object):
    def __init__(self, config, varying_param_prefix='$', context=None):
        if context is None:
            context = set([])
        if isinstance(config, str):
            with open(config, 'r') as file:
                config = yaml.load(file)
        self._config = config
        self._context = context
        self._varying_param_prefix = varying_param_prefix
        self._params_dict = None
        self._demangle_conf()
        self._degree = self._get_degree(self._config, 0)

    def _demangle_conf(self):
        params = self._demangle_param(None, self._config, parents=[], recurse=True)
        self._params_dict = params

    def _demangle_param(self, key, value, parents, recurse=True):
        if key is not None and key.startswith(self._varying_param_prefix) and recurse:
            if isinstance(value, dict):
                param_sets = ListElement()
                for k, v in sorted(value.items()):
                    if parents:
                        new_parents = list(itertools.product(parents, k.split('|')))
                    else:
                        new_parents = k.split('|')

                    param_set = self._demangle_param(key[1:], v, new_parents, recurse=False)
                    if isinstance(param_set, list):
                        param_sets.extend(param_set)
                    else:
                        param_sets.append(param_set)
                return param_sets

            elif isinstance(value, list):
                context = set(parents)
                return ListElement([VaryingParam(context, value)])
            else:
                raise ValueError("value is of incorrect type, your configuration is inconsistent")
        else:
            if not recurse:
                context = set(parents)
                return AtomicParam(context, value)
            else:
                if isinstance(value, dict):
                    dict_ = {}
                    for k, v in sorted(value.items()):
                        params = self._demangle_param(k, v, parents, recurse)
                        trimed_key = k[1:] if k.startswith(self._varying_param_prefix) else k
                        dict_[trimed_key] = params
                    return dict_
                elif isinstance(value, list):
                    list_ = []
                    for v in value:
                        params = self._demangle_param(None, v, parents, recurse)
                        list_.append(params)
                    return list_
                else:
                    context = set(parents)
                    return AtomicParam(context, value)

    def _get_degree(self, value, degree):
        if isinstance(value, dict):
            for k, v in sorted(value.items()):
                degree = max(len(k) - len(k.lstrip(self._varying_param_prefix)), degree)
                degree = max(self._get_degree(v, 0) + degree, degree)
            return degree
        if isinstance(value, list):
            for v in value:
                return self._get_degree(v, degree)
        return degree

    @staticmethod
    def _get_union_context_generator(param_sets):
        contexts = []
        for p in param_sets:
            if isinstance(p, dict):
                [contexts.extend(c.context) for _, c in sorted(p.items())]
            elif isinstance(p, list):
                [contexts.extend(c.context) for c in p]
            else:
                contexts.extend(p.context)
        context_set = set(contexts)
        for c in sorted(context_set):
            yield c

    def _get_context_generators(self, value, context_generators):
        if isinstance(value, ParamsSet):
            context_generators.append(value.context_generator())
        elif isinstance(value, ListElement):
            context_generators.append(self._get_union_context_generator(value))
        elif isinstance(value, dict):
            for _, v in sorted(value.items()):
                self._get_context_generators(v, context_generators)
        elif isinstance(value, list):
            for v in value:
                self._get_context_generators(v, context_generators)
        else:
            raise ValueError()

    @staticmethod
    def _get_product_generator(param_sets):
        gens = [p.generator() for p in param_sets]
        for sets in itertools.product(*gens):
            for e in sorted(sets):
                yield e

    def _get_generators(self, dict_, key, context, references, summary_references, generators):
        value = dict_[key]
        if isinstance(value, ParamsSet):
            generator = value.generator()
            generators.append(generator)
            references.append((dict_, key))
        elif isinstance(value, list):
            # retain all fiting contexts:
            param_sets = []
            if isinstance(value, ListElement):
                if not key.startswith(self._varying_param_prefix):
                    summary_references.append((dict_, key))
                for v in value:
                    if v.is_matching_context(context):
                        param_sets.append(v)
                if len(param_sets) > 1:
                    # inconsistency
                    param_sets = []
                elif not param_sets:
                    # No matching, keep all sets
                    param_sets = value
                generator = self._get_product_generator(param_sets)
                generators.append(generator)
                references.append((dict_, key))
            else:
                for i, k in enumerate(value):
                    self._get_generators(value, i, context, references, summary_references, generators)
        elif isinstance(value, dict):
            for k in sorted(value.keys()):
                self._get_generators(value, k, context, references, summary_references, generators)
        else:
            raise ValueError()

    def generate(self):
        context_generators = []
        self._get_context_generators(self._params_dict, context_generators)

        for context in itertools.product(*context_generators):
            context_set = set(context).union(self._context)
            config = copy.deepcopy(self._params_dict)
            generators = []
            references = []
            summary_references = []
            for k in sorted(config.keys()):
                self._get_generators(config, k, context_set, references, summary_references, generators)
            for values in itertools.product(*generators):
                for ref, v in zip(references, values):
                    ref[0][ref[1]] = v
                summary = {}
                for ref in summary_references:
                    if ref[1] in summary:
                        proxy_key = ref[1] + '$' + str(
                            len([k for k in sorted(summary.keys()) if k == ref[1] or k.startswith(ref[1] + '$')]))
                    else:
                        proxy_key = ref[1]
                    summary[proxy_key] = ref[0][ref[1]]

                if self._degree > 1:
                    exp_gen = ConfGenerator(copy.deepcopy(config), self._varying_param_prefix,
                                            copy.deepcopy(context_set))
                    for _config, _summary in exp_gen.generate():
                        csummary = copy.deepcopy(summary)
                        for k, v in sorted(_summary.items()):
                            if k in csummary:
                                proxy_key = k + '$' + str(len(
                                    [key for key in sorted(csummary.keys()) if key == k or key.startswith(k + '$')]))
                            else:
                                proxy_key = k
                            csummary[proxy_key] = v
                        yield _config, csummary
                else:
                    yield config, summary
