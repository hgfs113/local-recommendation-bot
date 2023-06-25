import glob
from doit.task import clean_targets
from doit.tools import create_folder


# def task_pot():
#     c1 = 'pybabel extract --input-dirs=. --output-file=messages.pot'
#     return {'actions': [c1],
#             'file_dep': glob.glob('*.py'),
#             'targets': ['messages.pot'], }    


# def task_locale():
#     c1 = 'pybabel update -D geoguesser_bot -d src/locale -i messages.pot'
#     return {'actions': [c1],
#             'file_dep': ['messages.pot'],
#             'targets': ['src/locale/en/LC_MESSAGES/messages.po'], }


# def task_mo():
#     c1 = 'pybabel compile -D geoguesser -l en -i'
#     c2 = ' locale/en/LC_MESSAGES/messages.po -d .'
#     return {'actions': [c1 + c2],
#             'file_dep': ['locale/en/LC_MESSAGES/messages.po'],
#             'targets': ['locale/en/LC_MESSAGES/messages.mo'], }


def task_gitclean():
    return {
            'actions': ['git clean -Xdf'],
           }


def task_flake8():
    return {
            'actions': ['flake8'],
           }


def task_html():
    return {
            'actions': ['sphinx-build doc _build'],
            'file_dep': glob.glob("*.py"),
            'targets': ['_build/index.html'],
            'clean': [clean_targets],
           }


def task_test():
    return {
            'actions': ['pytest core/test_ut.py'],
            'file_dep': glob.glob("*.py"),
            'clean': True,
           }


def task_wheel():
    return {
            'actions': ['pyproject-build -w'],
            'file_dep': glob.glob("*.py"),
            'task_dep': ['mo'], 
           }
