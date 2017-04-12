from collections import namedtuple

Example = namedtuple('Example', ['original', 'good', 'bad', 'reason'])


examples = [
    Example(
        'what is 1 + 1?',
        'it is 2',
        'i think it is 5',
        'it is wrong because reasons',
    ),
]
