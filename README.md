
**Conf-Generator is a tool for specifying and exploring hyper-parameters sets in Machine Learning pipelines defined through configuration files.**

A typical configuration instance to train a model would look like this:
```yaml
model: resnet
learning_rate: 0.01
training_epochs: 10
```

With Conf-Generator it is possible to specify multiple configurations representing parameter exploration:

```yaml
model: resnet
$learning_rate: [0.01, 0.005]
$training_epochs: [10, 20]
```

The '$' prefix is used to specify the varying parameters. We can generate the configurations with the following snippet:

```python
from conf_generator import ConfGenerator

exp = ConfGenerator("some/config.yml")
for conf, summary in exp.generate():
	print(conf)
 ```
The generator generates the configurations as python dictionary objects:
```
{'learning_rate': 0.01, 'training_epochs': 10, 'model': 'resnet'}
{'learning_rate': 0.01, 'training_epochs': 20, 'model': 'resnet'}
{'learning_rate': 0.005, 'training_epochs': 10, 'model': 'resnet'}
{'learning_rate': 0.005, 'training_epochs': 20, 'model': 'resnet'}
```
The cartesian product is made over the varying parameters if those are defined using lists, we can tie them using dictionaries:

```yaml
model: resnet
$learning_rate: {a:0.01, b:0.005}
$training_epochs: [a:10, b:20]
```
This will produce:

```
{'learning_rate': 0.01, 'training_epochs': 10, 'model': 'resnet'}
{'learning_rate': 0.005, 'training_epochs': 20, 'model': 'resnet'}
```
It is also possible to nest the variations:

```yaml
model: resnet
$$learning_rate: [{a: 0.01, b: 0.001}, {a: 0.05, b: 0.005}]
$training_epochs: {a: 10, b: 20}
```
This will produce:

```
{'learning_rate': 0.01, 'model': 'resnet', 'training_epochs': 10}
{'learning_rate': 0.05, 'model': 'resnet', 'training_epochs': 10}
{'learning_rate': 0.001, 'model': 'resnet', 'training_epochs': 20}
{'learning_rate': 0.005, 'model': 'resnet', 'training_epochs': 20}
```