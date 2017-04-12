#!/usr/bin/env python2
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import ujson as json
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement, LocaleRequirement
from boto.mturk.price import Price
from tqdm import tqdm


def init_turk(prod):
    if prod:
        AMAZON_HOST = "mechanicalturk.amazonaws.com"
    else:
        AMAZON_HOST = "mechanicalturk.sandbox.amazonaws.com"

    return MTurkConnection(
        aws_access_key_id=os.environ['MTURK_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['MTURK_AWS_SECRET_ACCESS_KEY'],
        host=AMAZON_HOST,
    )


def get_qualifications(prod):
    qualifications = Qualifications()
    if args.prod:
        qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value=str(95)))
        qualifications.add(NumberHitsApprovedRequirement(comparator="GreaterThan", integer_value=str(500)))
        # these location constraints are potentially useful
        # qualifications.add(LocaleRequirement(comparator="NotEqualTo", locale="your country code", required_to_preview=True))
        # qualifications.add(LocaleRequirement(comparator="EqualTo", locale="your country code", required_to_preview=True))
    return qualifications


def get_form(app_name, example_id, **options):
    url = "https://{}.herokuapp.com/example/{}".format(app_name, example_id)
    if options:
        url = url + '?' + '&'.join(['{}={}'.format(k, v) for k, v in options.items()])
    question_form = ExternalQuestion(url, 800)
    return question_form


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('app_name', default='app_name', help='name of your app for Firebase. Used to construct the url.')
    parser.add_argument('fdata', help='data file to use, each line is a json for an example, with an id field')
    parser.add_argument('--fconfig', default='turk.config.json', help='MTurk HIT configuration.')
    parser.add_argument('--prod', action='store_true', help='whether to use production')
    parser.add_argument('--price', type=float, default=0.25, help='price per HIT')
    parser.add_argument('--copies', type=int, default=1, help='how many copies per HIT?')
    parser.add_argument('--duration', type=int, default=60*60*3, help='how many seconds per HIT, defaults to 3 hours.')
    parser.add_argument('--debug_hits', type=int, default=3, help='how many HITs to submit if in sandbox mode.')
    args = parser.parse_args()
    print(args)

    connection = init_turk(prod=args.prod)
    qualifications = get_qualifications(prod=args.prod)

    with open(args.fconfig, 'rt') as f:
        hit_config = json.load(f)

    with open(args.fdata, 'r') as f, open(args.fdata.replace('.json', '.hits.json'), 'w') as fout:
        data = json.load(f)['examples']
        e_ids = sorted(list(data.keys()))
        for i, example_id in tqdm(enumerate(e_ids)):
            if not args.prod and i >= args.debug_hits:
                print('stopping after {} HITs because I\'m in Sandbox mode'.format(args.debug_hits))
                break
            e = data[example_id]
            options = {}
            if args.prod:
                options['prod'] = True

            # show tables
            create_hit_result = connection.create_hit(
                duration=args.duration,
                max_assignments=args.copies,  # one copy
                question=get_form(args.app_name, example_id, **options),
                reward=Price(amount=args.price),
                # Determines information returned by method in API, not super important
                response_groups=('Minimal', 'HITDetail'),
                qualifications=qualifications,
                **hit_config
            )
            fout.write(json.dumps({'id': example_id, 'hits': [h.HITId for h in create_hit_result]}) + '\n')
