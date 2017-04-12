#!/usr/bin/env python2
from argparse import ArgumentParser
import os
import json
from collections import Counter
from tqdm import tqdm
from pprint import pprint

from submit import init_turk
import records


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--prod', action='store_true', help='whether to use production or sandbox MTurk')
    parser.add_argument('--delete', action='store_true', help='whether to delete all HITs')
    parser.add_argument('--download', default='', help='if specified, downloads all HITs to the database given')
    parser.add_argument('--accept', action='store_true', help='whether to accept all HITs')
    parser.add_argument('--title_filter', default='', help='if specified, will filter HITs that contain this substring in the title')
    parser.add_argument('--extend', type=int, default=0, help='how many days to extend expiration by')
    args = parser.parse_args()
    print(args)

    connection = init_turk(prod=args.prod)
    counts = Counter()

    header = ['AssignmentId', 'AcceptTime', 'AssignmentStatus', 'HITId', 'SubmitTime', 'WorkerId', 'example_id']
    # other fields you want to dump to database
    header += []

    if args.download:
        db = records.Database('sqlite:///{}'.format(args.download))
        db.query('drop table if exists assignments')

    for hit in tqdm(connection.get_all_hits()):
        if args.title_filter and args.title_filter not in hit.Title:
            continue
        counts['hit_' + hit.HITStatus] += 1
        for a in connection.get_assignments(hit.HITId):
            counts['assignment_' + a.AssignmentStatus] += 1

            row = {form.qid: form.fields[0] for form in a.answers[0]}
            row.update({k: getattr(a, k) for k in ['AcceptTime', 'AssignmentStatus', 'HITId', 'SubmitTime', 'WorkerId', 'AssignmentId']})

            if args.download:
                if header is None:
                    header = list(sorted(list(row.keys())))
                    s = ', '.join(['{} {}'.format(c, 'text primary key' if c == 'AssignmentId' else 'text') for c in header])
                    db.query('create table assignments ({})'.format(s))
                q = 'insert into assignments ({}) values ({})'.format(', '.join(header), ', '.join([':' + k for k in header]))
                db.query(q, **row)

            if a.AssignmentStatus == 'Submitted' and args.accept:
                connection.approve_assignment(a.AssignmentId, feedback='Thank you!')
                counts['action_assignment_accepted'] += 1

        if args.extend > 0:
            try:
                connection.extend_hit(hit.HITId, expiration_increment=60 * 60 * 24 * args.extend)
                counts['action_hit_extended'] += 1
            except Exception:
                raise

        if args.delete:
            try:
                connection.expire_hit(hit.HITId)
                counts['action_hit_expired'] += 1
            except Exception:
                pass
            try:
                connection.dispose_hit(hit.HITId)
                counts['action_hit_disposed'] += 1
            except Exception:
                pass

    pprint(counts)
