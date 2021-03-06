import os

from invoke import Collection, tasks
from invoke.util import LOG_FORMAT

from steem import command as steem_cmd
from action.claim import command as claim_cmd
from action.vote import command as vote_cmd
from action.transfer import command as transfer_cmd


def add_tasks_in_module(mod, ns):
    functions = [(name, val) for name, val in mod.__dict__.items() if callable(val)]
    for (name, method) in functions:
        # only add the method if it's of type invoke.tasks.Task
        if type(method) == tasks.Task:
            ns.add_task(method, name)
    return ns

steem_ns = add_tasks_in_module(steem_cmd, Collection('steem'))
claim_ns = add_tasks_in_module(claim_cmd, Collection('claim'))
vote_ns = add_tasks_in_module(vote_cmd, Collection('vote'))
transfer_ns = add_tasks_in_module(transfer_cmd, Collection('transfer'))

ns = Collection(
    steem_ns,
    claim_ns,
    vote_ns,
    transfer_ns
)

ns.configure({'conflicted': 'default value'})
