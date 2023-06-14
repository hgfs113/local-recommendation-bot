import glob

def task_gitclean():
    return {
            'actions': ['git clean -Xdf'],
           }


def task_html():
    return {
            'actions': ['sphinx-build doc _build'],
            'file_dep': glob.glob("*.py"),
            'targets': ['_build/index.html'],
           }


def task_test():
    return {
            'actions': ['pytest core/test_ut.py'],
            'file_dep': glob.glob("*.py"),
            'clean': True,
           }

