import os
import subprocess

from PYEVALB import scorer, parser


def pyevalb(pred_path, gold_path, result_path):
    """Use PYEVALB to score trees."""
    scorer.Scorer().evalb(gold_path, pred_path, result_path)


def evalb(evalb_dir, pred_path, gold_path, result_path, ignore_error=1000):
    """Use original EVALB to score trees."""
    evalb_dir = os.path.expanduser(evalb_dir)
    assert os.path.exists(evalb_dir), f'Do you have EVALB installed at {evalb_dir}?'
    evalb_exec = os.path.join(evalb_dir, "evalb")
    command = '{} {} {} -e {} > {}'.format(
        evalb_exec,
        pred_path,
        gold_path,
        ignore_error,
        result_path
    )
    subprocess.run(command, shell=True)
