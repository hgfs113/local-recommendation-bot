import glob
from doit.task import clean_targets


def task_pot():
    c1 = 'pybabel extract --input-dirs=. --output-file=messages.pot'
    return {
            'actions': [c1],
            'file_dep': glob.glob('*.py'),
            'targets': ['messages.pot'],
           }


def task_locale():
    c1 = 'pybabel update -d src/locale -i messages.pot'
    return {
            'actions': [c1],
            'file_dep': ['messages.pot'],
            'targets': ['src/locale/en/LC_MESSAGES/messages.po'],
           }


def task_mo():
    c1 = 'pybabel compile -d src/locale --locale en -f'
    return {
            'actions': [c1],
            'file_dep': ['src/locale/en/LC_MESSAGES/messages.po'],
            'targets': ['src/locale/en/LC_MESSAGES/messages.mo'],
           }


def task_gitclean():
    return {
            'actions': ['git clean -Xdf'],
           }


def task_flake8():
    return {
            'actions': ['flake8'],
           }


def task_docstyle():
    return {'actions': ['pydocstyle  --ignore=D10,D203,D211,D212 .']}


def task_html():
    return {
            'actions': ['sphinx-build src/doc _build'],
            'file_dep': glob.glob("*.py"),
            'targets': ['_build/index.html'],
            'clean': [clean_targets],
           }


def task_test():
    return {
            'actions': ['pytest src/core/test_ut.py'],
            'file_dep': glob.glob("*.py"),
            'clean': True,
           }


def task_wheel():
    return {
            'actions': ['pyproject-build -w'],
            'file_dep': glob.glob("*.py"),
            'targets': glob.glob("dist/local_recommendation_bot*.whl"),
            'clean': [clean_targets],
           }
