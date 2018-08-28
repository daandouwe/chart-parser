import os
from IPython.display import Image, display
from nltk.draw import TreeWidget
from nltk.draw.util import CanvasFrame
from nltk.tree import Tree
from collections import defaultdict

def make_nltk_tree(derivation):
    """
    Return a NLTK Tree object based on the derivation
    (list or tuple of Rules)
    """
    d = defaultdict(None, ((r.lhs, r.rhs) for r in derivation))

    def make_tree(lhs):
        return Tree(str(lhs.symbol), (str(child.symbol) if child not in d else make_tree(child) for child in d[lhs]))

    return make_tree(derivation[0].lhs)


def jupyter_draw_nltk_tree(tree):
    """
    Draws the nltk tree inside the jupyter
    notebook instead of in a new window

    Solution taken from
    https://stackoverflow.com/questions/31779707/how-do-you-make-nltk-draw-trees-that-are-inline-in-ipython-jupyter
    ### Not working for yet everyone! (Joost reported a problem) ###
    """
    cf = CanvasFrame()
    tc = TreeWidget(cf.canvas(), tree)
    tc['node_font'] = 'arial 13 bold'
    tc['leaf_font'] = 'arial 14'
    tc['node_color'] = '#005990'
    tc['leaf_color'] = '#3F8F57'
    tc['line_color'] = '#175252'
    cf.add_widget(tc, 10, 10)
    cf.print_to_file('tmp_tree_output.ps')
    cf.destroy()
    os.system('convert tmp_tree_output.ps tmp_tree_output.png')
    display(Image(filename='tmp_tree_output.png'))
    os.system('rm tmp_tree_output.ps tmp_tree_output.png')
